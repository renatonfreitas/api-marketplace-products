from app.api.v2.repositories.address_repository import AddressRepository
from app.schemas.v2.address import AddressResponse
from app.core.exceptions import InvalidParametersError
from uuid import UUID
import logging


logger = logging.getLogger(__name__)

class AddressService:

    @staticmethod
    async def list_addresses(supplier_id: UUID = None) -> list[AddressResponse]:
        try:
            addresses = await AddressRepository.get_all(supplier_id)
            return [
                AddressResponse(
                    address_id=UUID(addr["address_id"]),
                    supplier_id=UUID(addr["supplier_id"]),
                    street=addr["street"],
                    number=addr.get("number"),
                    complement=addr.get("complement"),
                    neighborhood=addr.get("neighborhood"),
                    city=addr["city"],
                    state=addr["state"],
                    zip_code=addr["zip_code"],
                    country=addr.get("country", "Brasil"),
                    is_active=addr.get("is_active", True),
                    created_at=addr["created_at"],
                    updated_at=addr["updated_at"]
                )
                for addr in addresses
            ]
        except Exception as e:
            logger.error(f"Erro ao listar endereços: {str(e)}")
            raise

    @staticmethod
    async def get_address(address_id: UUID) -> AddressResponse:
        try:
            address = await AddressRepository.get_by_id(address_id)
            if not address:
                raise InvalidParametersError(f"Endereço com ID '{address_id}' não encontrado")
            
            return AddressResponse(
                address_id=UUID(address["address_id"]),
                supplier_id=UUID(address["supplier_id"]),
                street=address["street"],
                number=address.get("number"),
                complement=address.get("complement"),
                neighborhood=address.get("neighborhood"),
                city=address["city"],
                state=address["state"],
                zip_code=address["zip_code"],
                country=address.get("country", "Brasil"),
                is_active=address.get("is_active", True),
                created_at=address["created_at"],
                updated_at=address["updated_at"]
            )
        except Exception as e:
            logger.error(f"Erro ao buscar endereço: {str(e)}")
            raise

    @staticmethod
    async def create_address(address_data: dict) -> AddressResponse:
        try:
            address = await AddressRepository.create({
                **address_data,
                "is_active": True
            })

            return AddressResponse(
                address_id=UUID(address["address_id"]),
                supplier_id=UUID(address["supplier_id"]),
                street=address["street"],
                number=address.get("number"),
                complement=address.get("complement"),
                neighborhood=address.get("neighborhood"),
                city=address["city"],
                state=address["state"],
                zip_code=address["zip_code"],
                country=address.get("country", "Brasil"),
                is_active=address.get("is_active", True),
                created_at=address["created_at"],
                updated_at=address["updated_at"]
            )
        except Exception as e:
            logger.error(f"Erro ao criar endereço: {str(e)}")
            raise

    @staticmethod
    async def update_address(address_id: UUID, address_data: dict) -> AddressResponse:
        try:
            if not await AddressRepository.exists(address_id):
                raise InvalidParametersError(f"Endereço não encontrado")
            
            address = await AddressRepository.update(address_id, address_data)

            return AddressResponse(
                address_id=UUID(address["address_id"]),
                supplier_id=UUID(address["supplier_id"]),
                street=address["street"],
                number=address.get("number"),
                complement=address.get("complement"),
                neighborhood=address.get("neighborhood"),
                city=address["city"],
                state=address["state"],
                zip_code=address["zip_code"],
                country=address.get("country", "Brasil"),
                is_active=address.get("is_active", True),
                created_at=address["created_at"],
                updated_at=address["updated_at"]
            )
        except Exception as e:
            logger.error(f"Erro ao atualizar endereço: {str(e)}")
            raise

    @staticmethod
    async def delete_address(address_id: UUID) -> dict:
        try:
            if not await AddressRepository.exists(address_id):
                raise InvalidParametersError("Endereço não encontrado")
            
            await AddressRepository.delete(address_id)
            return {"message": "Endereço deletado com sucesso"}
        except Exception as e:
            logger.error(f"Erro ao deletar endereço: {str(e)}")
            raise