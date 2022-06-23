"""A package for building reactive web applications."""

__version__ = "0.2.0.9008"

from ._shinyenv import is_pyodide as _is_pyodide

# User-facing subpackages that should be available on `from shiny import *`
from . import reactive
from . import render
from .session import *
from . import ui

# Private submodules that have some user-facing functionality
from ._app import App
from ._decorators import event
from ._modules import Module
from ._validation import req
from ._deprecated import *

if _is_pyodide:
    # In pyodide, avoid importing _main because it imports packages that aren't
    # available.
    run_app = None
else:
    from ._main import run_app


# N.B.: we intentionally don't import 'developer-facing' submodules (e.g.,
# html_dependencies) so that they aren't super visible when you `import shiny`, but
# developers who know what they're doing can import them directly.


__all__ = (
    # public sub-packages
    "reactive",
    "render",
    "session",
    "ui",
    # _app.py
    "App",
    # _decorators.py
    "event",
    # _main.py
    "run_app",
    # _modules.py
    "Module",
    # _session.py
    "Session",
    "Inputs",
    "Outputs",
    # _validation.py
    "req",
    # _deprecated.py
    "render_text",
    "render_plot",
    "render_image",
    "render_ui",
)
