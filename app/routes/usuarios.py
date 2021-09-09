from datetime import datetime
from os import environ

from dotenv import load_dotenv
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from app.auth.auth_barear import JWTBearer
from app.helpers.helpers import get_groups
from app.helpers.cognito import Cognito
from app.helpers.dynamodb import DynamoDB
from app.models.grupos import Grupo
from app.models.solicitacao_ligantes import Solicitacao

router = APIRouter()
load_dotenv()
cognito = Cognito()
db = DynamoDB(table=environ.get("ACESSO_LIGANTES_TABLE"), nome_api="usuario", key="usuarioID")


@router.get("/")
async def busca_users(user: dict = Depends(JWTBearer())):
    grupos = get_groups(user["cognito:groups"])
    if "diretoria" in grupos:
        usuarios = cognito.busca_todos_usuarios()
        if usuarios.status is True:
            if len(usuarios.response) > 0:
                return {"status": "sucesso", "resultados": usuarios.response}
            else:
                raise HTTPException(status_code=404, detail="Nenhum usuário encontrado")
        else:
            raise HTTPException(status_code=500, detail="Erro em buscar usuários")
    else:
        raise HTTPException(status_code=403, detail="Not authorized")


@router.get("/{username}")
async def get_user(username: str, user: dict = Depends(JWTBearer())):
    grupos = get_groups(user["cognito:groups"])
    if "diretoria" in grupos:
        usuario = cognito.busca_usuario(username=username)
        print(usuario)
        if usuario.status is True:
            return {"status": "sucesso", "usuario": usuario.response}
        else:
            raise HTTPException(status_code=500, detail="Erro em buscar usuário")
    else:
        raise HTTPException(status_code=403, detail="Not authorized")


@router.put("/{username}")
async def put(username: str, atributo: str, valor: str, user: dict = Depends(JWTBearer())):
    grupos = get_groups(user["cognito:groups"])
    if "diretoria" in grupos:
        usuario = cognito.altera_usuario(username=username, attr=atributo, value=valor)
        if usuario.status is True:
            return {"status": "sucesso", "message": "usuario alterado"}
        else:
            raise HTTPException(status_code=500, detail="Erro em alterar usuário")
    else:
        raise HTTPException(status_code=403, detail="Not authorized")


@router.delete("/{username}")
async def delete(username: str, user: dict = Depends(JWTBearer())):
    grupos = get_groups(user["cognito:groups"])
    if "diretoria" in grupos:
        usuario = cognito.deleta_usuario(username=username)
        if usuario.status is True:
            return {"status": "sucesso", "message": "usuário deletado"}
        else:
            raise HTTPException(status_code=500, detail="Erro em deletar usuário")
    else:
        raise HTTPException(status_code=403, detail="Not authorized")


@router.get("/grupos")
async def list_grupos(user: dict = Depends(JWTBearer())):
    grupos = get_groups(user["cognito:groups"])
    if "diretoria" in grupos:
        return {"grupos": usuario.grupos}
    else:
        raise HTTPException(status_code=403, detail="Not authorized")


@router.post("/{username}/grupo")
async def add_grupo(username: str, grupo: Grupo, user: dict = Depends(JWTBearer())):
    grupos = get_groups(user["cognito:groups"])
    grp = grupo.grupo
    if "diretoria" in grupos:
        grp_response = cognito.add_grupo(username=username, grupo=grp)
        if grp_response.status is True:
            return {"status": "sucesso", "message": "usuario alterado"}
        else:
            raise HTTPException(status_code=500, detail="Erro em alterar usuário")
    else:
        raise HTTPException(status_code=403, detail="Not authorized")


@router.delete("/{username}/grupo")
async def remove_grupo(username: str, grupo: str, user: dict = Depends(JWTBearer())):
    grupos = get_groups(user["cognito:groups"])
    if "diretoria" in grupos:
        remove_response = cognito.remove_grupo(username=username, grupo=grupo)
        if remove_response.status is True:
            return {"status": "sucesso", "message": "usuario alterado"}
        else:
            raise HTTPException(status_code=500, detail="Erro em alterar usuário")
    else:
        raise HTTPException(status_code=403, detail="Not authorized")


@router.get("/solicitacoes_ligante/")
async def busca_solicitacoes_ligantes(user: dict = Depends(JWTBearer())):
    grupos = get_groups(user["cognito:groups"])
    if "diretoria" in grupos:
        db_response = db.busca_todos(grupos=False)
        if db_response.status is True:
            usuarios = []
            for usuario in db_response.response:
                cognito_response = cognito.busca_usuario(username=usuario["usuarioID"])
                if cognito_response.status is True:
                    data = cognito_response.response
                    data["data_solicitacao"] = usuario["data_cadastro"]
                    usuarios.append(data)
                else:
                    raise HTTPException(status_code=500, detail="Erro em buscar usuario")
            return {"messagem": "solicitacoes encontradas", "resultados": usuarios}
        else:
            raise HTTPException(status_code=500, detail="Erro em buscar solicitacoes")
    else:
        raise HTTPException(status_code=403, detail="Not authorized")


@router.post("/solicitacoes_ligante/")
async def solicita_ingresso_ligantes(user: dict = Depends(JWTBearer())):
    grupos = get_groups(user["cognito:groups"])
    if len(grupos) == 1 and grupos[0] == "geral":
        solicitacao = Solicitacao(usuarioID=user["username"], data_cadastro=str(datetime.now()))
        db_response = db.cria_item(dados=solicitacao.json())
        if db_response.status is True:
            return {"status": "sucesso", "message": "solicitacao cadastrada"}
        else:
            raise HTTPException(status_code=500, detail="Erro em cadastrar solicitacao")
    else:
        raise HTTPException(status_code=403, detail="Not authorized")


@router.post("/solicitacoes_ligante/{username}/{status}")
async def gerenciar_solicitacao_ligantes(username: str, status: str, user: dict = Depends(JWTBearer())):
    grupos = get_groups(user["cognito:groups"])
    if "diretoria" in grupos:
        grp_response = None
        if status == "aprovar":
            grp_response = cognito.add_grupo(username=username, grupo="ligantes")
            if grp_response.status is False:
                raise HTTPException(status_code=500, detail="Erro em alterar usuário")

        if (grp_response is not None and grp_response.status is True) or status == "negar":
            db_response = db.deleta_item(id_item=username, grupos=grupos)
            if db_response.status is True:
                return {"status": "sucesso", "message": "usuario aprovado para ligante"}
            else:
                raise HTTPException(status_code=500, detail="Erro em alterar usuário")
    else:
        raise HTTPException(status_code=403, detail="Not authorized")
