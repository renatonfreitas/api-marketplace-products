"""
Informações de versão e metadados da API
"""

from enum import Enum


class APIVersion(str, Enum):
    """Versões disponíveis da API"""
    V1 = "v1"
    V2 = "v2"

class VersionInfo:
    """Informações sobre as versões da API"""

    # Versão atual
    CURRENT_VERSION = "2.0.0"
    LATEST_VERSION = "2.0.0"

    # Versões
    V1_VERSION = "1.0.0"
    V2_VERSION = "2.0.0"

    # Status
    V1_STATUS = "deprecated"  # Descontinuada
    V2_STATUS = "stable"      # Estável

    # Datas
    V1_RELEASE_DATE = "2024-01-01"
    V2_RELEASE_DATE = "2024-06-01"
    V1_DEPRECATION_DATE = "2025-12-31"
    
    # Descrições
    V1_DESCRIPTION = "Versão original - Produtos apenas"
    V2_DESCRIPTION = "Versão melhorada - Produtos, Categorias, Suppliers e Addresses"
    
    # Endpoints
    V1_ENDPOINTS = [
        "GET /api/v1/products",
        "POST /api/v1/products",
        "GET /api/v1/products/{sku}",
        "PUT /api/v1/products/{sku}",
        "DELETE /api/v1/products/{sku}"
    ]
    
    V2_ENDPOINTS = [
        # Products
        "GET /api/v2/products",
        "POST /api/v2/products",
        "GET /api/v2/products/{sku}",
        "PUT /api/v2/products/{sku}",
        "DELETE /api/v2/products/{sku}",
        
        # Categories
        "GET /api/v2/categories",
        "POST /api/v2/categories",
        "GET /api/v2/categories/{category_id}",
        "PUT /api/v2/categories/{category_id}",
        "DELETE /api/v2/categories/{category_id}",
        
        # Suppliers
        "GET /api/v2/suppliers",
        "POST /api/v2/suppliers",
        "GET /api/v2/suppliers/{supplier_id}",
        "PUT /api/v2/suppliers/{supplier_id}",
        "DELETE /api/v2/suppliers/{supplier_id}",
        
        # Addresses
        "GET /api/v2/addresses",
        "POST /api/v2/addresses",
        "GET /api/v2/addresses/{address_id}",
        "PUT /api/v2/addresses/{address_id}",
        "DELETE /api/v2/addresses/{address_id}"
    ]

    # Recursos
    V1_RESOURCES = [
        "Products"
    ]
    
    V2_RESOURCES = [
        "Products",
        "Categories",
        "Suppliers",
        "Addresses"
    ]

    # Features
    V1_FEATURES = [
        "CRUD completo de produtos",
        "Filtros básicos",
        "Paginação"
    ]
    
    V2_FEATURES = [
        "CRUD completo de produtos com relacionamentos M:N",
        "CRUD de categorias",
        "CRUD de suppliers com múltiplos endereços",
        "CRUD de endereços normalizado",
        "Filtros avançados",
        "Paginação melhorada",
        "Soft delete em todos os recursos",
        "Validações completas"
    ]

    # Breaking Changes
    BREAKING_CHANGES_V2 = [
        "quantity_per_unit renomeado para unit_quantity",
        "is_active adicionado em todos os recursos",
        "Addresses é tabela separada (normalizada)"
    ]

    # Deprecation Info
    DEPRECATION_INFO = {
        "V1": {
            "status": "deprecated",
            "message": "A versão V1 está descontinuada",
            "deprecation_date": "2024-01-01",
            "sunset_date": "2025-12-31",
            "migration_guide": "Use /api/v2 em vez de /api/v1"
        }
    }

class APIMetadata:
    """Metadados gerais da API"""

    TITLE = "Products API"
    DESCRIPTION = "API RESTful para gerenciamento de produtos, categorias, suppliers e endereços"
    VERSION = VersionInfo.CURRENT_VERSION
    
    CONTACT = {
        "name": "Support Team",
        "email": "support@example.com",
        "url": "https://example.com/support"
    }
    
    LICENSE = {
        "name": "MIT",
        "url": "https://opensource.org/licenses/MIT"
    }
    
    SERVERS = [
        {
            "url": "http://localhost:8000",
            "description": "Development Server"
        },
        {
            "url": "https://api.example.com",
            "description": "Production Server"
        }
    ]

class ResponseStatus:
    """Status HTTP Padrão"""
    
    # Success
    OK_200 = {"code": 200, "message": "Requisição bem-sucedida"}
    CREATED_201 = {"code": 201, "message": "Recurso criado com sucesso"}
    NO_CONTENT_204 = {"code": 204, "message": "Sucesso, sem conteúdo"}
    
    # Client Errors
    BAD_REQUEST_400 = {"code": 400, "message": "Requisição inválida"}
    NOT_FOUND_404 = {"code": 404, "message": "Recurso não encontrado"}
    CONFLICT_409 = {"code": 409, "message": "Conflito - Recurso já existe"}
    
    # Server Errors
    INTERNAL_ERROR_500 = {"code": 500, "message": "Erro interno do servidor"}

def get_version_info(version: APIVersion = APIVersion.V2) -> dict:
    """Retorna informações sobre uma versão específica"""
    
    if version == APIVersion.V1:
        return {
            "version": VersionInfo.V1_VERSION,
            "status": VersionInfo.V1_STATUS,
            "release_date": VersionInfo.V1_RELEASE_DATE,
            "deprecation_date": VersionInfo.V1_DEPRECATION_DATE,
            "description": VersionInfo.V1_DESCRIPTION,
            "resources": VersionInfo.V1_RESOURCES,
            "endpoints": VersionInfo.V1_ENDPOINTS,
            "features": VersionInfo.V1_FEATURES,
            "message": "Esta versão está descontinuada. Por favor, migre para V2."
        }
    
    elif version == APIVersion.V2:
        return {
            "version": VersionInfo.V2_VERSION,
            "status": VersionInfo.V2_STATUS,
            "release_date": VersionInfo.V2_RELEASE_DATE,
            "description": VersionInfo.V2_DESCRIPTION,
            "resources": VersionInfo.V2_RESOURCES,
            "endpoints": VersionInfo.V2_ENDPOINTS,
            "features": VersionInfo.V2_FEATURES,
            "breaking_changes": VersionInfo.BREAKING_CHANGES_V2
        }

def get_api_info() -> dict:
    """Retorna informações gerais da API"""
    
    return {
        "title": APIMetadata.TITLE,
        "description": APIMetadata.DESCRIPTION,
        "version": APIMetadata.VERSION,
        "current_version": APIVersion.V2.value,
        "available_versions": [v.value for v in APIVersion],
        "v1_info": get_version_info(APIVersion.V1),
        "v2_info": get_version_info(APIVersion.V2),
        "contact": APIMetadata.CONTACT,
        "license": APIMetadata.LICENSE,
        "docs": {
            "swagger": "/docs",
            "redoc": "/redoc",
            "openapi": "/openapi.json"
        }
    }
