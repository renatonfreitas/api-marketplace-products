import logging
from uuid import UUID
from app.core.database import supabase


logger = logging.getLogger(__name__)

class CategoryRepository:

    @staticmethod
    async def get_all() -> list[dict]:
        try:
            response = supabase.table("categories").select("*").eq("is_active", True).order("name").execute()
            return response.data
        except Exception as e:
            logger.error(f"Erro ao listar categorias {str(e)}")
            raise

    @staticmethod
    async def get_by_id(category_id: UUID) -> dict | None:
        try:
            response = supabase.table("categories").select("*").eq(
                "category_id", str(category_id)
            ).eq("is_active", True).execute()
            return response.data[0] if response.data else None
        except Exception as e:
            logger.error(f"Erro ao buscar categoria: {str(e)}")
            raise

    @staticmethod
    async def create(name: str) -> dict:
        try:
            response = supabase.table("categories").insert({
                "name": name.strip(),
                "is_active": True
            }).execute()
            if not response.data:
                raise Exception("Falha ao criar categoria")
            return response.data[0]
        except Exception as e:
            logger.error(f"Erro ao criar categoria: {str(e)}")
            if "duplicate key" in str(e).lower():
                raise ValueError(f"Categoria '{name}' já existe")
            raise

    @staticmethod
    async def update(category_id: UUID, name: str) -> dict:
        try:
            response = supabase.table("categories").update({
                "name": name.strip()
            }).eq("category_id", str(category_id)).execute()
            if not response.data:
                raise Exception("Categoria não encontrada")
            return response.data[0]
        except Exception as e:
            logger.error(f"Erro ao atualizar categoria: {str(e)}")
            raise

    @staticmethod
    async def delete(category_id: UUID) -> bool:
        try:
            response = supabase.table("categories").update({
                "is_active": False
            }).eq("category_id", str(category_id)).execute()
            return len(response.data) > 0
        except Exception as e:
            logger.error(f"Erro ao deletar categoria: {str(e)}")
            raise

    @staticmethod
    async def exists(category_id: UUID) -> bool:
        try:
            response = supabase.table("categories").select("category_id").eq(
                "category_id", str(category_id)
            ).eq("is_active", True).execute()
            return len(response.data) > 0
        except Exception as e:
            logger.error(f"Erro ao verificar categoria: {str(e)}")
            raise

    @staticmethod
    async def get_product_count(category_id: UUID) -> int:
        try:
            response = supabase.table("products_categories").select(
                "product_id"
            ).eq("category_id", str(category_id)).execute()
            return len(response.data)
        except Exception as e:
            logger.error(f"Erro ao contar produtos: {str(e)}")
            return 0