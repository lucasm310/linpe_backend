from fastapi.responses import JSONResponse

from .logger import get_logger

GRUPOS = {"diretoria": ["diretoria", "ligantes", "geral"], "ligantes": ["ligantes", "geral"], "geral": ["geral"]}


def get_groups(grupos_cognito):
    if "diretoria" in grupos_cognito:
        return GRUPOS["diretoria"]
    elif "ligantes" in grupos_cognito:
        return GRUPOS["ligantes"]
    else:
        return GRUPOS["geral"]
