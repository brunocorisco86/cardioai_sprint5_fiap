# encoding: utf-8

import os
import uuid
from pathlib import Path
from typing import Any, Dict, List, Optional

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from ibm_watson import AssistantV2
from ibm_cloud_sdk_core.authenticators import IAMAuthenticator
from ibm_cloud_sdk_core.api_exception import ApiException

load_dotenv()


# Configurações

WATSON_API_KEY = os.getenv("WATSON_API_KEY")
WATSON_URL = os.getenv("WATSON_URL")
WATSON_ASSISTANT_ID = os.getenv("WATSON_ASSISTANT_ID")
WATSON_VERSION = os.getenv("WATSON_VERSION", "2024-08-25")
PORT = int(os.getenv("PORT", 8000))
BASE_DIR = Path(__file__).resolve().parent
FRONTEND_DIR = (BASE_DIR / "frontend").resolve()

if not WATSON_API_KEY or not WATSON_URL or not WATSON_ASSISTANT_ID:
    raise RuntimeError(
        "Defina WATSON_API_KEY, WATSON_URL e WATSON_ASSISTANT_ID no arquivo .env"
    )


# Cliente Watson Assistant

authenticator = IAMAuthenticator(WATSON_API_KEY)
assistant = AssistantV2(version=WATSON_VERSION, authenticator=authenticator)
assistant.set_service_url(WATSON_URL)

# App FastAPI

app = FastAPI(
    title="CardioIA Backend",
    description="API do assistente cardiológico conversacional com IBM Watson Assistant",
    version="1.0.0"
)

# CORS pode ficar assim em desenvolvimento
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Armazenamento em memória | client_id -> watson_session_id

watson_sessions: Dict[str, str] = {}

# Schemas
class SessionRequest(BaseModel):
    client_id: Optional[str] = None


class ChatRequest(BaseModel):
    message: str
    client_id: Optional[str] = None


class ResetRequest(BaseModel):
    client_id: str


# Helpers

def get_or_create_client_id(client_id: Optional[str]) -> str:
    if client_id and client_id.strip():
        return client_id.strip()
    return str(uuid.uuid4())


def extract_text_responses(watson_response: Dict[str, Any]) -> List[str]:
    messages: List[str] = []
    generic = watson_response.get("output", {}).get("generic", [])

    for item in generic:
        if item.get("response_type") == "text" and item.get("text"):
            messages.append(item["text"])

    if not messages:
        fallback_text = watson_response.get("output", {}).get("text", [])
        if isinstance(fallback_text, list):
            messages.extend(fallback_text)

    return messages


def get_or_create_watson_session(client_id: str) -> str:
    if client_id in watson_sessions:
        return watson_sessions[client_id]

    session = assistant.create_session(
        assistant_id=WATSON_ASSISTANT_ID
    ).get_result()

    session_id = session["session_id"]
    watson_sessions[client_id] = session_id
    return session_id


def delete_watson_session(client_id: str) -> bool:
    session_id = watson_sessions.get(client_id)
    if not session_id:
        return False

    try:
        assistant.delete_session(
            assistant_id=WATSON_ASSISTANT_ID,
            session_id=session_id
        ).get_result()
    finally:
        watson_sessions.pop(client_id, None)

    return True



# Rotas do Frontend

@app.get("/")
def serve_index():
    index_file = f'{FRONTEND_DIR}/index.html'
    if not os.path.exists(index_file):
        raise HTTPException(
            status_code=404,
            detail=f"Arquivo index.html não encontrado em: {index_file}"
        )
    return FileResponse(str(index_file))


# Arquivos estáticos do frontend: css, js, imagens...
app.mount("/static", StaticFiles(directory=str(FRONTEND_DIR)), name="static")



# Rotas da API

@app.get("/health")
def health():
    return {
        "status": "ok",
        "watson_configured": True
    }


@app.post("/api/session")
def create_session(payload: SessionRequest):
    client_id = get_or_create_client_id(payload.client_id)

    try:
        session_id = get_or_create_watson_session(client_id)
        return {
            "client_id": client_id,
            "session_created": True,
            "watson_session_id": session_id
        }
    except ApiException as e:
        raise HTTPException(
            status_code=500,
            detail=f"Falha ao criar sessão no Watson Assistant: {str(e)}"
        )


@app.post("/api/chat")
def chat(payload: ChatRequest):
    user_message = payload.message.strip()
    client_id = get_or_create_client_id(payload.client_id)

    if not user_message:
        raise HTTPException(
            status_code=400,
            detail="O campo 'message' é obrigatório."
        )

    try:
        session_id = get_or_create_watson_session(client_id)

        watson_response = assistant.message(
            assistant_id=WATSON_ASSISTANT_ID,
            session_id=session_id,
            input={
                "message_type": "text",
                "text": user_message,
                "options": {
                    "return_context": True
                }
            }
        ).get_result()

        responses = extract_text_responses(watson_response)

        return {
            "client_id": client_id,
            "user_message": user_message,
            "assistant_messages": responses,
            "raw_response": watson_response
        }

    except ApiException as e:
        raise HTTPException(
            status_code=500,
            detail=f"Erro ao enviar mensagem para o Watson Assistant: {str(e)}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Erro interno no backend: {str(e)}"
        )


@app.post("/api/reset")
def reset_chat(payload: ResetRequest):
    try:
        deleted = delete_watson_session(payload.client_id)
        return {
            "client_id": payload.client_id,
            "conversation_reset": deleted
        }
    except ApiException as e:
        raise HTTPException(
            status_code=500,
            detail=f"Falha ao resetar a sessão no Watson Assistant: {str(e)}"
        )


@app.get("/api/docs-info")
def docs_info():
    return {
        "message": "A documentação interativa da API está disponível em /docs"
    }