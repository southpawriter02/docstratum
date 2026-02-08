"""Root conftest for DocStratum test suite.

Provides compatibility shims for running tests on Python 3.10 when the
project targets Python 3.11+. This file is loaded by pytest before any
test imports, ensuring the StrEnum backport is available.
"""

import sys

# ── Python 3.10 StrEnum compatibility shim ────────────────────────────
# The project targets Python >=3.11 which includes StrEnum in the stdlib.
# When running on Python 3.10 (e.g., in CI environments or sandboxes that
# don't have 3.11 available), we inject the `strenum` backport into the
# `enum` module so that `from enum import StrEnum` works transparently.

if sys.version_info < (3, 11):
    try:
        import strenum
        import enum

        enum.StrEnum = strenum.StrEnum  # type: ignore[attr-defined]
    except ImportError:
        pass  # If strenum isn't installed, let the natural ImportError propagate
