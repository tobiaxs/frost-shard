from typing import Generic, Protocol, TypeVar

from pydantic import BaseModel

ReadModel = TypeVar("ReadModel", bound=BaseModel)
CreateModel = TypeVar("CreateModel", bound=BaseModel, contravariant=True)


class Repository(Protocol, Generic[ReadModel, CreateModel]):
    """Abstraction over the idea of persistent storage.

    Interface class for all the concrete repository implementations.
    """

    def create(self, data: CreateModel) -> ReadModel:
        """Create a new object.

        Args:
            data (CreateModel): Data to create the object with.
        """
        ...

    def collect(self) -> list[ReadModel]:
        """Collect all objects."""
        ...
