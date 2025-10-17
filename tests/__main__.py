import sys

import pytest


def main() -> int:
    """Run test suite via `python -m tests`."""
    return pytest.main()


if __name__ == "__main__":
    raise SystemExit(main())
