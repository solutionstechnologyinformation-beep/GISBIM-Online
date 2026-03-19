"""Backend package for Mini-QGIS-Online.

This module exists so that backend submodules can be imported with
``from backend import spatial`` etc.  It also prevents namespace errors if
scripts are executed from the project root.
"""

# make imports available at package level if desired
from .spatial import convert
from .upload import process_upload, allowed_file
from .raster import info

