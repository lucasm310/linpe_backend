from fastapi import APIRouter, Depends, HTTPException

from pydantic import BaseModel

from app.auth.auth_barear import JWTBearer

from app.helpers.helpers import get_groups
from app.helpers.cognito import Cognito
from app.models.grupos import Grupo

router = APIRouter()
cognito = Cognito()


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
