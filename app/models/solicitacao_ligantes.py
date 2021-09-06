from datetime import datetime
from pydantic import BaseModel


class Solicitacao(BaseModel):
    usuarioID: str
    data_cadastro: datetime