from fastapi import APIRouter, Depends, HTTPException

from app.auth.auth_barear import JWTBearer

from ..helpers.helpers import get_groups
from .services import Perfil

router = APIRouter()
perfil = Perfil()

@router.get("/")
async def get_perfil(user: dict = Depends(JWTBearer())):
    return perfil.get_perfil(token=user['access_token'])

@router.put("/")
async def put_perfil(atributo: str, valor: str, user: dict = Depends(JWTBearer())):
    return perfil.altera_perfil(token=user['access_token'], attr=atributo, value=valor)
