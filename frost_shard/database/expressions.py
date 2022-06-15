from typing import Any

from sqlalchemy.sql.elements import BinaryExpression
from sqlmodel import SQLModel


def get_expression(
    model: type[SQLModel],
    field: str,
    value: Any,
) -> BinaryExpression:
    """Create a single SQLAlchemy expression from a field and value.

    Args:
        model (type[SQLModel]): Model to create the expression for.
        field (str): Field to create the expression for.
        value (Any): Field value.

    Raises:
        NotImplementedError: If the lookup type is not implemented.

    Returns:
        BinaryExpression: SQLAlchemy binary expression.
    """
    field_and_operator = field.split("__")
    if len(field_and_operator) == 1:
        return getattr(model, field) == value

    field, operator = field_and_operator
    match operator:
        case "gt":
            return getattr(model, field) > value
        case "lt":
            return getattr(model, field) < value
        case _:
            raise NotImplementedError(f"Unsupported operator: {operator}")


def create_expressions(
    model: type[SQLModel],
    filters: dict,
) -> list[BinaryExpression]:
    """Create a list of SQLAlchemy expressions from a dictionary of filters.

    Args:
        model (type[SQLModel]): Model to create the expressions for.
        filters (dict): Dictionary of filters.

    Returns:
        list[BinaryExpression]: List of SQLAlchemy expressions.
    """
    return [
        get_expression(model, field, value) for field, value in filters.items()
    ]
