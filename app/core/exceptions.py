from uuid import UUID

from fastapi import HTTPException, status


class ProductNotFoundError(HTTPException):
    def __init__(self, sku: str):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Produto com SKU '{sku}' não encontrado"
        )

class DuplicateSkuError(HTTPException):
    def __init__(self, sku: str):
        super().__init__(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"SKU '{sku}' já existe no banco de dados"
        )

class InvalidParametersError(HTTPException):
    def __init__(self, message: str = "Parâmetros inválidos"):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=message
        )

class CannotDeleteProductError(HTTPException):
    def __init__(self, sku: str, reason: str = ""):
        detail = f"Produto '{sku}' não pode ser deletado"
        if reason: 
            detail += f": {reason}"
        super().__init__(
            status.HTTP_409_CONFLICT,
            detail=detail
        )
    
class CategoryNotFoundError(HTTPException):
    def __init__(self, category_id: UUID):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Categoria com ID '{category_id}' não encontrada"
        )

class EmptyListResponse(HTTPException):
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_204_NO_CONTENT,
            detail="Nenhum produto encontrado"
        )
