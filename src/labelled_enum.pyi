# labelled_enum.pyi
import enum

class LabelledEnum(enum.Enum):
    @property
    def label(self) -> str: ...
    @property
    def value(self) -> int: ...
