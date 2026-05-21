from app.api.v2.services.address_service import AddressService
from app.schemas.v2.address import AddressRequest, AddressResponse
from fastapi import APIRouter, HTTPException, status
from uuid import UUID
import logging


logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/addresses",
    tags=["addresses-v2"],
    responses={
        400: {"description": "Parâmetros inválidos"},
        404: {"description": "Não encontrado"},
        500: {"description": "Erro no servidor"}
    }
)

@router.get("", response_model=list[AddressResponse], status_code=status.HTTP_200_OK)
async def list_addresses():
    """Lista todos os endereços"""
    try:
        return await AddressService.list_addresses()
    except Exception as e:
        logger.error(f"Erro ao listar endereços: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro ao listar endereços"
        )
    
@router.get("/{address_id}", response_model=AddressResponse, status_code=status.HTTP_200_OK)
async def get_address(address_id: UUID):
    """Obtém um endereço específico"""
    try:
        return await AddressService.get_address(address_id)
    except ValueError as e:
        logger.error(f"Erro ao buscar endereço: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Endereço não encontrado"
        )
    except Exception as e:
        logger.error(f"Erro ao buscar endereço: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro ao buscar endereço"
        )
    
@router.post("", response_model=AddressResponse, status_code=status.HTTP_201_CREATED)
async def create_address(address: AddressRequest):
    """Cria um novo endereço"""
    try:
        return await AddressService.create_address(address.model_dump())
    except Exception as e:
        logger.error(f"Erro ao criar endereço: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro ao criar endereço"
        )
    
@router.put("/{address_id}", response_model=AddressResponse, status_code=status.HTTP_200_OK)
async def update_address(address_id: UUID, address: AddressRequest):
    """Atualiza um endereço"""
    try:
        return await AddressService.update_address(address_id, address.model_dump(exclude_none=True))
    except ValueError as e:
        logger.error(f"Erro ao atualizar endereço: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Endereço não encontrado"
        )
    except Exception as e:
        logger.error(f"Erro ao atualizar endereço: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro ao atualizar endereço"
        )
    
@router.delete("/{address_id}", status_code=status.HTTP_200_OK)
async def delete_address(address_id: UUID):
    """Deleta um endereço"""
    try:
        return await AddressService.delete_address(address_id)
    except Exception as e:
        logger.error(f"Erro ao deletar endereço: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro ao deletar endereço"
        )