from datetime import datetime
from typing import Optional
from uuid import UUID, uuid4
from os import environ

from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel
from dotenv import load_dotenv

from app.auth.auth_barear import JWTBearer
from app.models.documentos import Documento, DocumentoCreate
from app.helpers.dynamodb import DynamoDB
from app.helpers.helpers import get_groups
from app.helpers.s3 import S3

router = APIRouter()
load_dotenv()
db = DynamoDB(table=environ.get("DOCUMENTOS_TABLE"), nome_api="documentos", key="documentoID")


@router.get("/")
async def get_docs(name: Optional[str] = None, tipo: Optional[str] = None, user: dict = Depends(JWTBearer(auto_error=False))):
    if user:
        grupos = get_groups(user["cognito:groups"])
    else:
        grupos = ["geral"]

    if tipo is not None:
        db_response = db.busca_por_argumento(argumento="tipo", valor=tipo, grupos=grupos)
    elif name is not None and user:
        db_response = db.busca_por_argumento(argumento="nome", valor=name, grupos=grupos)
    elif user:
        db_response = db.busca_todos(grupos=grupos)
    else:
        raise HTTPException(status_code=403, detail="Not authorized")

    if db_response.status is True:
        if len(db_response.response) > 0:
            return {
                "mensagem": "documentos encontrados",
                "resultados": db_response.response,
            }
        else:
            raise HTTPException(status_code=404, detail="nenhum documento encontrado")
    else:
        raise HTTPException(status_code=500, detail=db_response.error_message)


@router.get("/{id_doc}")
async def get_doc(id_doc: str, user: dict = Depends(JWTBearer(auto_error=False)), s3: S3 = Depends(S3)):
    if user:
        tipo = "all"
        grupos = get_groups(user["cognito:groups"])
    else:
        tipo = "publico"
        grupos = ["geral"]
    db_response = db.busca_por_id(id_item=id_doc, grupos=grupos)
    if db_response.status is True:
        if len(db_response.response) > 0:
            for doc in db_response.response:
                if doc["tipo"] == tipo or tipo == "all":
                    if "nome_file" in doc.keys() and doc["nome_file"] != "":
                        s3_response = s3.get_url(arquivo=doc["nome_file"])
                        if s3_response.status is True:
                            doc["url"] = s3_response.response
            return {
                "mensagem": "documentos encontrados",
                "resultados": db_response.response,
            }
        else:
            raise HTTPException(status_code=404, detail="nenhum documento encontrado")
    else:
        raise HTTPException(status_code=500, detail=db_response.error_message)


@router.post("/", status_code=201)
async def post(documento: DocumentoCreate, user: dict = Depends(JWTBearer()), s3: S3 = Depends(S3)):
    grupos = get_groups(user["cognito:groups"])
    if "diretoria" in grupos:
        documento.documentoID = str(uuid4())
        documento.data_cadastro = str(datetime.now())
        documento.usuario_id = user["username"]
        nome_file = f"{uuid4()}.{documento.nome_file.split('.')[-1]}"
        documento.nome_file = nome_file
        db_response = db.cria_item(dados=documento.json())
        if db_response.status is True:
            s3_response = s3.make_url(nome_file)
            if s3_response.status is True:
                return {"mensagem": "documento criado", "url_upload": s3_response.response["url"], "fields_upload": s3_response.response["fields"]}
            else:
                raise HTTPException(status_code=500, detail="erro gerar url para upload")
        else:
            raise HTTPException(status_code=500, detail="erro ao criar documento")
    else:
        raise HTTPException(status_code=403, detail="Not authorized")


@router.put("/{id_doc}")
async def put(id_doc: str, documento: Documento, user: dict = Depends(JWTBearer())):
    grupos = get_groups(user["cognito:groups"])
    if "diretoria" in grupos:
        db_response = db.atualiza_item(id_item=id_doc, dados=documento.json(exclude_unset=True))
        if db_response.status is True:
            return {"mensagem": "documento atualizado"}
        else:
            raise HTTPException(status_code=500, detail=db_response.error_message)
    else:
        raise HTTPException(status_code=403, detail="Not authorized")


@router.delete("/{id_doc}")
async def delete(id_doc: str, user: dict = Depends(JWTBearer())):
    grupos = get_groups(user["cognito:groups"])
    if "diretoria" in grupos:
        db_response = db.deleta_item(id_item=id_doc, grupos=grupos)
        if db_response.status is True:
            return {"status": "sucesso", "message": "documento deletado"}
        else:
            raise HTTPException(status_code=404, detail="Campos invalidos")
    else:
        raise HTTPException(status_code=403, detail="Not authorized")
