from fastapi import FastAPI
from app.core.config import settings
from app.core.indexer import get_index
from app.routers.api import router

app = FastAPI(
    title=settings.APP_NAME,
    description="API avançada para indexação e busca de documentos",
    version="2.0.0"
)

app.include_router(router)


@app.on_event("startup")
async def startup_event():
    get_index()
    print(f"🚀 {settings.APP_NAME} iniciada!")
    print(f"📁 Indexando a partir de: {settings.DATA_DIRECTORY}")
    print(f"🔍 Índice Whoosh em: {settings.INDEX_DIR}")
    print(f"📄 Paginação padrão: {settings.DEFAULT_PAGE_SIZE} itens")


@app.get("/", tags=["Status"])
async def root():
    return {
        "message": f"Bem-vindo ao {settings.APP_NAME}",
        "version": "2.0.0",
        "endpoints": {
            "search": "/search",
            "index": "/index",
            "stats": "/index/stats"
        }
    }
