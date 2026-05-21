from decimal import Decimal
import logging
from uuid import UUID
from app.core.database import supabase

logger = logging.getLogger(__name__)

class ProductRepository:

    @staticmethod
    async def get_all_products(
        page: int = 1, 
        limit: int = 10, 
        sort: str = "name", 
        order: str = "asc", 
        category: str | None = None, 
        min_price: Decimal | None = None, 
        max_price: Decimal | None = None, 
        search: str | None = None
    ) -> tuple[list[dict], int]:
        """
        Lista produtos com filtros, paginação e ordenação
        Retorna: (produtos, total de registros)
        """
        try:
            # Query base
            query = supabase.table("products").select(
                "product_id, name, sku, description, quantity_per_unit, "
                "unit_price, discount, created_at, updated_at, "
                "categories: products_categories(category_id, categories(category_id, name))"
            )

            # Filtros
            if search:
                # Busca por nome ou descrição (case-insensitive)
                query = query.or_(f"name.ilike.%{search}%.description.ilike.%{search}%")

            if min_price is not None:
                query = query.gte("unit_price", float(min_price))

            if max_price is not None:
                query = query.lte("unit_price", float(max_price))

            # Se filtrar por categoria, precisa de join
            if category:

                # Buscar categoria
                cat_response = supabase.table("categories").select("category_id").eq("name", category).execute()
                if not cat_response.data:
                    return [], 0
                
                category_id = cat_response.data[0]["category_id"]
                query = query.in_("product_id",
                    supabase.table("products_categories")
                    .select("product_id")
                    .eq("category_id", category_id)
                    .execute()
                    .data or []                  
                )

            # Contar total antes da paginação
            count_response = query.execute()
            total = len(count_response.data) if count_response.data else 0

            # Ordenação:
            if sort == "unit_price":
                sort = "unit_price"
            elif sort == "discount":
                sort = "discount"
            elif sort == "created_at":
                sort = "created_at"
            else:
                sort = "name"

            query = query.order(sort, desc=(order.lower() == "desc"))

            # Paginação
            offset = (page - 1) * limit
            response = query.range(offset, offset + limit - 1).execute()

            return response.data, total

        except Exception as e:
            logger.error(f"Erro ao listar produtos: {str(e)}")
            # return [], 0
            raise

    @staticmethod
    async def get_by_sku(sku: str) -> dict | None:
        """Busca produto por SKU"""
        try:
            response = supabase.table("products").select(
                "*, categories: products_categories(category_id, categories(category_id, name))"
            ).eq("sku", sku).execute()

            return response.data[0] if response.data else None
        
        except Exception as e:
            logger.error(f"Erro ao buscar produto por SKU: {str(e)}")
            raise

    async def check_sku_exists(sku: str) -> bool:
        """Verifica se SKU já existe"""
        try:
            query = supabase.table("products").select("product_id").eq("sku", sku)

            response = query.execute()
            return len(response.data > 0)
        except Exception as e:
            logger.error(f"Erro ao verificar SKU: {str(e)}")
            raise


    # TODO
    # @staticmethod
    # async def create(product_data: dict, category_ids: list[UUID] | None = None) -> dict:
    #     """Cria novo produto com categorias"""

    # TODO
    # @staticmethod
    # async def update(sku: str, product_data: dict, category_ids: list[UUID] | None = None) -> dict:
    #     """Atualiza produto e categorias"""

    # TODO
    # @staticmethod
    # async def delete_product(sku: str) -> bool:
    #     """Deleta produto e suas categorias"""

    @staticmethod
    async def validate_categories_exist(category_ids: list[UUID]) -> bool:
        """Valida se todas as categorias existem"""
        try:
            if not category_ids:
                return True
            response = supabase.table("categories").select("category_id").in_(
                "category_id",
                [str(cid) for cid in category_ids]
            ).execute()

            return len(response.data) == len(category_ids)
        except Exception as e:
            logger.error(f"Erro ao validar categorias: {str(e)}")
            raise