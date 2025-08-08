from __future__ import annotations

"""SQLAlchemy models package.

This file turns the *models* directory into a proper Python package so that
`import clean_backend.models` works.  We expose the shared ``Base`` instance
from `clean_backend.database` and eagerly import individual model modules so
that their table metadata is registered with SQLAlchemy at import-time.
"""

from ..database import Base  # noqa: F401 – make Base re-exported at package level

# Import all model modules here so that they are discovered by Alembic / Base.metadata.
# Keep the imports **at the bottom** to avoid circular-import issues during initialisation.
from . import crypto  # noqa: F401  # pylint: disable=unused-import 
from . import velafi_order  # noqa: F401  # ensure VelafiOrder is registered

# ---------------------------------------------------------------------------
# Legacy module support – until all code moves into the *models* package, we
# dynamically load the older `clean_backend/models.py` file (sibling to this
# package) and re-export its attributes here so imports continue to work.
# ---------------------------------------------------------------------------

import importlib.util as _importlib_util
from types import ModuleType as _ModuleType
from pathlib import Path as _Path

_legacy_path = (_Path(__file__).resolve().parent.parent / "models.py").as_posix()

if _Path(_legacy_path).is_file():
    _spec = _importlib_util.spec_from_file_location("clean_backend._legacy_models", _legacy_path)
    if _spec and _spec.loader:
        _legacy_mod = _importlib_util.module_from_spec(_spec)  # type: _ModuleType
        _spec.loader.exec_module(_legacy_mod)  # type: ignore[arg-type]
        # Re-export every public symbol (no leading underscore) to this package
        globals().update({k: v for k, v in _legacy_mod.__dict__.items() if not k.startswith("_")})
        # Also register the module under the canonical name so `import clean_backend.models`
        # will see attributes set both in the package and the legacy module.
        import sys as _sys
        _sys.modules["clean_backend.models._legacy"] = _legacy_mod
        # Clean-up helper vars
        del _spec, _legacy_mod, _importlib_util, _ModuleType, _Path, _sys 



"""

from __future__ import annotations

"""SQLAlchemy models package.

This file turns the *models* directory into a proper Python package so that
`import clean_backend.models` works.  We expose the shared ``Base`` instance
from `clean_backend.database` and eagerly import individual model modules so
that their table metadata is registered with SQLAlchemy at import-time.
"""

# ---------------------------------------------------------------------------
# Legacy module support – until all code moves into the *models* package, we
# dynamically load the older `clean_backend/models.py` file (sibling to this
# package) and re-export its attributes here so imports continue to work.
# ---------------------------------------------------------------------------
import importlib.util as _importlib_util
from pathlib import Path as _Path
from types import ModuleType as _ModuleType

from VelaFi import (
    models as _velafi_models,  # noqa: F401 – ensure VelaFi tables registered
)

from ..database import Base  # noqa: F401 – make Base re-exported at package level

# Import all model modules here so that they are discovered by Alembic / Base.metadata.
# Keep the imports **at the bottom** to avoid circular-import issues during initialisation.
from . import crypto  # noqa: F401  # pylint: disable=unused-import 
from . import velafi_order  # noqa: F401  # ensure VelafiOrder is registered

_legacy_path = (_Path(__file__).resolve().parent.parent / "models.py").as_posix()

if _Path(_legacy_path).is_file():
    _spec = _importlib_util.spec_from_file_location("clean_backend._legacy_models", _legacy_path)
    if _spec and _spec.loader:
        _legacy_mod = _importlib_util.module_from_spec(_spec)  # type: _ModuleType
        _spec.loader.exec_module(_legacy_mod)  # type: ignore[arg-type]
        # Re-export every public symbol (no leading underscore) to this package
        globals().update({k: v for k, v in _legacy_mod.__dict__.items() if not k.startswith("_")})
        # Also register the module under the canonical name so `import clean_backend.models`
        # will see attributes set both in the package and the legacy module.
        import sys as _sys
        _sys.modules["clean_backend.models._legacy"] = _legacy_mod
        # Clean-up helper vars
        del _spec, _legacy_mod, _importlib_util, _ModuleType, _Path, _sys 
"""