import matplotlib
import matplotlib.pyplot as plt

from ..util import *
from .diagram import Diagram
from . import styles

class CMD(Diagram):
    def __init__(self, axes, orig=None):
        super().__init__(axes, orig=orig)

        if not isinstance(orig, CMD):
            pass
        else:
            pass

        self._validate()

    def _validate(self):
        pass

    def can_plot(self, catalog, observed=None):
        return catalog.has_diagram_values(self.axes, observed=observed)

