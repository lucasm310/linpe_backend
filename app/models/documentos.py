from datetime import datetime
from typing import Optional
from uuid import UUID
from pydantic import BaseModel, constr, ValidationError, validator

from .common import GRUPOS


class Documento(BaseModel):
    documentoID: Optional[UUID]
    nome: Optional[str]
    data_cadastro: Optional[datetime]
    nome_file: Optional[str]
    usuario_id: Optional[str]
    tipo: Optional[str]
    grupo: Optional[str]
    categoria: Optional[str]

    @validator("grupo")
    def grupo_validate(cls, value):
        if value not in GRUPOS:
            raise ValueError("grupo invalido")
        else:
            return value
    
    @validator("tipo")
    def tipo_validate(cls, value):
        if value not in ["privado","publico"]:
            raise ValueError("tipo invalido")
        else:
            return value


class DocumentoCreate(Documento):
    nome: constr(min_length=2)
    nome_file: constr(min_length=2)
    tipo: constr(min_length=2)
    grupo: constr(min_length=2)
    categoria: constr(min_length=2)
