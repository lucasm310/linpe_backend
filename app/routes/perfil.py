from fastapi import APIRouter, Depends, HTTPException

from app.auth.auth_barear import JWTBearer

from app.helpers.helpers import get_groups
from app.helpers.cognito import Cognito

router = APIRouter()
cognito = Cognito()


@router.get("/")
async def get_perfil(user: dict = Depends(JWTBearer())):
    perfil = cognito.get_perfil(token=user["access_token"])
    if perfil.status is True:
        return {"status": "sucesso", "usuario": perfil.response}
    else:
        raise HTTPException(status_code=500, detail={"status": "falha", "mensagem": "erro buscar perfil"})


@router.put("/")
async def put_perfil(atributo: str, valor: str, user: dict = Depends(JWTBearer())):
    perfil_update = cognito.altera_perfil(token=user["access_token"], attr=atributo, value=valor)
    if perfil_update.status is True:
        return {"status": "sucesso", "message": "usuario alterado"}
    else:
        raise HTTPException(status_code=500, detail={"status": "falha", "mensagem": "erro ao alterar perfil"})
