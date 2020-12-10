"""
Reference : https://alexvanzyl.com/posts/2020-05-24-fastapi-simple-application-structure-from-scratch-part-2/#restructure-project-to-support-auto-migrations
"""

from typing import Any

import inflect
from sqlalchemy.ext.declarative import as_declarative, declared_attr

p = inflect.engine()


@as_declarative()
class Base:
    id: Any
    __name__: str

    # Generate __tablename__ automatically in plural form.
    # i.e 'Post' model will generate table name 'posts'
    @declared_attr
    def __tablename__(cls) -> str:
        return p.plural(cls.__name__.lower())