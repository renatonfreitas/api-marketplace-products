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

    @staticmethod
    async def get_by_id(product_id: UUID) -> dict | None:
        """Busca produto por ID"""
        try:
            response = supabase.table("products").select(
                "*, categories:products_categories(category_id, categories(category_id, name))"
            ).eq("product_id", str(product_id)).execute()
            
            return response.data[0] if response.data else None
        except Exception as e:
            logger.error(f"Erro ao buscar produto por ID: {str(e)}")
            raise

    @staticmethod
    async def check_sku_exists(sku: str) -> bool:
        """Verifica se SKU já existe"""
        try:
            query = supabase.table("products").select("product_id").eq("sku", sku)

            response = query.execute()
            return len(response.data) > 0
        except Exception as e:
            logger.error(f"Erro ao verificar SKU: {str(e)}")
            raise


    @staticmethod
    async def create(product_data: dict, category_ids: list[UUID] | None = None) -> dict:
        """Cria novo produto com categoria"""
        
        try:
            # Inserir produto
            response = supabase.table("products").insert(product_data).execute()
            
            if not response.data:
                raise Exception("Falha ao criar produto")

            product = response.data[0]
            product_id = product["product_id"]

            # Adicionar categorias se fornecidas
            if category_ids:
                product_categories = [
                    {"product_id": str(product_id), "category_id": str(cat_id)}
                    for cat_id in category_ids
                ]
                supabase.table("products_categories").insert(product_categories).execute()

            # Retornar produto completo
            return await ProductRepository.get_by_sku(product["sku"])

        except Exception as e:
            logger.error(f"Erro ao criar produto: {str(e)}")
            raise

    @staticmethod
    async def update(product_id: UUID, product_data: dict, category_ids: list[UUID] | None = None) -> dict:
        """Atualiza produto e categorias"""
        
        try:
            #Atualizar produto
            response = supabase.table("products").update(product_data).eq("product_id", str(product_id)).execute()
            
            if not response.data:
                raise Exception("Produto não encontrado")
            
            # Atualizar categorias se fornecidas
            if category_ids is not None:
                # Deletar categorias anteriores
                supabase.table("products_categories").delete().eq("product_id", str(product_id)).execute()

                # Inserir novas categorias
                if category_ids:
                    product_categories = [
                        {"product_id": str(product_id), "category_id": str(cat_id)}
                        for cat_id in category_ids
                    ]
                    supabase.table("products_categories").insert(product_categories).execute()

            return await ProductRepository.get_by_id(product_id)
        
        except Exception as e:
            logger.error(f"Erro ao atualizar produto: {str(e)}")
            raise

    @staticmethod
    async def delete(product_id: UUID) -> bool:
        """Deleta produto e suas categorias"""
        try:
            # Deletar relacionamentos
            supabase.table("products_categories").delete().eq("product_id", str(product_id)).execute()
            
            # Deletar produto
            response = supabase.table("products").delete().eq("product_id", str(product_id)).execute()
            
            return len(response.data) > 0
        except Exception as e:
            logger.error(f"Erro ao deletar produto: {str(e)}")
            raise

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
