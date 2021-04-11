"""Parent Module for Cogs."""
# This is required for the dynamic import chain to work.
import os
from os.path import dirname, basename


__all__ = [basename(f)[:-3] for f in os.listdir(dirname(__file__)) if f[-3:] == ".py" and not f.endswith("__init__.py")]

