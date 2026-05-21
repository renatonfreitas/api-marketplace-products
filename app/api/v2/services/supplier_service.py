import logging
from uuid import UUID

from app.api.v2.repositories.supplier_repository import SupplierRepository
from app.schemas.v2.supplier import SupplierResponse, SupplierWithProductCount


logger = logging.getLogger(__name__)

class SupplierService:

    @staticmethod
    async def list_suppliers(
        page: int = 1,
        limit: int = 10, 
        search: str = None,
        only_active: bool = True
    ) -> tuple[list[SupplierWithProductCount], int]:
        try:
            suppliers, total = await SupplierRepository.get_all(page, limit, search, only_active)

            result = []
            for sup in suppliers:
                product_count = await SupplierRepository.get_product_count(
                    UUID(sup["supplier_id"])
                )
                result.append(SupplierWithProductCount(
                    supplier_id=UUID(sup["supplier_id"]),
                    name=sup["name"],
                    email=sup.get("email"),
                    phone=sup.get("phone"),
                    is_active=sup.get("is_active", True),
                    addresses=[],
                    created_at=sup["created_at"],
                    updated_at=sup["updated_at"],
                    product_count=product_count
                ))

            return result, total
        except Exception as e:
            logger.error(f"Erro ao listar suppliers: {str(e)}")
            raise

    @staticmethod
    async def get_supplier(supplier_id: UUID) -> SupplierWithProductCount:
        try:
            supplier = await SupplierRepository.get_by_id(supplier_id)
            if not supplier:
                raise ValueError(f"Supplier não encontrado")
            
            product_count = await SupplierRepository.get_product_count(supplier_id)

            return SupplierWithProductCount(
                supplier_id=UUID(supplier["supplier_id"]),
                name=supplier["name"],
                email=supplier.get("email"),
                phone=supplier.get("phone"),
                is_active=supplier.get("is_active", True),
                addresses=[],
                created_at=supplier["created_at"],
                updated_at=supplier["updated_at"],
                product_count=product_count
            )
        except Exception as e:
            logger.error(f"Erro ao buscar supplier: {str(e)}")
            raise

    @staticmethod
    async def create_supplier(supplier_data: dict) -> SupplierResponse:
        try:
            supplier = await SupplierRepository.create({
                **supplier_data,
                "is_active": True
            })

            return SupplierResponse(
                supplier_id=UUID(supplier["supplier_id"]),
                name=supplier["name"],
                email=supplier.get("email"),
                phone=supplier.get("phone"),
                is_active=supplier.get("is_active", True),
                addresses=[],
                created_at=supplier["created_at"],
                updated_at=supplier["updated_at"]
            )
        except Exception as e:
            logger.error(f"Erro ao criar supplier: {str(e)}")
            raise

    @staticmethod
    async def update_supplier(supplier_id: UUID, supplier_data: dict) -> SupplierResponse:
        try:
            supplier = await SupplierRepository.update(supplier_id, supplier_data)

            return SupplierResponse(
                supplier_id=UUID(supplier["supplier_id"]),
                name=supplier["name"],
                email=supplier.get("email"),
                phone=supplier.get("phone"),
                is_active=supplier.get("is_active", True),
                addresses=[],
                created_at=supplier["created_at"],
                updated_at=supplier["updated_at"]
            )
        except Exception as e:
            logger.error(f"Erro ao atualizar supplier: {str(e)}")
            raise

    @staticmethod
    async def delete_supplier(supplier_id: UUID) -> dict:
        try:
            await SupplierRepository.delete(supplier_id)
            return {"message": "Supplier deletado"}
        except Exception as e:
            logger.error(f"Erro ao deletar supplier: {str(e)}")
            raise