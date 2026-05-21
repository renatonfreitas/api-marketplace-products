from app.api.v2.repositories.category_repository import CategoryRepository
from app.schemas.v2.category import CategoryResponse, CategoryWithProductCount
from app.core.exceptions import CategoryNotFoundError, InvalidParametersError
from uuid import UUID
import logging


logger = logging.getLogger(__name__)

class CategoryService:

    @staticmethod
    async def list_categories() -> list[CategoryWithProductCount]:
        try:
            categories = await CategoryRepository.get_all()

            result = []
            for cat in categories:
                product_count = await CategoryRepository.get_product_count(
                    UUID(cat["category_id"])
                )
                result.append(CategoryWithProductCount(
                    category_id=UUID(cat["category_id"]),
                    name=cat["name"],
                    is_active=cat.get("is_active", True),
                    created_at=cat["created_at"],
                    updated_at=cat["updated_at"],
                    product_count=product_count
                ))

            return result
        except Exception as e:
            logger.error(f"Erro ao listar categorias: {str(e)}")
            raise

    @staticmethod
    async def get_category(category_id: UUID) -> CategoryWithProductCount:

        try: 
            category = await CategoryRepository.get_by_id(category_id)
            if not category:
                raise CategoryNotFoundError(str(category_id))
            
            product_count = await CategoryRepository.get_product_count(category_id)

            return CategoryWithProductCount(
                category_id=category_id,
                name=category["name"],
                is_active=category.get("is_active", True),
                created_at=category["created_at"],
                updated_at=category["updated_at"],
                product_count=product_count
            )
        except Exception as e:
            logger.error(f"Erro ao buscar categoria: {str(e)}")
            raise

    @staticmethod
    async def create_category(name: str) -> CategoryResponse:
        try:
            category = await CategoryRepository.create(name)
            return CategoryResponse(
                category_id=UUID(category["category_id"]),
                name=category["name"],
                is_active=category.get("is_active", True),
                created_at=category["created_at"],
                updated_at=category["updated_at"]
            )
        except ValueError as e:
            raise InvalidParametersError(str(e))
        except Exception as e:
            logger.erro(f"Erro ao criar categoria: {str(e)}")
            raise

    @staticmethod
    async def update_category(category_id: UUID, name: str) -> CategoryResponse:
        try:
            if not await CategoryRepository.exists(category_id):
                raise CategoryNotFoundError(str(category_id))
            
            category = await CategoryRepository.update(category_id, name)

            return CategoryResponse(
                category_id=UUID(category["category_id"]),
                name=category["name"],
                is_active=category.get("is_active", True),
                created_at=category["created_at"],
                updated_at=category["updated_at"]
            )
        except ValueError as e:
            raise InvalidParametersError(str(e))
        except Exception as e:
            logger.error(f"Erro ao atualizar categoria: {str(e)}")
            raise

    @staticmethod
    async def delete_category(category_id: UUID) -> dict:
        try:
            if not await CategoryRepository.exists(category_id):
                raise CategoryNotFoundError(str(category_id))
            
            await CategoryRepository.delete(category_id)
            return {"message": f"Categoria deletada com sucesso"}
        except Exception as e:
            logger.error(f"Erro ao deletar categoria: {str(e)}")
            raise