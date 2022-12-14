# -*- coding: utf-8 -*-
# code generated by Prisma. DO NOT EDIT.
# pyright: reportUnusedImport=false
# fmt: off

# global imports for type checking
from builtins import bool as _bool
from builtins import int as _int
from builtins import float as _float
from builtins import str as _str
import sys
import decimal
import datetime
from typing import (
    TYPE_CHECKING,
    Optional,
    Iterable,
    Iterator,
    Callable,
    Generic,
    Mapping,
    Tuple,
    Union,
    List,
    Dict,
    Type,
    Any,
    Set,
    overload,
    cast,
)
from typing_extensions import TypedDict, Literal


LiteralString = str
# -- template engine/abstract.py.jinja --
from abc import ABC, abstractmethod
from ..types import DatasourceOverride
from .._compat import get_running_loop

__all__ = (
    'AbstractEngine',
)

class AbstractEngine(ABC):
    dml: str

    def stop(self) -> None:
        """Wrapper for synchronously calling close() and aclose()"""
        self.close()
        try:
            loop = get_running_loop()
        except RuntimeError:
            # no event loop in the current thread, we cannot cleanup asynchronously
            return
        else:
            if not loop.is_closed():
                loop.create_task(self.aclose())

    @abstractmethod
    def close(self) -> None:
        """Synchronous method for closing the engine, useful if the underlying engine uses a subprocess"""
        ...

    @abstractmethod
    async def aclose(self) -> None:
        """Asynchronous method for closing the engine, only used if an
        asynchronous client is generated.
        """
        ...

    @abstractmethod
    async def connect(
        self,
        timeout: int = 10,
        datasources: Optional[List[DatasourceOverride]] = None,
    ) -> None:
        """Connect to the engine"""
        ...

    @abstractmethod
    async def query(self, content: str) -> Any:
        """Execute a GraphQL query.

        This method expects a JSON object matching this structure:

        {
            'variables': {},
            'operation_name': str,
            'query': str,
        }
        """
        ...