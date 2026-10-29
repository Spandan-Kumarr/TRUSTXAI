from copy import deepcopy
from types import SimpleNamespace

import pytest
from fastapi.testclient import TestClient


class IdleWorkspace:
    """Queue protocol fake: requests are recorded, never executed."""
    def __init__(self):
        self.calls = []
        self.reject = False
        self.models = SimpleNamespace(available=lambda: {'ready': True, 'assets': {}, 'phase': 'idle'})

    def submit(self, case_id, kind='analysis', question=None):
        if self.reject:
            raise ValueError('The local inference queue is full')
        self.calls.append((case_id, kind, question))

    def cancel(self, case_id):
        return False

    def shutdown(self):
        pass


@pytest.fixture
def client(isolated_store, monkeypatch):
    import trustxai.main as main
    workspace = IdleWorkspace()
    monkeypatch.setattr(main, 'Workspace', lambda: workspace)
    with TestClient(main.app) as http:
        yield http, workspace, isolated_store


def user_case(case_payload):
    return {**case_payload, 'source_id': None}


def test_api_excludes_gold_fields_and_queues_real_analysis(client, case_payload):
    http, workspace, _ = client
    response = http.post('/api/cases', json={**user_case(case_payload), 'answer_idx': 'D', 'answer': 'Gold only'})
    assert response.status_code == 201
    case = response.json()
    assert case['input']['kind'] == 'diagnostic'
    assert 'answer_idx' not in case['input'] and 'answer' not in case['input']
    assert case['result'] is None
    assert workspace.calls == [(case['id'], 'analysis', None)]
    assert case['messages'][0]['role'] == 'user'
    assert 'answer_idx' not in case['messages'][0]['payload']


def test_invalid_case_does_not_create_history_or_submit_model_job(client, case_payload):
    http, workspace, store = client
    response = http.post('/api/cases', json={**user_case(case_payload), 'options': {'A': 'Only one option'}})
    assert response.status_code == 422
    assert store.list_cases() == [] and workspace.calls == []


def test_edit_is_new_version_and_export_preserves_original_snapshot(client, case_payload):
    http, _, store = client
    original = http.post('/api/cases', json=user_case(case_payload)).json()
    result = {'evidence': {'decision': {'label': 'A'}}, 'input_sha256': 'original-snapshot'}
    store.update_case(original['id'], status='complete', result=result)
    before = http.get(f"/api/cases/{original['id']}").json()
    edited = http.post('/api/cases', json={
        **user_case(case_payload), 'parent_id': original['id'],
        'case_text': case_payload['case_text'].replace('three days', 'four days'),
    }).json()
    assert edited['id'] != original['id'] and edited['input']['parent_id'] == original['id']
    assert edited['result'] is None
    assert http.get(f"/api/cases/{original['id']}").json() == before
    exported = http.get(f"/api/cases/{original['id']}/export")
    assert exported.status_code == 200
    assert exported.json() == before
    assert 'attachment;' in exported.headers['content-disposition']


def test_fabricated_public_source_and_missing_parent_are_rejected(client, case_payload):
    http, workspace, store = client
    source = http.post('/api/cases', json={**case_payload, 'source_id': 'medqa-invented-attribution'})
    parent = http.post('/api/cases', json={**user_case(case_payload), 'parent_id': 'missing-case'})
    assert source.status_code == 422 and parent.status_code == 404
    assert store.list_cases() == [] and workspace.calls == []


def test_queue_rejection_does_not_leave_an_orphan_conversation(client, case_payload):
    http, workspace, store = client
    workspace.reject = True
    response = http.post('/api/cases', json=user_case(case_payload))
    assert response.status_code == 409
    assert store.list_cases() == []


def test_rejected_followup_does_not_append_an_unqueued_user_message(client, case_payload):
    http, workspace, store = client
    created = http.post('/api/cases', json=user_case(case_payload)).json()
    store.update_case(created['id'], status='complete', result={'evidence': {'decision': {'label': 'A'}}})
    before = deepcopy(store.messages(created['id']))
    workspace.reject = True
    response = http.post(f"/api/cases/{created['id']}/messages", json={'text': 'Explain the recorded audit'})
    assert response.status_code == 409
    assert store.messages(created['id']) == before
    assert store.get_case(created['id'])['status'] == 'complete'


def test_active_case_rejects_followup_before_mutating_history(client, case_payload):
    http, _, store = client
    created = http.post('/api/cases', json=user_case(case_payload)).json()
    before = store.messages(created['id'])
    response = http.post(f"/api/cases/{created['id']}/messages", json={'text': 'Another question'})
    assert response.status_code == 409
    assert store.messages(created['id']) == before


def test_chat_only_conversation_and_whitespace_validation(client):
    http, workspace, store = client
    empty = http.post('/api/chats', json={'text': '   '})
    assert empty.status_code == 422 and store.list_cases() == []
    response = http.post('/api/chats', json={'text': ' What does MedQA measure? '})
    assert response.status_code == 201
    case = response.json()
    assert case['input']['kind'] == 'chat'
    assert case['result'] is None
    assert workspace.calls == [(case['id'], 'chat', 'What does MedQA measure?')]


def test_queue_rejection_does_not_leave_an_orphan_chat(client):
    http, workspace, store = client
    workspace.reject = True
    response = http.post('/api/chats', json={'text': 'What does MedQA measure?'})
    assert response.status_code == 409
    assert store.list_cases() == []


def test_deleted_conversation_is_unavailable_for_export_or_messages(client, case_payload):
    http, _, _ = client
    created = http.post('/api/cases', json=user_case(case_payload)).json()
    assert http.delete(f"/api/cases/{created['id']}").status_code == 200
    assert http.get(f"/api/cases/{created['id']}").status_code == 404
    assert http.get(f"/api/cases/{created['id']}/export").status_code == 404
    assert http.post(f"/api/cases/{created['id']}/messages", json={'text': 'Question'}).status_code == 404
