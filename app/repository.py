import logging
from uuid import UUID
from typing import Generic, TypeVar

from sqlalchemy import BinaryExpression, select
from sqlalchemy.exc import (
    IntegrityError,
    MultipleResultsFound,
    NoResultFound,
    SQLAlchemyError,
)
from sqlalchemy.ext.asyncio import AsyncSession

from models import Base

logger = logging.getLogger(__name__)
Model = TypeVar("Model", bound=Base)


class DatabaseRepository(Generic[Model]):
    """Repository for performing database queries."""

    def __init__(self, model: type[Model], session: AsyncSession) -> None:
        self.model: type[Model] = model
        self.session: AsyncSession = session

    async def create(self, data: dict) -> Model:
        try:
            logger.debug(f"Creating {self.model.__name__}")
            instance = self.model(**data)

            self.session.add(instance)
            await self.session.commit()
            logger.info(f"Created {self.model.__name__} with id {instance.id}")
            return instance
        except IntegrityError as e:
            logger.error("Integrity error occurred.", exc_info=False)
            raise e
        except SQLAlchemyError as e:
            logger.error("SQLAlchemy error occurred.", exc_info=False)
            raise e
        except Exception as e:
            logger.error("Unexpected error occurred.", exc_info=False)
            raise e

    async def get(self, id: UUID) -> Model | None:
        try:
            logger.debug(f"Getting {self.model.__name__} with id {id}")
            query = select(self.model).where(self.model.id == id)
            response = await self.session.execute(query)
            instance = response.scalar_one()
            logger.info(f"Got {self.model.__name__} with id {id}")
            return instance
        except MultipleResultsFound as e:
            logger.error("Multiple results found.", exc_info=False)
            raise e
        except NoResultFound as e:
            logger.error("No result found.", exc_info=False)
            raise e
        except SQLAlchemyError as e:
            logger.error("SQLAlchemy error occurred.", exc_info=False)
            raise e
        except Exception as e:
            logger.error("Unexpected error occurred.", exc_info=False)
            raise e

    async def filter(
        self,
        *expressions: BinaryExpression,
    ) -> list[Model]:
        query = select(self.model)
        if expressions:
            query = query.where(*expressions)
        return list(await self.session.scalars(query))
