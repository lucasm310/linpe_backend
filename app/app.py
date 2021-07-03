import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette.exceptions import HTTPException as StarletteHTTPException
from fastapi.responses import JSONResponse
from mangum import Mangum

from app.helpers.logger import get_logger

from app.documentos.api import router as documentos
from app.upload.api import router as upload
from app.noticias.api import router as noticias
from app.eventos.api import router as eventos
from app.usuarios.api import router as usuarios
from app.perfil.api import router as perfil

logger = get_logger()
app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request, exc):
    logger.error(f'status_code={exc.status_code}, message={exc.detail}')
    return JSONResponse(
        status_code=exc.status_code,
        content=exc.detail,
    )

app.include_router(documentos, prefix='/documentos', tags=['documentos'])
app.include_router(upload, prefix='/upload', tags=['upload'])
app.include_router(noticias, prefix='/noticias', tags=['noticias'])
app.include_router(eventos, prefix='/eventos', tags=['eventos'])
app.include_router(usuarios, prefix='/usuarios', tags=['usuarios'])
app.include_router(perfil, prefix='/perfil', tags=['perfil'])

handler = Mangum(app)
