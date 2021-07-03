from datetime import datetime
from typing import Optional
from uuid import UUID, uuid4
from os import environ

from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel
from dotenv import load_dotenv

from app.auth.auth_barear import JWTBearer

from .services import NoticiasDatabase
from ..helpers.helpers import get_groups


class Noticia(BaseModel):
    noticiaID: Optional[UUID]
    titulo: str
    data_cadastro: Optional[datetime]
    conteudo: Optional[str]
    resumo: str
    usuario_id: Optional[str]

router = APIRouter()
load_dotenv()
db = NoticiasDatabase(table=environ.get("NOTICIAS_TABLE"))

@router.get("/")
async def get_noticias(titulo: Optional[str] = None):
    if titulo is not None:
        return db.busca_por_argumento(argumento="titulo", valor=titulo, grupos=False)
    else:
        return db.busca_todos(grupos=False)

@router.get("/{id_noticia}")
async def get_noticia(id_noticia: str):
    return db.busca_por_id(id_item=id_noticia, grupos=False)

@router.post("/", status_code=201)
async def post(noticia: Noticia, user: dict = Depends(JWTBearer())):
    grupos = get_groups(user['cognito:groups'])
    if 'diretoria' in grupos:
        noticia.noticiaID = str(uuid4())
        noticia.data_cadastro = str(datetime.now())
        noticia.usuario_id = user['username']
        return db.cria_item(dados=noticia.json())
    else:
        raise HTTPException(status_code=403, detail="Not authorized")

@router.put("/{id_noticia}")
async def put(id_noticia: str, request: Request, user: dict = Depends(JWTBearer())):
    grupos = get_groups(user['cognito:groups'])
    if 'diretoria' in grupos:
        valid_keys = ['titulo', 'conteudo','resumo']
        body = await request.json()
        if not any(i in valid_keys for i in body.keys()):
            raise HTTPException(status_code=404, detail="Campos invalidos")
        else:
            return db.atualiza_item(id_item=id_noticia, dados=body)
    else:
        raise HTTPException(status_code=403, detail="Not authorized")

@router.delete("/{id_noticia}")
async def delete(id_noticia: str, user: dict = Depends(JWTBearer())):
    grupos = get_groups(user['cognito:groups'])
    if 'diretoria' in grupos:
        return db.deleta_item(id_item=id_noticia, grupos=grupos)
    else:
        raise HTTPException(status_code=403, detail="Not authorized")