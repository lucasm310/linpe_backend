from datetime import datetime
from typing import Optional
from uuid import UUID
from pydantic import BaseModel, constr, ValidationError, validator

from .common import GRUPOS


class Evento(BaseModel):
    eventosID: Optional[UUID]
    nome: Optional[str]
    data_inicio: Optional[datetime]
    data_fim: Optional[datetime]
    data_cadastro: Optional[datetime]
    descricao: Optional[str]
    local: Optional[str]
    all_day: Optional[bool]
    usuario_id: Optional[str]
    grupo: Optional[str]

    @validator("grupo")
    def grupo_validate(cls, value):
        if value not in GRUPOS:
            raise ValueError("grupo invalido")
        else:
            return value


class EventoCreate(Evento):
    nome: constr(min_length=2)
    data_inicio: datetime
    data_fim: datetime
    grupo: constr(min_length=2)
