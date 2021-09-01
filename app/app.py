import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from mangum import Mangum

from app.middleware.exceptions import exceptions_handler

from app.routes.perfil import router as perfil
from app.routes.eventos import router as eventos
from app.routes.noticias import router as noticias
from app.routes.usuarios import router as usuarios
from app.routes.documentos import router as documentos

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.middleware("http")(exceptions_handler)
app.include_router(perfil, prefix="/perfil", tags=["perfil"])
app.include_router(eventos, prefix="/eventos", tags=["eventos"])
app.include_router(noticias, prefix="/noticias", tags=["noticias"])
app.include_router(usuarios, prefix="/usuarios", tags=["usuarios"])
app.include_router(documentos, prefix="/documentos", tags=["documentos"])

handler = Mangum(app)
