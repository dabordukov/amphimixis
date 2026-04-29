"""Sphinx configuration for the Amphimixis documentation."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

project = "Amphimixis"
author = "Amphimixis contributors"
copyright = "2026, Amphimixis contributors"

extensions = [
    "myst_parser",
    "sphinx.ext.autodoc",
    "sphinx.ext.autosummary",
    "sphinx.ext.intersphinx",
]

source_suffix = {
    ".rst": "restructuredtext",
    ".md": "markdown",
    ".yml": "markdown",
}

root_doc = "index"

autosummary_generate = True
autosummary_imported_members = False
autodoc_member_order = "bysource"
autodoc_default_options = {
    "members": True,
    "undoc-members": False,
    "show-inheritance": True,
}
add_module_names = False
autodoc_typehints = "both"
autodoc_preserve_defaults = True
python_use_unqualified_type_names = True

intersphinx_mapping = {
    "python": ("https://docs.python.org/3.12", None),
}

myst_enable_extensions = [
    "colon_fence",
]

html_theme = "furo"

html_title = "Amphimixis"
html_short_title = "Amphimixis"
html_baseurl = "https://amphimixis.org/"

templates_path = ["_templates"]
