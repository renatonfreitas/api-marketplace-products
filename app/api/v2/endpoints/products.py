from decimal import Decimal
import logging
from fastapi import APIRouter, Body, HTTPException, Path, Query, status
from sqlmodel import default
from app.api.v2.services.product_service import ProductService
from app.core.exceptions import EmptyListResponse
from app.schemas.v2.product import PaginatedProductResponse, ProductFilterParams, ProductRequest, ProductResponse, ProductUpdate

logger = logging.getLogger(__name__)

router = APIRouter( # Controller
    prefix="/products",
    tags=["products-v2"],
    responses={
        400: {"description": "Parâmetros inválidos"},
        404: {"description": "Não encontrado"},
        409: {"description": "Conflito"},
        500: {"description": "Erro no servidor"}
    }
)

@router.get("", response_model=PaginatedProductResponse)
async def list_products(
    page: int = Query(default=1, ge=1, description="Número da página"),
    limit: int = Query(default=10, ge=1, le=100, description="Itens por página"),
    sort: str = Query(default="name", pattern="^(name|unit_price|discount|created_at)$", description="Campo para ordenação"),
    order: str = Query(default="asc", pattern="^(asc|desc)$", description="Ordem ascendente ou descendente"),
    category: str | None = Query(default=None, description="Nome da categoria para filtrar"),
    supplier_id: str | None = Query(default=None, description="Filtrar por UUID do supplier"),
    min_price: Decimal | None = Query(default=None, ge=0, description="Preço mínimo"),
    max_price: Decimal | None = Query(default=None, ge=0, description="Preço máximo"),
    search: str | None = Query(default=None, description="Busca por nome ou descrição"),
    only_active: bool = Query(default=True, description="Mostrar apenas produtos ativos")
):
    """
    Lista todos os produtos com filtros avançados
    
    - **page**: Número da página (padrão: 1)
    - **limit**: Itens por página (padrão: 10, máximo: 100)
    - **sort**: Campo para ordenação (name, unit_price, discount, created_at)
    - **order**: Ordem (asc ou desc)
    - **category**: Nome da categoria
    - **supplier_id**: UUID do supplier
    - **min_price**: Preço mínimo
    - **max_price**: Preço máximo
    - **search**: Busca livre
    - **only_active**: Mostrar apenas ativos (padrão: true)
    """
    try:
        params = ProductFilterParams(
            page=page,
            limit=limit,
            sort=sort,
            order=order,
            category=category,
            min_price=min_price,
            max_price=max_price,
            search=search,
            only_active=only_active
        )

        return await ProductService.list_products(params)
    
    except EmptyListResponse as e:
        raise e
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Parâmetros inválidos: {str(e)}"
        )
    except Exception as e:
        logger.error(f"Erro ao listar produtos: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro ao listar produtos"
        )

@router.get("/sku", response_model=ProductResponse, status_code=status.HTTP_200_OK)
async def get_product(sku: str):
    """
    Obtém um produto específico pelo SKU
    
    - **sku**: Código único do produto
    """

    try:
        return await ProductService.get_product(sku)
    except ValueError as e:
        logger.warning(f"Produto não encontrado: {sku}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Erro ao buscar produto: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro ao buscar produto"
        )

@router.post("", response_model=ProductResponse, status_code=status.HTTP_201_CREATED)
async def create_product(product: ProductRequest):
    """
    Cria um novo produto
    
    - **sku**: Código único (obrigatório)
    - **name**: Nome do produto (obrigatório)
    - **unit_price**: Preço unitário (obrigatório, deve ser > 0)
    - **discount**: Desconto em % (opcional, 0-100)
    - **description**: Descrição (opcional)
    - **unit_quantity**: Quantidade por unidade (opcional)
    - **category_ids**: Lista de IDs de categorias (opcional)
    - **supplier_ids**: Lista de IDs de suppliers (opcional)
    """
    try:
        return await ProductService.create_product(
            sku=product.sku,
            name=product.name,
            unit_price=product.unit_price,
            discount=product.discount,
            description=product.description,
            unit_quantity=product.unit_quantity,
            category_ids=product.category_ids,
            supplier_ids=product.supplier_ids
        )
    except ValueError as e:
        logger.warning(f"Erro de validação: {str(e)}")
        if "já existe" in str(e):
            raise HTTPException(status_code=409, detail=str(e))
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Erro ao criar produto: {str(e)}")
        raise HTTPException(status_code=500, detail="Erro ao criar produto")

@router.put("/{sku}", response_model=ProductResponse)
async def update_product(sku: str, product: ProductUpdate):
    """
    Atualiza um produto existente
    
    - **sku**: SKU do produto a atualizar
    - Outros campos são opcionais
    """
    try:
        return await ProductService.update_product(
            sku=sku,
            new_sku=product.sku,
            name=product.name,
            unit_price=product.unit_price,
            discount=product.discount,
            description=product.description,
            unit_quantity=product.unit_quantity,
            is_active=product.is_active,
            category_ids=product.category_ids,
            supplier_ids=product.supplier_ids
        )
    except ValueError as e:
        logger.warning(f"Erro de validação: {str(e)}")
        if "não encontrado" in str(e):
            raise HTTPException(status_code=404, detail=str(e))
        if "já existe" in str(e):
            raise HTTPException(status_code=409, detail=str(e))
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Erro ao atualizar produto: {str(e)}")
        raise HTTPException(status_code=500, detail="Erro ao atualizar produto")
    
@router.delete("/{sku}", status_code=status.HTTP_200_OK)
async def delete_product(sku: str):
    """
    Deleta um produto (soft delete - marca como inativo)
    
    - **sku**: SKU do produto a deletar
    """
    try:
        return await ProductService.delete_product(sku)
    except ValueError as e:
        logger.warning(f"Produto não encontrado: {sku}")
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Erro ao deletar produto: {str(e)}")
        raise HTTPException(status_code=500, detail="Erro ao deletar produto")
