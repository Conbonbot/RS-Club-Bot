
"""Parent module for CreateDatabaseEvent."""
import abc

# This is required for the dynamic import chain to work.
import os
from os.path import dirname, basename
__all__ = [basename(f)[:-3] for f in os.listdir(dirname(__file__)) if f[-3:] == ".py" and not f.endswith("__init__.py")]

import routines


class CreateDatabaseEvent(routines.Routine):
    """Parent class for CreateDatabaseEvent. Used for dynamic loading."""

    @abc.abstractmethod
    def actions(self):
        """Abstract method for actions."""


# This has to go here to ensure the dynamic import chain works.
from routines.create_database import *
