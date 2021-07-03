from fastapi import APIRouter, Depends, HTTPException

from pydantic import BaseModel

from app.auth.auth_barear import JWTBearer

from ..helpers.helpers import get_groups
from .services import Usuarios

router = APIRouter()
usuario = Usuarios()

class Grupo(BaseModel):
    grupo: str


@router.get("/")
async def busca_users(user: dict = Depends(JWTBearer())):
    grupos = get_groups(user['cognito:groups'])
    if 'diretoria' in grupos:
        return usuario.busca_todos()
    else:
        raise HTTPException(status_code=403, detail="Not authorized")

@router.get("/{username}")
async def get_user(username: str, user: dict = Depends(JWTBearer())):
    grupos = get_groups(user['cognito:groups'])
    if 'diretoria' in grupos:
        return usuario.busca_user(username=username)
    else:
        raise HTTPException(status_code=403, detail="Not authorized")

@router.put("/{username}")
async def put(username: str, atributo: str, valor: str, user: dict = Depends(JWTBearer())):
    grupos = get_groups(user['cognito:groups'])
    if 'diretoria' in grupos:
        return usuario.altera(username=username, attr=atributo, value=valor)
    else:
        raise HTTPException(status_code=403, detail="Not authorized")

@router.delete("/{username}")
async def delete(username: str, user: dict = Depends(JWTBearer())):
    grupos = get_groups(user['cognito:groups'])
    if 'diretoria' in grupos:
        return usuario.deleta(username=username)
    else:
        raise HTTPException(status_code=403, detail="Not authorized")

@router.get("/grupos")
async def list_grupos(user: dict = Depends(JWTBearer())):
    grupos = get_groups(user['cognito:groups'])
    if 'diretoria' in grupos:
        return {'grupos': usuario.grupos}
    else:
        raise HTTPException(status_code=403, detail="Not authorized")

@router.post("/{username}/grupo")
async def add_grupo(username: str, grupo: Grupo, user: dict = Depends(JWTBearer())):
    grupos = get_groups(user['cognito:groups'])
    grp = grupo.grupo
    if 'diretoria' in grupos:
        return usuario.add_grupo(username=username, grupo=grp)
    else:
        raise HTTPException(status_code=403, detail="Not authorized")

@router.delete("/{username}/grupo")
async def remove_grupo(username: str, grupo: str, user: dict = Depends(JWTBearer())):
    grupos = get_groups(user['cognito:groups'])
    if 'diretoria' in grupos:
        return usuario.remove_grupo(username=username, grupo=grupo)
    else:
        raise HTTPException(status_code=403, detail="Not authorized")