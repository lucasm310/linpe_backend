from datetime import datetime
from typing import Optional
from uuid import uuid4
from os import environ

from fastapi import APIRouter, Depends, HTTPException, Request

from dotenv import load_dotenv

from app.auth.auth_barear import JWTBearer
from app.helpers.dynamodb import DynamoDB
from app.helpers.helpers import get_groups
from app.models.eventos import Evento, EventoCreate

load_dotenv()
router = APIRouter()
db = DynamoDB(table=environ.get("EVENTOS_TABLE"), nome_api="eventos", key="eventosID")


@router.get("/")
async def get_eventos(
    nome: Optional[str] = None,
    data_inicio: Optional[str] = None,
    data_fim: Optional[str] = None,
    user: dict = Depends(JWTBearer(auto_error=False)),
):
    if user:
        grupos = get_groups(user["cognito:groups"])
    else:
        grupos = ["geral"]

    if nome is not None:
        db_response = db.busca_por_argumento(argumento="nome", valor=nome, grupos=grupos)
    elif data_inicio is None and data_fim is None:
        db_response = db.busca_todos(grupos=grupos)
    else:
        db_response = db.busca_por_data(inicio=data_inicio, fim=data_fim, grupos=grupos)

    if db_response.status is True:
        if len(db_response.response) > 0:
            return {
                "mensagem": "eventos encontrados",
                "resultados": db_response.response,
            }
        else:
            raise HTTPException(status_code=404, detail="nenhum evento encontrado")
    else:
        raise HTTPException(status_code=500, detail=db_response.error_message)


@router.get("/{id_evento}")
async def get_evento(id_evento: str, user: dict = Depends(JWTBearer(auto_error=False))):
    if user:
        grupos = get_groups(user["cognito:groups"])
    else:
        grupos = ["geral"]
    db_response = db.busca_por_id(id_item=id_evento, grupos=grupos)
    if db_response.status is True:
        if db_response.response:
            return {"mensagem": "evento encontrado", "resultados": db_response.response}
        else:
            raise HTTPException(status_code=404, detail="nenhum evento encontrado")
    else:
        raise HTTPException(status_code=500, detail=db_response.error_message)


@router.post("/", status_code=201)
async def post(evento: EventoCreate, user: dict = Depends(JWTBearer())):
    grupos = get_groups(user["cognito:groups"])
    if "diretoria" in grupos:
        evento.eventosID = str(uuid4())
        evento.data_cadastro = str(datetime.now())
        evento.usuario_id = user["username"]
        db_response = db.cria_item(dados=evento.json())
        if db_response.status is True:
            return {"mensagem": "evento cadastrado", "eventosID": evento.eventosID}
        else:
            raise HTTPException(status_code=500, detail=db_response.error_message)
    else:
        raise HTTPException(status_code=403, detail="Not authorized")


@router.put("/{id_evento}")
async def put(id_evento: str, evento: Evento, user: dict = Depends(JWTBearer())):
    grupos = get_groups(user["cognito:groups"])
    if "diretoria" in grupos:
        db_response = db.atualiza_item(id_item=id_evento, dados=evento.json(exclude_unset=True))
        if db_response.status is True:
            return {"mensagem": "evento atualizado"}
        else:
            raise HTTPException(status_code=500, detail=db_response.error_message)
    else:
        raise HTTPException(status_code=403, detail="Not authorized")


@router.delete("/{id_evento}")
async def delete(id_evento: str, user: dict = Depends(JWTBearer())):
    grupos = get_groups(user["cognito:groups"])
    if "diretoria" in grupos:
        db_response = db.deleta_item(id_item=id_evento, grupos=grupos)
        if db_response.status is True:
            return {"mensagem": "evento deletado"}
        else:
            raise HTTPException(status_code=500, detail=db_response.error_message)
    else:
        raise HTTPException(status_code=403, detail="Not authorized")
