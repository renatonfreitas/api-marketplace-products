from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from app.api.v1.endpoints import products as products_v1
from app.api.v2.endpoints import addresses as addresses_v2
from app.api.v2.endpoints import categories as categories_v2
from app.api.v2.endpoints import products as products_v2
from app.api.v2.endpoints import suppliers as suppliers_v2
from app.core.exceptions import EmptyListResponse
from app.core.version_info import VersionInfo, get_api_info


app = FastAPI(
    title="Products API",
    description="API para gerenciamento de produtos com categories, suppliers e addresses",
    version="2.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# @app.exception_handler(EmptyListResponse)
async def empty_list_handler(request, exc):
    return JSONResponse(
        status_code=204,
        content=None
    )

# V1 - Legacy (deprecated)
app.include_router(
    products_v1.router, 
    prefix="/api/v1",
    # deprecated=True
)

# V2 - Current
app.include_router(addresses_v2.router, prefix="/api/v2")
app.include_router(categories_v2.router, prefix="/api/v2")
app.include_router(suppliers_v2.router, prefix="/api/v2")
app.include_router(products_v2.router, prefix="/api/v2")

@app.get("/", tags=["health"])
async def root():
    return {
        "message": "API de produtos rodando!", 
        "version": "2.0.0", 
        "docs": "/docs"
    }

@app.get("/api/info", tags=["health"])
async def api_info():
    """
    Retorna informações completas da API
    
    Inclui:
    - Versão atual
    - Versões disponíveis (V1 deprecated, V2 stable)
    - Features de cada versão
    - Breaking changes
    - Endpoints disponíveis
    - Documentação
    """
    try:
        return get_api_info()
    except Exception as e:
        return {
            "error": "Erro ao obter informações",
            "version": VersionInfo.CURRENT_VERSION
        }