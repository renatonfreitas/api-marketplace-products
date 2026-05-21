import logging
from uuid import UUID
from app.core.database import supabase


logger = logging.getLogger(__name__)

class AddressRepository:

    @staticmethod
    async def get_all(supplier_id: UUID | None = None) -> list[dict]:
        try:
            query = supabase.table("addresses").select("*").eq("is_active", True)
            if supplier_id:
                query = query.eq("supplier_id", str(supplier_id))
            response = query.order("city").execute()
            return response.data
        except Exception as e:
            logger.error(f"Erro ao listar endereços: {str(e)}")
            raise

    @staticmethod
    async def get_by_id(address_id:UUID) -> dict | None:
        try:
            response = supabase.table("addresses").select("*").eq(
                "address_id", str(address_id)
            ).eq("is_active", True).execute()
            return response.data[0] if response.data else None
        except Exception as e:
            logger.error(f"Erro ao buscar endereço: {str(e)}")
            raise

    @staticmethod
    async def create(address_data: dict) -> dict:
        try:
            response = supabase.table("addresses").insert(address_data).execute()
            if not response.data:
                raise Exception("Falha ao criar endereço")
            return response.data[0]
        except Exception as e:
            logger.error(f"Erro ao criar endereço: {str(e)}")
            raise

    @staticmethod
    async def update(address_id: UUID, address_data:dict) -> dict:
        try:
            response = supabase.table("addresses").update(
                address_data
            ).eq("address_id", str(address_id)).execute()
            if not response.data:
                raise Exception("Endereço não encontrado")
            return response.data[0]
        except Exception as e:
            logger.error(f"Erro ao atualizar endereço: {str(e)}")
            raise

    @staticmethod
    async def delete(address_id: UUID) -> bool:
        try:
            response = supabase.table("addresses").update({
                "is_active": False
            }).eq("address_id", str(address_id)).execute()
            return len(response.data) > 0
        except Exception as e:
            logger.error(f"Erro ao deletar endereço: {str(e)}")
            raise

    @staticmethod
    async def exists(address_id: UUID) -> bool:
        try:
            response = supabase.table("addresses").select("address_id").eq(
                "address_id", str(address_id)
            ).eq("is_active", True).execute()
            return len(response.data) > 0
        except Exception as e:
            logger.errror(f"Erro ao verificar endereço: {str(e)}")
            raise