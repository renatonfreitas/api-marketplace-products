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
        supplier_id: UUID | None = None,
        min_price: Decimal | None = None, 
        max_price: Decimal | None = None, 
        search: str | None = None,
        only_active: bool = True
    ) -> tuple[list[dict], int]:
        """
        Lista produtos com filtros, paginação e ordenação

        Args:
            page: Número da página (1+)
            limit: Itens por página (1-100)
            sort: Campo para ordenação
            order: Asc ou desc
            category: Nome da categoria (filtro)
            supplier_id: UUID do supplier (filtro)
            min_price: Preço mínimo
            max_price: Preço máximo
            search: Busca em name ou description
            only_active: Mostrar apenas ativos

        Retorna: (produtos, total de registros)
        """
        try:
            # Query base
            query = supabase.table("products").select(
                "product_id, name, sku, unit_price, discount, is_active, created_at, "
                "categories: products_categories(category_id, categories(*)),"
                "suppliers: products_suppliers(supplier_id, suppliers(*, addresses(*)))"
            )

            # Filtros
            if only_active:
                query = query.eq("is_active", True)

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
                cat_response = supabase.table("categories").select("category_id").eq("name", category).eq("is_active", True).execute()

                if not cat_response.data:
                    return [], 0
                
                cat_id = cat_response.data[0]["category_id"]
                prod_ids = supabase.table("products_categories").select(
                    "product_id"
                ).eq("category_id", cat_id).execute().data or []

                if not prod_ids:
                    return [], 0

                query = query.in_("product_id", [p["product_id"] for p in prod_ids])

            if supplier_id:
                sup_prods = supabase.table("products_suppliers").select(
                    "product_id"
                ).eq("supplier_id", str(supplier_id)).execute().data or []

                if not sup_prods:
                    return [], 0
                
                query = query.in_("product_id", [p["product_id"] for p in sup_prods])

            # Contar total antes da paginação
            count_response = query.execute()
            total = len(count_response.data) if count_response.data else 0

            # Ordenação:
            if sort == "unit_price":
                sort_field = "unit_price"
            elif sort == "discount":
                sort_field = "discount"
            elif sort == "created_at":
                sort_field = "created_at"
            else:
                sort_field = "name"

            query = query.order(sort_field, desc=(order.lower() == "desc"))

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
                "*, "
                "categories: products_categories(category_id, categories(*)), "
                "suppliers: products_suppliers(supplier_id, suppliers(*, addresses(*)))"
            ).eq("sku", sku).eq("is_active", True).execute()

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

    @staticmethod
    async def get_by_id(product_id: UUID) -> dict | None:
        """Busca produto pelo ID (UUID) - usado internamente"""
        try:
            response = supabase.table("products").select(
                "*, "
                "categories: products_categories(category_id, categories(*)), "
                "suppliers: products_suppliers(supplier_id, suppliers(*, addresses(*)))"
            ).eq("product_id", str(product_id)).execute()
            
            return response.data[0] if response.data else None
        except Exception as e:
            logger.error(f"Erro ao buscar produto por ID: {str(e)}")
            raise

    @staticmethod
    async def update(
        sku: str,
        product_data: dict,
        category_ids: list[UUID] | None = None,
        supplier_ids: list[UUID] | None = None
    ) -> dict:
        """
        Atualiza produto e suas relações de forma atômica
        
        Args:
            sku: SKU do produto
            product_data: Campos a atualizar na tabela products
            category_ids: Lista de UUIDs de categorias (None = não altera)
            supplier_ids: Lista de UUIDs de suppliers (None = não altera)
        
        Returns:
            Produto atualizado com relações carregadas
        """
        try:
            # Busca o produto atual para obter o ID
            existing = await ProductRepository.get_by_sku(sku)
            if not existing:
                raise ProductNotFoundError(sku)
            
            product_id = existing["product_id"]
            
            # Atualiza campos do produto (se houver dados)
            if product_data:
                update_response = (
                    supabase.table("products")
                    .update(product_data)
                    .eq("sku", sku)
                    .execute()
                )
                
                if not update_response.data:
                    raise Exception(f"Falha ao atualizar produto SKU: {sku}")
            
            # Atualiza relações de categorias (se fornecidas)
            if category_ids is not None:
                await ProductRepository._update_product_categories(
                    product_id, category_ids
                )
            
            # Atualiza relações de suppliers (se fornecidas)
            if supplier_ids is not None:
                await ProductRepository._update_product_suppliers(
                    product_id, supplier_ids
                )
            
            # Retorna o produto completo atualizado
            updated_product = await ProductRepository.get_by_sku(
                product_data.get("sku", sku)  # usa novo SKU se foi alterado
            )
            return updated_product
            
        except ProductNotFoundError:
            raise
        except Exception as e:
            logger.error(f"Erro ao atualizar produto {sku}: {str(e)}")
            raise

    @staticmethod
    async def _update_product_categories(product_id: UUID, category_ids: list[UUID]) -> None:
        """Atualiza relações produto-categoria de forma segura"""
        try:
            # Remove relações existentes
            supabase.table("products_categories") \
                .delete() \
                .eq("product_id", str(product_id)) \
                .execute()
            
            # Insere novas relações (se houver categorias)
            if category_ids:
                relations = [
                    {
                        "product_id": str(product_id),
                        "category_id": str(category_id)
                    }
                    for category_id in category_ids
                ]
                supabase.table("products_categories") \
                    .insert(relations) \
                    .execute()
                    
        except Exception as e:
            logger.error(f"Erro ao atualizar categorias do produto {product_id}: {str(e)}")
            raise

    @staticmethod
    async def _update_product_suppliers(product_id: UUID, supplier_ids: list[UUID]) -> None:
        """Atualiza relações produto-supplier de forma segura"""
        try:
            # Remove relações existentes
            supabase.table("products_suppliers") \
                .delete() \
                .eq("product_id", str(product_id)) \
                .execute()
            
            # Insere novas relações (se houver suppliers)
            if supplier_ids:
                relations = [
                    {
                        "product_id": str(product_id),
                        "supplier_id": str(supplier_id)
                    }
                    for supplier_id in supplier_ids
                ]
                supabase.table("products_suppliers") \
                    .insert(relations) \
                    .execute()
                    
        except Exception as e:
            logger.error(f"Erro ao atualizar suppliers do produto {product_id}: {str(e)}")
            raise

    # TODO
    # @staticmethod
    # async def delete(sku: str) -> bool:
    #     """Deleta produto e suas categorias"""

    @staticmethod
    async def validate_categories_exist(category_ids: list[UUID]) -> bool:
        """Valida se todas as categorias existem"""
        if not category_ids:
                return True
        
        try:
            response = supabase.table("categories").select("category_id").in_(
                "category_id", [str(cid) for cid in category_ids]
            ).eq("is_active", True).execute()
            return len(response.data) == len(category_ids)
        except Exception as e:
            logger.error(f"Erro ao validar categorias: {str(e)}")
            raise
    
    @staticmethod
    async def validate_suppliers_exist(supplier_ids: list[UUID]) -> bool:
        if not supplier_ids:
            return True
        
        try:
            response = supabase.table("suppliers").select("supplier_id").in_(
                "supplier_id", [str(sup_id) for sup_id in supplier_ids]
            ).eq("is_active", True).execute()
            return len(response.data) == len(supplier_ids)
        except Exception as e:
            logger.error(f"Erro ao validar suppliers: {str(e)}")
            raise
