from fastapi.responses import JSONResponse

from .logger import get_logger

GRUPOS = {
    "diretoria": ["diretoria", "ligantes", "geral"],
    "ligantes": ["ligantes", "geral"],
    "geral": ["geral"]
}

def get_groups(grupos_cognito):
    if "diretoria" in grupos_cognito:
        return GRUPOS["diretoria"]
    elif "ligantes" in grupos_cognito:
        return GRUPOS["ligantes"]
    else:
        return GRUPOS["geral"]

class CustomException(Exception):
    def __init__(self, status_code, message):
        self.status_code = status_code
        self.message = message
        self.logger = get_logger()
    def handler(self):
        self.logger.error(f'message="{self.message}"')
        return JSONResponse(
            status_code=self.status_code,
            content={"status":"falha", "message":self.message},
        )