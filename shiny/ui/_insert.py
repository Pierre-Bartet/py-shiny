__all__ = ("insert_ui", "remove_ui")

from typing import Literal

from htmltools import TagChild

from .._deprecated import _session_param_docs as _session_param
from .._docstring import add_example, doc_format
from ..session import require_active_session
from ..types import MISSING, MISSING_TYPE


@add_example()
@doc_format(session_param=_session_param)
def insert_ui(
    ui: TagChild,
    selector: str,
    where: Literal["beforeBegin", "afterBegin", "beforeEnd", "afterEnd"] = "beforeEnd",
    multiple: bool = False,
    immediate: bool = False,
    session: MISSING_TYPE = MISSING,
) -> None:
    """
    Insert UI objects.

    Parameters
    ----------
    ui
        The UI object you want to insert. This can be anything that you usually put
        inside your app's UI function. If you're inserting multiple elements in one
        call, make sure to wrap them in either a :func:`~htmltools.TagList` or a
        :func:`~shiny.ui.tags.div` (the latter option has the advantage that you can
        give it an id to make it easier to reference or remove it later on). If you want
        to insert raw HTML, use :class:`~shiny.ui.HTML`.
    selector
        A string that is accepted by jQuery's selector (i.e. the string ``s`` to be
        placed in a ``$(s)`` jQuery call) which determines the element(s) relative to
        which you want to insert your UI object.
    where
        Where your UI object should go relative to the selector: "beforeBegin":
        before the selector element itself; "beforeEnd": just inside the selector
        element, after its last child (default); "afterEnd": after the selector
        element itself. Adapted from
        https://developer.mozilla.org/en-US/docs/Web/API/Element/insertAdjacentHTML.
    multiple
        In case your selector matches more than one element, ``multiple``
        determines whether Shiny should insert the UI object relative to all
        matched elements or just relative to the first matched element (default).
    immediate
        Whether the UI object should be immediately inserted or removed, or whether
        Shiny should wait until all outputs have been updated and all effects have been
        run (default).
    {session_param}

    Note
    ----
    This function allows you to dynamically add arbitrary UI into your app, whenever you
    want, as many times as you want. Unlike :class:`~shiny.render.ui`, the UI generated
    with `insert_ui` is persistent: once it's created, it stays there until removed by
    :func:`~shiny.ui.remove_ui`. Each new call to `insert_ui` creates more UI objects, in addition
    to the ones already there (all independent from one another). To update a part of
    the UI (ex: an input object), you must use the appropriate render function or a
    customized reactive function.

    See Also
    --------
    * :func:`~shiny.ui.remove_ui`
    * :class:`~shiny.render.ui`
    """

    active_session = require_active_session(session)

    def callback() -> None:
        active_session._send_insert_ui(
            selector=selector,
            multiple=multiple,
            where=where,
            content=active_session._process_ui(ui),
        )

    if immediate:
        callback()
    else:
        active_session.on_flushed(callback, once=True)


@add_example()
@doc_format(session_param=_session_param)
def remove_ui(
    selector: str,
    multiple: bool = False,
    immediate: bool = False,
    session: MISSING_TYPE = MISSING,
) -> None:
    """
    Remove UI objects.

    Parameters
    ----------
    selector
        A string that is accepted by jQuery's selector (i.e. the string ``x`` to be
        placed in a ``$(x)`` jQuery call), which determines the element(s) to remove. If
        you want to remove a Shiny input or output, note that many of these are wrapped
        in ``<div>``s, so you may need to use a somewhat complex selector — see the
        Examples below. (Alternatively, you could also wrap the inputs/outputs that you
        want to be able to remove easily in a ``<div>`` with an id.)
    multiple
        In case your selector matches more than one element, ``multiple`` determines
        whether Shiny should insert the UI object relative to all matched elements
        or just relative to the first matched element (default).
    immediate
        Whether the UI object should be immediately inserted or removed, or whether
        Shiny should wait until all outputs have been updated and all effects have been
        run (default).
    {session_param}

    See Also
    --------
    * :func:`~shiny.ui.insert_ui`
    * :class:`~shiny.render.ui`
    """

    active_session = require_active_session(session)

    def callback():
        active_session._send_remove_ui(selector=selector, multiple=multiple)

    if immediate:
        callback()
    else:
        active_session.on_flushed(callback, once=True)
