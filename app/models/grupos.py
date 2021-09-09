from pydantic import BaseModel, ValidationError, validator

from .common import GRUPOS


class Grupo(BaseModel):
    grupo: str

    @validator("grupo")
    def grupo_validate(cls, value):
        if value not in GRUPOS:
            raise ValueError("grupo invalido")
        else:
            return value
