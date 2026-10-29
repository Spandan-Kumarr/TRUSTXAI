from copy import deepcopy
import threading
from types import SimpleNamespace

from conftest import ScriptedModels


def workspace_with_models(monkeypatch, models):
    import trustxai.services as services
    monkeypatch.setattr(services, 'LocalModels', lambda: models)
    return services.Workspace()


def test_missing_weights_is_a_visible_failure_without_fabricated_result(isolated_store, case_payload, monkeypatch):
    store = isolated_store
    models = ScriptedModels()
    models.available = lambda: {'ready': False}
    workspace = workspace_with_models(monkeypatch, models)
    case = store.create_case({**case_payload, 'kind': 'diagnostic'})
    event = threading.Event()
    workspace.events[case['id']] = event
    try:
        workspace._work(case['id'], 'analysis', None, event)
        result = store.get_case(case['id'])
        assert result['status'] == 'failed'
        assert result['result'] is None
        assert 'assets are unavailable' in result['error']
        assert models.classifications == [] and models.generations == []
        assert store.messages(case['id']) == []
        assert case['id'] not in workspace.events
    finally:
        workspace.shutdown()


def test_stop_after_inference_prevents_result_publication(isolated_store, case_payload, monkeypatch):
    store = isolated_store
    models = ScriptedModels()
    models.available = lambda: {'ready': True}
    workspace = workspace_with_models(monkeypatch, models)
    case = store.create_case({**case_payload, 'kind': 'diagnostic'})
    event = threading.Event()
    workspace.events[case['id']] = event
    def completes_after_stop(*args):
        event.set()
        return {'views': {'novice': {'C1': 'This must not be released'}}}
    workspace.pipeline = SimpleNamespace(analyze=completes_after_stop)
    try:
        workspace._work(case['id'], 'analysis', None, event)
        result = store.get_case(case['id'])
        assert result['status'] == 'cancelled' and result['result'] is None
        assert [message['kind'] for message in store.messages(case['id'])] == ['notice']
        assert case['id'] not in workspace.events
    finally:
        workspace.shutdown()


def test_chat_completion_appends_history_without_replacing_case_audit(isolated_store, case_payload, monkeypatch):
    store = isolated_store
    models = ScriptedModels()
    models.available = lambda: {'ready': True}
    workspace = workspace_with_models(monkeypatch, models)
    case = store.create_case({**case_payload, 'kind': 'diagnostic'})
    frozen = {'evidence': {'decision': {'label': 'A'}}, 'input_sha256': 'immutable-audit'}
    store.update_case(case['id'], status='complete', result=frozen)
    store.add_message(case['id'], 'user', 'text', {'text': 'What was recorded?'})
    event = threading.Event()
    workspace.events[case['id']] = event
    answer = {'text': 'The model recorded option A [1].', 'citations': [{'id': 'case-C1'}],
              'grounding_status': 'source_checked'}
    received = []
    def reply(question, history, snapshot, progress, cancelled):
        received.append((question, deepcopy(history), deepcopy(snapshot)))
        return answer
    workspace.pipeline = SimpleNamespace(chat=reply)
    try:
        workspace._work(case['id'], 'chat', 'What was recorded?', event)
        result = store.get_case(case['id'])
        assert result['status'] == 'complete' and result['result'] == frozen
        assert received[0][0] == 'What was recorded?'
        assert received[0][2]['result'] == frozen
        history = store.messages(case['id'])
        assert [message['role'] for message in history] == ['user', 'assistant']
        assert history[-1]['payload'] == answer
    finally:
        workspace.shutdown()
