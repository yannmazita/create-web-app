import logging
from typing import Generic, TypeVar
from uuid import UUID

from sqlalchemy import (
    func,
    select,
)
from sqlalchemy.exc import (
    IntegrityError,
    MultipleResultsFound,
    NoResultFound,
    SQLAlchemyError,
)
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Base
from app.schemas import Base as BaseSchema

logger = logging.getLogger(__name__)
Model = TypeVar("Model", bound=Base)
Schema = TypeVar("Schema", bound=BaseSchema)


class DatabaseRepository(Generic[Model, Schema]):
    """
    Repository for performing database queries.

    Attributes:
        model: The model to be used for queries.
        session: The database session to be used for queries.
    """

    def __init__(self, model: type[Model], session: AsyncSession) -> None:
        self.model: type[Model] = model
        self.session: AsyncSession = session

    async def create(self, data: type[Schema]) -> Model:
        """
        Create a new instance of the model in the database.

        Args:
            data: The data to be used for creating the instance.
        Returns:
            The created instance.
        """
        try:
            logger.debug(f"Creating {self.model.__name__}")
            instance = self.model(**data.model_dump())
            logger.debug(f"Adding {self.model.__name__} to session")
            self.session.add(instance)
            logger.debug("Committing session")
            await self.session.commit()
            logger.debug(f"Refreshing {self.model.__name__} instance")
            await self.session.refresh(instance)
            logger.info(f"Created {self.model.__name__}")
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

    async def get_by_attribute(
        self, value: UUID | str, column: str = "id", with_for_update: bool = False
    ) -> Model:
        """
        Get an instance of the model from the database.

        Args:
            value: The value of the attribute to be used for filtering.
            column: The column to be used for filtering.
            with_for_update:
        Returns:
            The retrieved instance.
        """
        try:
            logger.debug(f"Getting {self.model.__name__} with {column} {value}")
            query = select(self.model).where(getattr(self.model, column) == value)

            if with_for_update:
                logger.debug(f"Locking column {id}")
                query.with_for_update()

            response = await self.session.execute(query)
            instance = response.scalar_one()
            logger.info(f"Got {self.model.__name__} with {column} {value}")
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

    async def update_by_attribute(
        self, data: type[Schema], value: UUID | str, column: str = "id"
    ) -> Model:
        """
        Update an instance of the model in the database.

        Args:
            data: The data to be used for updating the instance.
            value: The value of the attribute to be used for filtering.
            column: The column to be used for filtering.
        Returns:
            The updated instance.
        """
        try:
            logger.debug(f"Updating {self.model.__name__} with {column} {value}")
            instance = await self.get_by_attribute(value, column, with_for_update=True)

            items = data.model_dump(exclude_unset=True).items()
            for key, value in items:
                # if key != "id":
                setattr(instance, key, value)
            logger.debug(f"Adding {self.model.__name__} to session")
            self.session.add(instance)
            logger.debug("Committing session")
            await self.session.commit()
            logger.debug(f"Refreshing {self.model.__name__} instance")
            await self.session.refresh(instance)
            logger.info(f"Updated {self.model.__name__} with {column} {value}")
            return instance
        except MultipleResultsFound as e:
            logger.error("Multiple results found.", exc_info=False)
            raise e
        except NoResultFound as e:
            logger.error("No result found.", exc_info=False)
            raise e
        except IntegrityError as e:
            logger.error("Integrity error occurred.", exc_info=False)
            raise e
        except SQLAlchemyError as e:
            logger.error("SQLAlchemy error occurred.", exc_info=False)
            raise e
        except Exception as e:
            logger.error("Unexpected error occurred.", exc_info=False)
            raise e

    async def delete(self, value: UUID | str, column: str = "id") -> Model:
        """
        Delete an instance of the model from the database.

        Args:
            value: The value of the attribute to be used for filtering.
            column: The column to be used for filtering.
        Returns:
            The deleted instance.
        """
        try:
            logger.debug(f"Deleting {self.model.__name__} with {column} {value}")
            instance = await self.get_by_attribute(value, column)
            logger.debug(f"Deleting {self.model.__name__} from session")
            await self.session.delete(instance)
            logger.debug("Committing session")
            await self.session.commit()
            logger.info(f"Deleted {self.model.__name__} with {column} {value}")
            return instance
        except MultipleResultsFound as e:
            logger.error("Multiple results found.", exc_info=False)
            raise e
        except NoResultFound as e:
            logger.error("No result found.", exc_info=False)
            raise e
        except IntegrityError as e:
            logger.error("Integrity error occurred.", exc_info=False)
            raise e
        except SQLAlchemyError as e:
            logger.error("SQLAlchemy error occurred.", exc_info=False)
            raise e
        except Exception as e:
            logger.error("Unexpected error occurred.", exc_info=False)
            raise e

    async def get_all(self, offset: int = 0, limit: int = 100):
        """
        Get all instances of the model from the database.
        Args:
            offset: The number of instances to skip.
            limit: The maximum number of instances to return.
        Returns:
            The list of instances and the total count.
        """
        try:
            logger.debug(
                f"Fetching {limit} {self.model.__name__} instances from {offset}"
            )
            total_count_query = select(func.count()).select_from(self.model)
            total_count_response = await self.session.execute(total_count_query)
            total_count: int = total_count_response.scalar_one()

            query = select(self.model).offset(offset).limit(limit)
            response = await self.session.execute(query)
            instances = response.scalars().all()
            logger.info(f"Fetched {len(instances)} instances")
            return instances, total_count
        except NoResultFound as e:
            logger.error("No result found", exc_info=False)
            raise e
        except SQLAlchemyError as e:
            logger.error(f"SQLAlchemyError occurred: {e}", exc_info=False)
            raise e
        except Exception as e:
            logger.error(f"Unexpected error occurred: {e}", exc_info=False)
            raise e
