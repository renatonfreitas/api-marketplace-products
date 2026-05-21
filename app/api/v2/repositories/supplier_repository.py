import logging
from uuid import UUID
from app.core.database import supabase

logger = logging.getLogger(__name__)

class SupplierRepository:

    @staticmethod
    async def get_all(
        page: int = 1,
        limit: int = 10,
        search: str | None = None,
        only_active: bool = True,
    ) -> tuple[list[dict], int]:
        try:
            query = supabase.table("suppliers").select("*, addresses(*)")

            if only_active:
                query = query.eq("is_active", True)

            if search:
                query = query.or_(f"name.ilike.%{search}%, email.ilike.%{search}%")

            count_response = query.execute()
            total = len(count_response.data)

            offset = (page - 1) * limit
            query = query.order("name")
            response = query.range(offset, offset + limit - 1).execute()

            return response.data, total
        except Exception as e:
            logger.error(f"Erro ao listar suppliers: {str(e)}")
            raise

    @staticmethod
    async def get_by_id(supplier_id: UUID) -> dict | None:
        try:
            response = supabase.table("suppliers").select(
                "*, addresses(*)"
            ).eq("supplier_id", str(supplier_id)).eq("is_active", True).execute()
            return response.data[0] if response.data else None
        except Exception as e:
            logger.error(f"Erro ao buscar supplier: {str(e)}")
            raise
    
    @staticmethod
    async def create(supplier_data: dict) -> dict:
        try:
            response = supabase.table("suppliers").insert(supplier_data).execute()
            if not response.data:
                raise Exception("Falha ao criar supplier")
            return response.data[0]
        except Exception as e:
            logger.error(f"Erro ao criar supplier: {str(e)}")
            if "duplicate key" in str(e).lower():
                raise ValueError(f"Supplier com este email ou nome já existe")
            raise
    
    @staticmethod
    async def update(supplier_id: UUID, supplier_data: dict) -> dict:
        try:
            response = supabase.table("suppliers").update(
                supplier_data
            ).eq("supplier_id", str(supplier_id)).execute()
            if not response.data:
                raise Exception("Supplier não encontrado")
            return response.data[0]
        except Exception as e:
            logger.error(f"Erro ao atualizar supplier: {str(e)}")
            raise

    @staticmethod
    async def delete(supplier_id: UUID) -> bool:
        try:
            response = supabase.table("suppliers").update({
                "is_active": False
            }).eq("supplier_id", str(supplier_id)).execute()
            return len(response.data) > 0
        except Exception as e:
            logger.error(f"Erro ao deletar supplier: {str(e)}")
            raise

    @staticmethod
    async def exists(supplier_id: UUID) -> bool:
        try:
            response = supabase.table("suppliers").select("supplier_id").eq(
                "supplier_id", str(supplier_id)
            ).eq("is_active", True).execute()
            return len(response.data) > 0
        except Exception as e:
            logger.error(f"Erro ao verificar supplier: {str(e)}")
            raise

    @staticmethod
    async def get_product_count(supplier_id: UUID) -> int:
        try:
            response = supabase.table("products_suppliers").select(
                "product_id"
            ).eq("supplier_id", str(supplier_id)).execute()
            return len(response.data)
        except Exception as e:
            logger.error(f"Erro ao contar produtos: {str(e)}")
            return 0