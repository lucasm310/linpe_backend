from datetime import datetime
from typing import Optional
from uuid import UUID, uuid4
from os import environ

from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel
from dotenv import load_dotenv

from app.auth.auth_barear import JWTBearer
from .services import EventosDatabase
from ..helpers.helpers import get_groups


class Evento(BaseModel):
    eventosID: Optional[UUID]
    nome: str
    data_inicio: datetime
    data_fim: datetime
    data_cadastro: Optional[datetime]
    descricao: Optional[str]
    local: Optional[str]
    all_day: Optional[bool]
    usuario_id: Optional[str]
    grupo: str


router = APIRouter()
load_dotenv()
db = EventosDatabase(table=environ.get("EVENTOS_TABLE"))


@router.get("/")
async def get_eventos(nome: Optional[str] = None, data_inicio: Optional[str] = None, data_fim: Optional[str] = None, user: dict = Depends(JWTBearer(auto_error=False))):
    if user:
        grupos = get_groups(user['cognito:groups'])
    else:
        grupos = ["geral"]
    if nome is not None:
        return db.busca_por_argumento(argumento="nome", valor=nome, grupos=grupos)
    elif data_inicio is None and data_fim is None:
        return db.busca_todos(grupos=grupos)
    else:
        return db.busca_por_data(inicio=data_inicio, fim=data_fim, grupos=grupos)


@router.get("/{id_evento}")
async def get_evento(id_evento: str, user: dict = Depends(JWTBearer(auto_error=False))):
    if user:
        grupos = get_groups(user['cognito:groups'])
    else:
        grupos = ["geral"]
    return db.busca_por_id(id_item=id_evento, grupos=grupos)


@router.post("/", status_code=201)
async def post(evento: Evento, user: dict = Depends(JWTBearer())):
    grupos = get_groups(user['cognito:groups'])
    if 'diretoria' in grupos:
        evento.eventosID = str(uuid4())
        evento.data_cadastro = str(datetime.now())
        evento.usuario_id = user['username']
        return db.cria_item(dados=evento.json())
    else:
        raise HTTPException(status_code=403, detail="Not authorized")


@router.put("/{id_evento}")
async def put(id_evento: str, request: Request, user: dict = Depends(JWTBearer())):
    grupos = get_groups(user['cognito:groups'])
    if 'diretoria' in grupos:
        valid_keys = ['nome', 'data_inicio', 'data_fim',
                      'descricao', 'local', 'grupo', 'all_day']
        body = await request.json()
        if not any(i in valid_keys for i in body.keys()):
            raise HTTPException(status_code=404, detail="Campos invalidos")
        else:
            return db.atualiza_item(id_item=id_evento, dados=body)
    else:
        raise HTTPException(status_code=403, detail="Not authorized")


@router.delete("/{id_evento}")
async def delete(id_evento: str, user: dict = Depends(JWTBearer())):
    grupos = get_groups(user['cognito:groups'])
    if 'diretoria' in grupos:
        return db.deleta_item(id_item=id_evento, grupos=grupos)
    else:
        raise HTTPException(status_code=403, detail="Not authorized")
