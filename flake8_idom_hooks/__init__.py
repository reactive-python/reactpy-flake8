from pkg_resources import DistributionNotFound as _DistributionNotFound
from pkg_resources import get_distribution as _get_distribution

try:
    __version__: str = _get_distribution(__name__).version
except _DistributionNotFound:  # pragma: no cover
    # package is not installed
    __version__ = "0.0.0"

from .flake8_plugin import Plugin
from .run import run_checks

plugin = Plugin()

__all__ = ["plugin", "run_checks"]
