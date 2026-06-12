"""
This package provides tools for analyzing simultaneousness factors in power grid calculations using climate time series data (solar radiation, wind velocity, air temperature, etc.) with a focus on northern Germany.

Main features:
- Data exploration and metadata analysis
- Utilities for retrieving and processing DWD CDC climate data
- Modular structure for easy extension

Submodules:
- meta: Metadata search, filtering, and table utilities
- retrieve_data_from_dwd_cdc: Data retrieval from DWD CDC

See the README for usage examples and development workflow.
"""

from . import meta
from .retrieve_data_from_dwd_cdc import main as retrieve_data

# Define __all__ to control what is exported with 'from simultaneousness_analysis import *'
__all__ = [
    "meta",
    "retrieve_data",
]
