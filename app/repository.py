import logging
from typing import Generic, TypeVar
from uuid import UUID

from sqlalchemy import (
    BooleanClauseList,
    func,
    select,
)
from sqlalchemy import (
    delete as sa_delete,
)
from sqlalchemy import (
    update as sa_update,
)
from sqlalchemy.exc import (
    IntegrityError,
    MultipleResultsFound,
    NoResultFound,
    SQLAlchemyError,
)
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Base

logger = logging.getLogger(__name__)
Model = TypeVar("Model", bound=Base)


class DatabaseRepository(Generic[Model]):
    """
    Repository for performing database queries.

    Attributes:
        model: The model to be used for queries.
        session: The database session to be used for queries.
    """

    def __init__(self, model: type[Model], session: AsyncSession) -> None:
        self.model: type[Model] = model
        self.session: AsyncSession = session

    async def create(self, data: dict) -> Model:
        """
        Create a new instance of the model in the database.

        Args:
            data: The data to be used for creating the instance.
        Returns:
            The created instance.
        """
        try:
            logger.debug(f"Creating {self.model.__name__}")
            instance = self.model(**data)

            logger.debug(f"Adding {self.model.__name__} to session")
            self.session.add(instance)
            logger.debug("Committing session")
            await self.session.commit()
            logger.debug(f"Refreshing {self.model.__name__} instance")
            await self.session.refresh(instance)
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

    async def get(self, id: UUID) -> Model:
        """
        Get an instance of the model from the database.

        Args:
            id: The id of the instance to be retrieved.
        Returns:
            The retrieved instance.
        """
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

    async def update(self, id: UUID, data: dict) -> Model:
        """
        Update an instance of the model in the database.

        Args:
            id: The id of the instance to be updated.
            data: The data to be used for updating the instance.
        Returns:
            The updated instance.
        """
        try:
            logger.debug(f"Updating {self.model.__name__} with id {id}")
            instance = await self.get(id)
            for key, value in data.items():
                if key != "id":
                    setattr(instance, key, value)
            logger.debug(f"Adding {self.model.__name__} to session")
            self.session.add(instance)
            logger.debug("Committing session")
            await self.session.commit()
            logger.debug(f"Refreshing {self.model.__name__} instance")
            await self.session.refresh(instance)
            logger.info(f"Updated {self.model.__name__} with id {id}")
            return instance
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

    async def delete(self, id: UUID) -> Model:
        try:
            logger.debug(f"Deleting {self.model.__name__} with id {id}")
            instance = await self.get(id)
            logger.debug(f"Deleting {self.model.__name__} from session")
            await self.session.delete(instance)
            logger.debug("Committing session")
            await self.session.commit()
            logger.info(f"Deleted {self.model.__name__} with id {id}")
            return instance
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

    async def _filter_and_perform(
        self,
        operation,
        expressions: list[BooleanClauseList] | None = None,
        id: UUID | None = None,
        data: dict | None = None,
    ) -> None:
        """
        Filter instances of the model in the database and perform an operation.

        This method is a helper method for performing operations on filtered instances.
        Args:
            operation: The operation to be performed.
            expressions: Optional list of filter expressions.
            id: Optional id of the instance to be filtered.
            data: Optional dictionary containing data for updating instances.
        """
        query = operation(self.model)
        if expressions:
            query = query.where(*expressions)
        if id:
            query = query.where(self.model.id == id)
        if data:
            query = query.values(**data)

        await self.session.execute(query)
        await self.session.commit()

    async def filter(
        self,
        *expressions: BooleanClauseList,
        update_data: dict | None = None,
        delete: bool = False,
    ):
        """
        Filter instances of the model in the database.

        Args:
            *expressions: The filter expressions.
            update_data: Optional dictionary containing data for updating instances.
            delete: Boolean flag to indicate if the matched instances should be deleted.
        Returns:
            The list of matched instances.
        """
        query = select(self.model)
        if expressions:
            query = query.where(*expressions)

        response = await self.session.execute(query)
        instances = response.scalars().all()

        if update_data:
            await self._filter_and_perform(
                sa_update, expressions=list(expressions), data=update_data
            )

        if delete:
            await self._filter_and_perform(sa_delete, expressions=list(expressions))

        return instances
