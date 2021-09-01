from datetime import datetime
from typing import Optional
from uuid import uuid4
from os import environ

from fastapi import APIRouter, Depends, HTTPException, Request

from dotenv import load_dotenv

from app.auth.auth_barear import JWTBearer
from app.models.noticias import Noticia, NoticiaCreate
from app.helpers.helpers import get_groups
from app.helpers.dynamodb import DynamoDB


router = APIRouter()
load_dotenv()
db = DynamoDB(table=environ.get("NOTICIAS_TABLE"), nome_api="noticias", key="noticiaID")


@router.get("/")
async def get_noticias(titulo: Optional[str] = None):
    if titulo is not None:
        db_response = db.busca_por_argumento(argumento="titulo", valor=titulo, grupos=False)
    else:
        db_response = db.busca_todos(grupos=False)
    if db_response.status is True:
        if len(db_response.response) > 0:
            return {
                "mensagem": "noticias encontradas",
                "resultados": db_response.response,
            }
        else:
            raise HTTPException(status_code=404, detail="nenhuma noticia encontrada")
    else:
        raise HTTPException(status_code=500, detail=db_response.error_message)


@router.get("/{id_noticia}")
async def get_noticia(id_noticia: str):
    db_response = db.busca_por_id(id_item=id_noticia, grupos=False)
    if db_response.status is True:
        if db_response.response:
            return {"mensagem": "noticia encontrada", "resultados": db_response.response}
        else:
            raise HTTPException(status_code=404, detail="nenhuma noticia encontrado")
    else:
        raise HTTPException(status_code=500, detail=db_response.error_message)


@router.post("/", status_code=201)
async def post(noticia: NoticiaCreate, user: dict = Depends(JWTBearer())):
    grupos = get_groups(user["cognito:groups"])
    if "diretoria" in grupos:
        noticia.noticiaID = str(uuid4())
        noticia.data_cadastro = str(datetime.now())
        noticia.usuario_id = user["username"]
        db_response = db.cria_item(dados=noticia.json())
        if db_response.status is True:
            return {"mensagem": "noticia cadastrada"}
        else:
            raise HTTPException(status_code=500, detail=db_response.error_message)
    else:
        raise HTTPException(status_code=403, detail="Not authorized")


@router.put("/{id_noticia}")
async def put(id_noticia: str, noticia: Noticia, user: dict = Depends(JWTBearer())):
    grupos = get_groups(user["cognito:groups"])
    if "diretoria" in grupos:
        db_response = db.atualiza_item(id_item=id_noticia, dados=noticia.json(exclude_unset=True))
        if db_response.status is True:
            return {"mensagem": "noticia atualizada"}
        else:
            raise HTTPException(status_code=500, detail=db_response.error_message)
    else:
        raise HTTPException(status_code=403, detail="Not authorized")


@router.delete("/{id_noticia}")
async def delete(id_noticia: str, user: dict = Depends(JWTBearer())):
    grupos = get_groups(user["cognito:groups"])
    if "diretoria" in grupos:
        db_response = db.deleta_item(id_item=id_noticia, grupos=grupos)
        if db_response.status is True:
            return {"mensagem": "noticia apagada"}
        else:
            raise HTTPException(status_code=500, detail=db_response.error_message)
    else:
        raise HTTPException(status_code=403, detail="Not authorized")
