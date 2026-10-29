from contextlib import asynccontextmanager
import json
from pathlib import Path
from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel, Field
from .config import BUILD, NLI_THRESHOLD
from .domain import CaseInput, prepare_case
from . import store
from .services import Workspace
from .sources import public_sources, examples, prepare_bound_case


@asynccontextmanager
async def lifespan(app):
    store.initialize()
    with store.connection() as con:
        con.execute("UPDATE cases SET status='failed',error='Server restarted during analysis; create a new case version to retry' WHERE status IN ('queued','running','cancelling')")
    app.state.workspace = Workspace()
    yield
    app.state.workspace.shutdown()

app = FastAPI(title='TRUSTXAI Clinical Workspace', version='0.1.0', lifespan=lifespan)


class MessageInput(BaseModel):
    text: str = Field(min_length=1, max_length=4000)


def case_or_404(case_id):
    case = store.get_case(case_id)
    if case is None: raise HTTPException(404, 'Conversation not found')
    return case


def full_case(case_id):
    case = case_or_404(case_id)
    case['messages'] = store.messages(case_id)
    return case


def enqueue(case_id, kind='analysis', text=None):
    try: app.state.workspace.submit(case_id, kind, text)
    except ValueError as error: raise HTTPException(409, str(error))


@app.get('/api/health')
def health():
    return {'status':'ok','prototype':True,'clinical_validation':'not established','version':'0.1.0'}


@app.get('/api/runtime')
def runtime():
    return {**app.state.workspace.models.available(), 'checker_threshold':NLI_THRESHOLD,
            'checker_operating_point':'provisional_development','independent_semantic_validation':False}


@app.get('/api/examples')
def case_examples():
    return examples()


@app.get('/api/sources')
def sources():
    return public_sources()


@app.get('/api/cases')
def cases():
    return store.list_cases()


@app.get('/api/cases/{case_id}')
def read_case(case_id: str):
    return full_case(case_id)


@app.post('/api/cases', status_code=201)
def create_case(payload: CaseInput):
    try: prepare_bound_case(payload)
    except ValueError as error: raise HTTPException(422, str(error))
    if payload.parent_id: case_or_404(payload.parent_id)
    case = store.create_case({**payload.model_dump(), 'kind':'diagnostic'})
    store.add_message(case['id'],'user','case',payload.model_dump())
    try: enqueue(case['id'])
    except HTTPException:
        store.discard_case(case['id'])
        raise
    return full_case(case['id'])


@app.post('/api/chats', status_code=201)
def create_chat(payload: MessageInput):
    text = payload.text.strip()
    if not text: raise HTTPException(422,'Enter a question')
    case = store.create_case({'kind':'chat','case_text':text,'title':text[:90]})
    store.add_message(case['id'],'user','text',{'text':text})
    try: enqueue(case['id'],'chat',text)
    except HTTPException:
        store.discard_case(case['id'])
        raise
    return full_case(case['id'])


@app.post('/api/cases/{case_id}/messages')
def add_message(case_id: str, payload: MessageInput):
    case = case_or_404(case_id)
    if case['status'] in ('queued','running','cancelling'):
        raise HTTPException(409,'Wait for the current analysis or stop it before sending another message')
    text = payload.text.strip()
    if not text: raise HTTPException(422,'Enter a question')
    if case['input'].get('kind') == 'diagnostic' and not case['result']:
        raise HTTPException(409,'This case has no completed audit. Create a new case version to retry.')
    message_id = store.add_message(case_id,'user','text',{'text':text})
    try: enqueue(case_id,'chat',text)
    except HTTPException:
        store.discard_message(message_id)
        raise
    return full_case(case_id)


@app.post('/api/cases/{case_id}/cancel')
def cancel(case_id: str):
    case_or_404(case_id)
    return {'requested':app.state.workspace.cancel(case_id)}


@app.delete('/api/cases/{case_id}')
def remove_case(case_id: str):
    case_or_404(case_id)
    app.state.workspace.cancel(case_id)
    store.delete_case(case_id)
    return {'deleted':True}


@app.get('/api/cases/{case_id}/export')
def export(case_id: str):
    data = full_case(case_id)
    return JSONResponse(data, headers={'Content-Disposition':f'attachment; filename="trustxai-{case_id}.json"'})


@app.get('/{path:path}', include_in_schema=False)
def frontend(path: str):
    if path.startswith('api/'):
        raise HTTPException(404,'API route not found')
    candidate = (BUILD/path).resolve()
    if BUILD.resolve() not in candidate.parents and candidate != BUILD.resolve():
        raise HTTPException(404,'File not found')
    if candidate.is_file(): return FileResponse(candidate)
    index = BUILD/'index.html'
    if index.exists(): return FileResponse(index)
    return JSONResponse({'status':'backend ready','frontend':'Run npm install and npm run build in frontend/'})
