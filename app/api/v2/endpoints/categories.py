from app.api.v2.services.category_service import CategoryService
from app.schemas.v2.category import CategoryRequest, CategoryResponse, CategoryWithProductCount
from fastapi import APIRouter, HTTPException, status
from uuid import UUID
import logging


logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/categories",
    tags=["categories-v2"],
     responses={
        400: {"description": "Parâmetros inválidos"},
        404: {"description": "Não encontrado"},
        500: {"description": "Erro no servidor"}
    }
)

@router.get("", response_model=list[CategoryWithProductCount], status_code=status.HTTP_200_OK)
async def list_categories():
    try:
        return await CategoryService.list_categories()
    except Exception as e:
        logger.error(f"Erro ao listar categorias: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro ao listar categorias"
        )

@router.get("/{category_id}", response_model=CategoryWithProductCount, status_code=status.HTTP_200_OK)
async def get_category(category_id: UUID):
    try:
        return await CategoryService.get_category(category_id)
    except ValueError as e:
        logger.error(f"Erro ao buscar categoria: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Categoria não encontrado"
        )
    except Exception as e:
        logger.error(f"Erro ao buscar categoria: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro ao buscar categoria"
        )

@router.post("", response_model=CategoryResponse, status_code=status.HTTP_201_CREATED)
async def create_category(category: CategoryRequest):
    try:
        return await CategoryService.create_category(category.name)
    except Exception as e:
        logger.error(f"Erro ao criar categoria: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro ao criar categoria"
        )

@router.put("/{category_id}", response_model=CategoryResponse, status_code=status.HTTP_200_OK)
async def update_category(category_id: UUID, category: CategoryRequest):
    try:
        return await CategoryService.update_category(category_id, category.name)
    except ValueError as e:
        logger.error(f"Erro ao atualizar categoria: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Categoria não encontrado"
        )
    except Exception as e:
        logger.error(f"Erro ao atualizar categoria: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro ao atualizar categoria"
        )

@router.delete("/{category_id}", status_code=status.HTTP_200_OK)
async def delete_category(category_id: UUID):
    try:
        return await CategoryService.delete_category(category_id)
    except Exception as e:
        logger.error(f"Erro ao deletar categoria: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro ao deletar categoria"
        )