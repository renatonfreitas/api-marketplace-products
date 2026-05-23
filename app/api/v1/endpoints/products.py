
from decimal import Decimal
from fastapi import APIRouter, HTTPException, Query, status
from app.api.v1.services.product_service import ProductService
from app.core.exceptions import EmptyListResponse
from app.schemas.v1.product import PaginatedProductResponse, ProductFilterParams, ProductListResponse, ProductResponse, ProductRequest
logger = logging.getLogger(__name__)

router = APIRouter( # Controller
    prefix="/products",
    tags=["products"],
    responses={
        400: {"description": "Parâmetros inválidos"},
        404: {"description": "Não encontrado"},
        409: {"description": "Conflito"},
        500: {"description": "Erro no servidor"}
    }
)

@router.get("", response_model=PaginatedProductResponse, status_code=status.HTTP_200_OK)
async def list_products(
    page: int = Query(default=1, ge=1, description="Número da página"),
    limit: int = Query(default=10, ge=1, le=100, description="Itens por página"),
    sort: str = Query(default="name", pattern="^(name|unit_price|discount|created_at)$", description="Campo para ordenação"),
    order: str = Query(default="asc", pattern="^(asc|desc)$", description="Ordem de classificação"),
    category: str | None = Query(default=None, description="Filtrar por nome da categoria"),
    min_price: Decimal | None = Query(default=None, ge=0, description="Preço mínimo"),
    max_price: Decimal | None = Query(default=None, ge=0, description="Preço máximo"),
    search: str | None = Query(default=None, min_length=1, max_length=255, description="Buscar por nome ou descrição")
):
    """
    Lista todos os produtos com suporte a filtros, paginação e busca.
    
    **Query Parameters:**
    - page: Número da página (padrão: 1)
    - limit: Itens por página, máximo 100 (padrão: 10)
    - sort: Campo para ordenação (name, unit_price, discount, created_at)
    - order: asc ou desc
    - category: Nome da categoria para filtrar
    - min_price: Preço mínimo
    - max_price: Preço máximo
    - search: Busca parcial por nome ou descrição
    
    **Responses:**
    - 200: Lista de produtos com paginação
    - 204: Nenhum produto encontrado
    - 400: Parâmetros inválidos
    - 500: Erro no servidor
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
            search=search
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

@router.get("/{sku}", response_model=ProductResponse, status_code=status.HTTP_200_OK)
async def get_product(sku: str):
    """
    Retorna um produto específico pelo SKU
    
    **Responses:**
    - 200: Produto encontrado
    - 404: Produto não encontrado
    - 500: Erro no servidor
    """
    
    try:
        return await ProductService.get_product_by_sku(sku)
    except HTTPException as e:
        raise e
    except Exception as e:
        logger.error(f"Erro ao buscar produto: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro ao buscar produto"
        )
@staticmethod
async def create_product(request: ProductRequest) -> ProductResponse:
    """Cria novo produto"""

    try:
        # Verifica SKU duplicado
        sku_exists = await ProductRepository.check_sku_exists(request.sku)

        if sku_exists:
            raise DuplicateSkuError(request.sku)

        # Validar categorias
        if request.category_ids:
            categories_valid = await ProductRepository.validate_categories_exist(
                request.category_ids
            )

            if not categories_valid:
                raise CategoryNotFoundError(request.category_ids[0])

        # Dados do produto
        product_data = {
            "name": request.name,
            "sku": request.sku,
            "description": request.description,
            "quantity_per_unit": request.quantity_per_unit,
            "unit_price": float(request.unit_price),
            "discount": float(request.discount)
        }

        # Repository salva no banco
        created_product = await ProductRepository.create(
            product_data=product_data,
            category_ids=request.category_ids
        )

        return ProductResponse(
            product_id=UUID(created_product["product_id"]),
            name=created_product["name"],
            sku=created_product["sku"],
            description=created_product["description"],
            quantity_per_unit=created_product["quantity_per_unit"],
            unit_price=Decimal(str(created_product["unit_price"])),
            discount=Decimal(str(created_product["discount"])),
            categories=[],
            created_at=created_product["created_at"],
            updated_at=created_product["updated_at"]
        )

    except (
        DuplicateSkuError,
        CategoryNotFoundError
    ):
        raise

    except Exception as e:
        logger.error(f"Erro ao criar produto: {str(e)}")

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro ao criar produto"
        )

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

# TODO
# @router.put("/{sku}", response_model=ProductResponse)
# async def update_product(sku: str, product: ProductRequest):
#     """
#     Atualiza um produto

#     **Path:**
#     - sku: SKU do produto a atualizar
    
#     **Body (todos opcionais):**
#     - name: Novo nome
#     - sku: Novo SKU
#     - unit_price: Novo preço
#     - description, quantity_per_unit, discount: outros campos
#     - category_ids: Nova lista de categorias
    
#     **Responses:**
#     - 200: Produto atualizado
#     - 400: Dados inválidos
#     - 404: Produto não encontrado
#     - 409: SKU já existe
#     - 500: Erro no servidor
#     """
    ssss


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
