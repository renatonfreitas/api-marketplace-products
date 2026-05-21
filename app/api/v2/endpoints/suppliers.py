from app.api.v2.services.supplier_service import SupplierService
from app.schemas.v2.supplier import SupplierRequest, SupplierResponse, SupplierUpdate, SupplierWithProductCount
from fastapi import APIRouter, HTTPException, Query, status
from uuid import UUID
import logging


logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/suppliers",
    tags=["suppliers-v2"],
     responses={
        400: {"description": "Parâmetros inválidos"},
        404: {"description": "Não encontrado"},
        500: {"description": "Erro no servidor"}
    }
)

@router.get("", response_model=dict, status_code=status.HTTP_200_OK)
async def list_suppliers(
    page: int = Query(1, ge=1), 
    limit: int = Query(10, ge=1, le=100), 
    search: str = Query(default=None),
    only_active: bool = Query(default=True)
):
    try:
        suppliers, total = await SupplierService.list_suppliers(page, limit, search, only_active)
        return {
            "data": suppliers,
            "total": total,
            "page": page,
            "limit": limit,
            "pages": (total + limit - 1) // limit
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro ao listar suppliers"
        )

@router.get("/{supplier_id}", response_model=SupplierWithProductCount, status_code=status.HTTP_200_OK)
async def get_supplier(supplier_id: UUID):
    try:
        return await SupplierService.get_supplier(supplier_id)
    except ValueError as e:
        logger.error(f"Erro ao buscar supplier: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Supplier não encontrado"
        )
    except Exception as e:
        logger.error(f"Erro ao buscar supplier: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro ao buscar supplier"
        )

@router.post("", response_model=SupplierResponse, status_code=status.HTTP_201_CREATED)
async def create_supplier(supplier: SupplierRequest):
    try:
        return await SupplierService.create_supplier(supplier.model_dump())
    except Exception as e:
        logger.error(f"Erro ao criar supplier: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro ao criar supplier"
        )

@router.put("/{supplier_id}", response_model=SupplierResponse, status_code=status.HTTP_200_OK)
async def update_supplier(supplier_id: UUID, supplier: SupplierUpdate):
    try:
        return await SupplierService.update_supplier(supplier_id, supplier.model_dump(exclude_none=True))
    except ValueError as e:
        logger.error(f"Erro ao atualizar supplier: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Supplier não encontrado"
        )
    except Exception as e:
        logger.error(f"Erro ao atualizar supplier: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro ao atualizar supplier"
        )

@router.delete("/{supplier_id}")
async def delete_supplier(supplier_id: UUID, status_code=status.HTTP_200_OK):
    try:
        return await SupplierService.delete_supplier(supplier_id)
    except Exception as e:
        logger.error(f"Erro ao deletar supplier: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro ao deletar supplier"
        )