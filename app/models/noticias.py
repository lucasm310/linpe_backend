from uuid import UUID
from typing import Optional
from datetime import datetime
from pydantic import BaseModel, constr


class Noticia(BaseModel):
    noticiaID: Optional[UUID]
    titulo: Optional[str]
    data_cadastro: Optional[datetime]
    conteudo: Optional[str]
    resumo: Optional[str]
    usuario_id: Optional[str]


class NoticiaCreate(Noticia):
    titulo: constr(min_length=2)
    resumo: constr(min_length=2)
