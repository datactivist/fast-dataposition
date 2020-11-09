# labelled_enum.py
# author : selimb
# source : https://github.com/samuelcolvin/pydantic/issues/1401#issuecomment-670223242
"""
A special Enum that plays well with ``pydantic`` and ``mypy``, while allowing human-readable
labels similarly to ``django.db.models.enums.Choices``.
"""
from typing import TypeVar, Type
import enum

T = TypeVar("T")


class LabelledEnum(enum.Enum):
    """Enum with labels. Assumes the value is integer and label is string."""

    def __new__(cls: Type[T], value: int, label: str) -> T:
        obj = object.__new__(cls)
        obj._value_ = value
        obj.label = label
        return obj
