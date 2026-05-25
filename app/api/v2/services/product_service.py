from app.api.v2.repositories.product_repository import ProductRepository
from app.api.v2.repositories.supplier_repository import SupplierRepository
from app.core.exceptions import ProductNotFoundError
from app.core.exceptions import EmptyListResponse, ProductNotFoundError
from app.schemas.v2.product import PaginatedProductResponse, ProductFilterParams, ProductListResponse, ProductRequest, ProductResponse
from decimal import Decimal
from uuid import UUID
import logging

logger = logging.getLogger(__name__)

class ProductService:

    @staticmethod
    async def list_products(params: ProductFilterParams) -> PaginatedProductResponse:
        """Lista produtos com filtros e paginação"""
        try:
            products, total = await ProductRepository.get_all_products(
                page=params.page,
                limit=params.limit,
                sort=params.sort,
                order=params.order,
                category=params.category,
                supplier_id=params.supplier_id,
                min_price=params.min_price,
                max_price=params.max_price,
                search=params.search,
                only_active=params.only_active
            )

            data = []
            for prod in products:
                category_count = len(prod.get("categories", []))
                supplier_count = len(prod.get("suppliers", []))
                
                data.append(ProductListResponse(
                    product_id=UUID(prod["product_id"]),
                    name=prod["name"],
                    sku=prod["sku"],
                    unit_price=Decimal(str(prod["unit_price"])),
                    discount=Decimal(str(prod["discount"])),
                    is_active=prod.get("is_active", True),
                    created_at=prod["created_at"],
                    category_count=category_count,
                    supplier_count=supplier_count
                ))
            
            pages = (total + params.limit - 1) // params.limit if total > 0 else 1
                
            return PaginatedProductResponse(
                data=data,
                total=total,
                page=params.page,
                limit=params.limit,
                pages=pages
            )
        except EmptyListResponse:
            raise
        except Exception as e:
            logger.error(f"Erro ao listar produtos: {str(e)}")
            raise Exception(f"Erro ao listar produtos: {str(e)}")
        
    @staticmethod
    async def get_product(sku: str) -> ProductResponse:
        """Busca produto por SKU"""
        try:
            product = await ProductRepository.get_by_sku(sku)
            if not product:
                raise ProductNotFoundError(sku)
            
            categories = []
            if product.get("categories"):
                for cat_rel in product["categories"]:
                    if cat_rel.get("categories"):
                        categories.append({
                            "category_id": UUID(cat_rel["categories"]["category_id"]),
                            "name": cat_rel["categories"]["name"],
                            "is_active": cat_rel["categories"].get("is_active", True),
                            "created_at": cat_rel["categories"]["created_at"],
                            "updated_at": cat_rel["categories"]["updated_at"]
                        })
            
            suppliers = []
            if product.get("suppliers"):
                for sup_rel in product["suppliers"]:
                    if sup_rel.get("suppliers"):
                        suppliers.append({
                            "supplier_id": UUID(sup_rel["suppliers"]["supplier_id"]),
                            "name": sup_rel["suppliers"]["name"],
                            "email": sup_rel["suppliers"].get("email"),
                            "phone": sup_rel["suppliers"].get("phone"),
                            "is_active": sup_rel["suppliers"].get("is_active", True),
                            "created_at": sup_rel["suppliers"]["created_at"],
                            "updated_at": sup_rel["suppliers"]["updated_at"]
                        })
            
            return ProductResponse(
                product_id=UUID(product["product_id"]),
                sku=product["sku"],
                name=product["name"],
                unit_price=Decimal(str(product["unit_price"])),
                discount=Decimal(str(product["discount"])),
                description=product.get("description"),
                unit_quantity=product.get("unit_quantity"),
                categories=categories,
                suppliers=suppliers,
                is_active=product.get("is_active", True),
                created_at=product["created_at"],
                updated_at=product["updated_at"]
            )
        except ProductNotFoundError:
            raise
        except Exception as e:
            logger.error(f"Erro ao buscar produto: {str(e)}")
            raise Exception(f"Erro ao buscar produto: {str(e)}")
        
    # TODO
    # @staticmethod
    # async def create_product(request: ProductRequest) -> ProductResponse:
    #     """Cria novo produto"""

    @staticmethod
    async def update_product(sku: str, request: ProductUpdate) -> ProductResponse:
        """Atualiza um produto existente (parcial)"""
        try:
            # 1. Valida existência (lógica de negócio)
            existing = await ProductRepository.get_by_sku(sku)
            if not existing:
                raise ProductNotFoundError(sku)

            product_id = UUID(existing["product_id"])

            # 2. Valida novo SKU (se alterado)
            if request.sku and request.sku != sku:
                if await ProductRepository.check_sku_exists(request.sku):
                    raise HTTPException(
                        status_code=status.HTTP_409_CONFLICT,
                        detail=f"SKU '{request.sku}' já está em uso",
                    )

            # 3. Valida categorias e suppliers (se fornecidos)
            if request.category_ids is not None:
                if not await ProductRepository.validate_categories_exist(
                    request.category_ids
                ):
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="Uma ou mais categorias não existem",
                    )
            if request.supplier_ids is not None:
                if not await ProductRepository.validate_suppliers_exist(
                    request.supplier_ids
                ):
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="Um ou mais suppliers não existem",
                    )

            # 4. Prepara dados (apenas campos enviados)
            update_data = request.model_dump(exclude_unset=True)
            category_ids = update_data.pop("category_ids", None)
            supplier_ids = update_data.pop("supplier_ids", None)

            if not update_data and category_ids is None and supplier_ids is None:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Nenhum campo para atualizar",
                )

            # 5. Chama o repository (passando product_id)
            updated_product = await ProductRepository.update(
                product_id=product_id,
                product_data=update_data,
                category_ids=category_ids,
                supplier_ids=supplier_ids,
            )

            # 6. Formata resposta
            return await ProductService._format_product_response(updated_product)

        except ProductNotFoundError:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Produto com SKU '{sku}' não encontrado",
            )
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Erro ao atualizar produto: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Erro ao atualizar produto",
            )

    # TODO
    # @staticmethod
    # async def delete_product(sku: str) -> dict:
    #     """Deleta produto"""    
    
