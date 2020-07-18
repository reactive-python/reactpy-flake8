from pkg_resources import (
    get_distribution as _get_distribution,
    DistributionNotFound as _DistributionNotFound,
)


try:
    __version__ = _get_distribution(__name__).version
except _DistributionNotFound:  # pragma: no cover
    # package is not installed
    __version__ = "0.0.0"


class Plugin:

    name = __name__
    version = __version__
    options = None

    def __init__(self, tree):
        self._tree = tree

    def run(self):
        return [(7, 39, "hooks cannot be used in conditionals", type(self))]
