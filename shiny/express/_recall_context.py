from __future__ import annotations

import functools
import sys
from types import TracebackType
from typing import Callable, Generic, Mapping, Optional, Type, TypeVar

from htmltools import (
    MetadataNode,
    Tag,
    TagAttrs,
    TagChild,
    Tagifiable,
    TagList,
    wrap_displayhook_handler,
)

from .._typing_extensions import ParamSpec, TypeGuard

P = ParamSpec("P")
R = TypeVar("R")
U = TypeVar("U")


class RecallContextManager(Generic[R]):
    def __init__(
        self,
        fn: Callable[..., R],
        *,
        args: tuple[object, ...] | None = None,
        kwargs: Mapping[str, object] | None = None,
        filter: Callable[[object], bool] | None = None,
    ):
        self.fn = fn

        if args is None:
            args = tuple()
        self.args: list[object] = list(args)

        if kwargs is None:
            kwargs = {}
        self.kwargs: dict[str, object] = dict(kwargs)

        if filter is None:
            filter = lambda x: True
        self.filter = filter

        # Let htmltools.wrap_displayhook_handler decide what to do with objects before
        # we append them.
        self.wrapped_append = wrap_displayhook_handler(self.args.append)

    def __enter__(self) -> None:
        self._prev_displayhook = sys.displayhook
        sys.displayhook = self.displayhook

    def __exit__(
        self,
        exc_type: Optional[Type[BaseException]],
        exc_value: Optional[BaseException],
        traceback: Optional[TracebackType],
    ) -> bool:
        sys.displayhook = self._prev_displayhook
        if exc_type is None:
            res = self.fn(*self.args, **self.kwargs)
            sys.displayhook(res)
        return False

    def displayhook(self, x: object) -> None:
        if isinstance(x, RecallContextManager):
            # This displayhook first checks if x (the child) is a RecallContextManager,
            # in which case it uses `with x` to trigger x.__enter__() and x.__exit__().
            # When x.__exit__() is called, it will invoke x.fn() and then pass the
            # result to this object's (the parent) self.displayhook(), which is this
            # same function, but instead of passing in a RecallContextManager, it will
            # pass in the actual object.
            #
            # In short, this is a way of invoking a re-entrant call to the current
            # function, but instead of passing in a RecallContextManager, it passes in
            # the result from the RecallContextManager.
            with x:
                pass
        elif not self.filter(x):
            pass
        else:
            self.wrapped_append(x)

    def tagify(self) -> Tag | TagList | MetadataNode | str:
        res = self.fn(*self.args, **self.kwargs)

        if callable(getattr(res, "tagify", None)):
            return res.tagify()  # pyright: ignore
        if callable(getattr(res, "_repr_html_", None)):
            return res._repr_html_()  # pyright: ignore

        raise RuntimeError(
            "RecallContextManager was used without `with`. When used this way, the "
            "result must have a .tagify() or ._repr_html_() method, but it does not."
        )


def wrap_recall_context_manager(
    fn: Callable[P, R]
) -> Callable[P, RecallContextManager[R]]:
    @functools.wraps(fn)
    def wrapped_fn(*args: P.args, **kwargs: P.kwargs) -> RecallContextManager[R]:
        return RecallContextManager(fn, args=args, kwargs=kwargs)

    return wrapped_fn


def filter_ui_objects(x: object) -> TypeGuard[TagChild | TagAttrs | None]:
    # Can't seem to figure out how to get typing to work
    valid_types = (  # type: ignore
        dict,
        str,
        Tagifiable,
        Tag,
        TagList,
        MetadataNode,
        str,
        float,
        list,
        tuple,
    )

    return (
        x is None
        or isinstance(x, valid_types)
        # TODO: Should export ReprHtml protocol class from htmltools and add it to
        # valid_types, and remove line below.
        or callable(getattr(x, "_repr_html_", None))
    )


class UiRecallContextManager(RecallContextManager[R]):
    def __init__(
        self,
        fn: Callable[..., R],
        *,
        args: tuple[object, ...] | None = None,
        kwargs: Mapping[str, object] | None = None,
        filter: Callable[[object], bool] | None = filter_ui_objects,
    ):
        super().__init__(fn, args=args, kwargs=kwargs, filter=filter)
