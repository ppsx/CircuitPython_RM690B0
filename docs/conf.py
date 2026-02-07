# -*- coding: utf-8 -*-

# SPDX-FileCopyrightText: 2017 Scott Shawcroft, written for Adafruit Industries
#
# SPDX-License-Identifier: MIT

import os
import sys
import datetime

sys.path.insert(0, os.path.abspath(".."))

# -- General configuration ------------------------------------------------

extensions = [
    "sphinx.ext.autodoc",
    "sphinxcontrib.jquery",
    "sphinx.ext.intersphinx",
    "sphinx.ext.napoleon",
    "sphinx.ext.todo",
]

autodoc_mock_imports = ["busdisplay", "qspibus", "displayio"]

autodoc_preserve_defaults = True


intersphinx_mapping = {
    "python": ("https://docs.python.org/3", None),
    "CircuitPython": ("https://docs.circuitpython.org/en/latest/", None),
}

# Show the docstring from both the class and its __init__() method.
autoclass_content = "both"

templates_path = ["_templates"]

source_suffix = ".rst"

# The master toctree document.
master_doc = "index"

# General information about the project.
project = "CircuitPython RM690B0 Library"
creation_year = "2026"
current_year = str(datetime.datetime.now().year)
year_duration = (
    current_year
    if current_year == creation_year
    else creation_year + " - " + current_year
)
copyright = year_duration + " Przemyslaw Patrick Socha"
author = "Przemyslaw Patrick Socha"

# The short X.Y version.
version = "1.0"
# The full version, including alpha/beta/rc tags.
release = "1.0"

language = "en"

exclude_patterns = [
    "_build",
    "Thumbs.db",
    ".DS_Store",
    ".env",
    "CODE_OF_CONDUCT.md",
]

default_role = "any"

add_function_parentheses = True

pygments_style = "sphinx"

todo_include_todos = False

todo_emit_warnings = True

napoleon_numpy_docstring = False

# -- Options for HTML output ----------------------------------------------

html_theme = "sphinx_rtd_theme"

html_static_path = ["_static"]

html_favicon = "_static/favicon.ico"

htmlhelp_basename = "CircuitPython_RM690B0_Librarydoc"

# -- Options for LaTeX output ---------------------------------------------

latex_elements = {}

latex_documents = [
    (
        master_doc,
        "CircuitPython_RM690B0_Library.tex",
        "CircuitPython RM690B0 Library Documentation",
        author,
        "manual",
    ),
]

# -- Options for manual page output ---------------------------------------

man_pages = [
    (
        master_doc,
        "CircuitPython_RM690B0_Library",
        "CircuitPython RM690B0 Library Documentation",
        [author],
        1,
    ),
]

# -- Options for Texinfo output -------------------------------------------

texinfo_documents = [
    (
        master_doc,
        "CircuitPython_RM690B0_Library",
        "CircuitPython RM690B0 Library Documentation",
        author,
        "CircuitPython_RM690B0_Library",
        "CircuitPython displayio driver for RM690B0 AMOLED displays.",
        "Miscellaneous",
    ),
]
