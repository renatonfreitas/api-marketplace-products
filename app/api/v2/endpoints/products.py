from decimal import Decimal
import logging
from fastapi import APIRouter, HTTPException, Query, status
from sqlmodel import default
from app.api.v2.services.product_service import ProductService
from app.core.exceptions import EmptyListResponse
from app.schemas.v2.product import PaginatedProductResponse, ProductFilterParams, ProductResponse

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

# TODO
# @router.post("", response_model=ProductResponse, status_code=status.HTTP_201_CREATED)
# async def create_product(product: ProductRequest):
#     """
#     Cria um novo produto

#     **Body:**
#     - name: Nome do produto (obrigatório)
#     - sku: Identificador único (obrigatório)
#     - unit_price: Preço unitário em decimal (obrigatório)
#     - description: Descrição (opcional)
#     - quantity_per_unit: Quantidade por unidade (opcional)
#     - discount: Desconto em % (0-100, padrão: 0)
#     - category_ids: Lista de UUIDs de categorias (opcional)
    
#     **Responses:**
#     - 201: Produto criado com sucesso
#     - 400: Dados inválidos
#     - 409: SKU já existe
#     - 500: Erro no servidor
#     """

router.put(
    "/{sku}",
    response_model=ProductResponse,
    status_code=status.HTTP_200_OK,
    summary="Atualizar produto",
    description="Atualiza um produto existente. Envie apenas os campos que deseja alterar."
)
async def update_product(
    sku: str = Path(..., description="SKU do produto a atualizar"),
    product: ProductUpdate = Body(..., description="Campos a atualizar (todos opcionais)")
):
    """
    Atualiza um produto e suas relações (categorias e fornecedores).
    - **sku**: SKU do produto a ser atualizado.
    - **Body**: Campos opcionais a serem atualizados.
    """
    try:
        return await ProductService.update_product(sku, product)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao atualizar produto: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro ao atualizar produto"
        )
    


# TODO
# @router.delete("/{sku}", status_code=status.HTTP_200_OK)
# async def delete_product(sku: str):
#     """
#     Deleta um produto.

#     **Path:**
#     - sku: SKU do produto a deletar
    
#     **Responses:**
#     - 200: Produto deletado com sucesso
#     - 404: Produto não encontrado
#     - 409: Produto não pode ser deletado
#     - 500: Erro no servidor
#     """
