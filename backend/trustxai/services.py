from concurrent.futures import ThreadPoolExecutor
import json
import threading
from . import store
from .domain import CaseInput
from .sources import prepare_bound_case
from .models import LocalModels
from .pipeline import Pipeline, Cancelled


class Workspace:
    def __init__(self):
        self.models = LocalModels()
        self.pipeline = Pipeline(self.models)
        self.executor = ThreadPoolExecutor(max_workers=1, thread_name_prefix='trustxai-inference')
        self.events = {}
        self.lock = threading.Lock()

    def submit(self, case_id, kind='analysis', question=None):
        with self.lock:
            if case_id in self.events:
                raise ValueError('This conversation already has a model job in progress')
            if len(self.events) >= 4:
                raise ValueError('The local inference queue is full; wait for a current case to finish')
            event = threading.Event()
            self.events[case_id] = event
        store.update_case(case_id, status='queued', progress={'stage':'queued','detail':'Waiting for the local inference worker','percent':0})
        self.executor.submit(self._work, case_id, kind, question, event)

    def cancel(self, case_id):
        with self.lock:
            event = self.events.get(case_id)
        if event:
            event.set()
            store.update_case(case_id, status='cancelling', progress={'stage':'cancelling','detail':'Stopping after the current bounded inference call','percent':0})
        return bool(event)

    def _work(self, case_id, kind, question, event):
        def cancelled():
            return event.is_set() or store.get_case(case_id) is None
        def progress(value):
            if cancelled(): raise Cancelled()
            store.update_case(case_id, status='running', progress=value)
        try:
            if cancelled(): raise Cancelled()
            case = store.get_case(case_id)
            if not self.models.available()['ready']:
                raise RuntimeError('Pinned local model assets are unavailable. See README runtime setup; no synthetic response was substituted.')
            if kind == 'analysis':
                payload = CaseInput.model_validate({key:value for key,value in case['input'].items() if key != 'kind'})
                prepared = prepare_bound_case(payload)
                result = self.pipeline.analyze(prepared, progress, cancelled)
                if cancelled(): raise Cancelled()
                store.add_message(case_id, 'assistant', 'analysis', {'text':'The recorded suggestion and evidence audit are ready.'})
                store.update_case(case_id, status='complete', result=result,
                                  progress={'stage':'complete','detail':'Case audit ready','percent':100})
            else:
                result = self.pipeline.chat(question, store.messages(case_id), case, progress, cancelled)
                if cancelled(): raise Cancelled()
                store.add_message(case_id, 'assistant', 'answer', result)
                store.update_case(case_id, status='complete', progress={'stage':'complete','detail':'Source-grounded reply ready','percent':100})
        except Cancelled:
            case = store.get_case(case_id)
            if case:
                store.add_message(case_id,'assistant','notice',{'text':'Stopped before another checked response was released.'})
                store.update_case(case_id, status='complete' if case['result'] else 'cancelled',
                                  progress={'stage':'cancelled','detail':'Stopped','percent':0})
        except Exception as error:
            # A real failure stays a failure; the app does not invent a diagnosis.
            store.update_case(case_id, status='failed', error=str(error),
                              progress={'stage':'failed','detail':'Analysis could not complete','percent':0})
        finally:
            self.models.phase = 'idle'
            with self.lock:
                self.events.pop(case_id, None)

    def shutdown(self):
        with self.lock:
            for event in self.events.values(): event.set()
        self.executor.shutdown(wait=False, cancel_futures=True)
