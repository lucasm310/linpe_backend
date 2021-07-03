from datetime import datetime
from typing import Optional
from uuid import UUID, uuid4
from os import environ

from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel
from dotenv import load_dotenv

from app.auth.auth_barear import JWTBearer
from .services import DocumentosDatabase
from ..helpers.helpers import get_groups


class Documento(BaseModel):
    documentoID: Optional[UUID]
    nome: str
    data_cadastro: Optional[datetime]
    nome_file: str
    usuario_id: Optional[str]
    tipo: str
    grupo: str


router = APIRouter()
load_dotenv()
db = DocumentosDatabase(table=environ.get("DOCUMENTOS_TABLE"))


@router.get("/")
async def get_docs(name: Optional[str] = None, tipo: Optional[str] = None, user: dict = Depends(JWTBearer(auto_error=False))):
    if user:
        grupos = get_groups(user['cognito:groups'])
    else:
        grupos = ["geral"]
    if tipo is not None:
        return db.busca_por_argumento(argumento="tipo", valor=tipo, grupos=grupos)
    elif name is not None and user:
        return db.busca_por_argumento(argumento="nome", valor=name, grupos=grupos)
    elif user:
        return db.busca_todos(grupos=grupos)
    else:
        raise HTTPException(status_code=403, detail="Not authorized")


@router.get("/{id_doc}")
async def get_doc(id_doc: str, user: dict = Depends(JWTBearer(auto_error=False))):
    if user:
        tipo = "all"
        grupos = get_groups(user['cognito:groups'])
    else:
        tipo = "publico"
        grupos = ["geral"]
    return db.busca_documento_id(id_documento=id_doc, grupos=grupos, tipo=tipo)


@router.post("/", status_code=201)
async def post(documento: Documento, user: dict = Depends(JWTBearer())):
    grupos = get_groups(user['cognito:groups'])
    if 'diretoria' in grupos:
        documento.documentoID = str(uuid4())
        documento.data_cadastro = str(datetime.now())
        documento.usuario_id = user['username']
        return db.cria_item(dados=documento.json())
    else:
        raise HTTPException(status_code=403, detail="Not authorized")


@router.put("/{id_doc}")
async def put(id_doc: str, request: Request, user: dict = Depends(JWTBearer())):
    grupos = get_groups(user['cognito:groups'])
    if 'diretoria' in grupos:
        valid_keys = ['nome', 'grupo']
        body = await request.json()
        if not any(i in valid_keys for i in body.keys()):
            raise HTTPException(status_code=404, detail="Campos invalidos")
        else:
            return db.atualiza_item(id_item=id_doc, dados=body, grupos=grupos)
    else:
        raise HTTPException(status_code=403, detail="Not authorized")


@router.delete("/{id_doc}")
async def delete(id_doc: str, user: dict = Depends(JWTBearer())):
    grupos = get_groups(user['cognito:groups'])
    if 'diretoria' in grupos:
        return db.deleta_item(id_item=id_doc, grupos=grupos)
    else:
        raise HTTPException(status_code=403, detail="Not authorized")
