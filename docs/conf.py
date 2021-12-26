from __future__ import annotations

from platformdirs.version import __version__

author = "The platformdirs team"
project = "platformdirs"
copyright = "2021, The platformdirs team"

release = __version__
version = release
extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.autosectionlabel",
    "sphinx.ext.viewcode",
    "sphinx.ext.intersphinx",
    # "sphinx_autodoc_typehints",
]
html_theme = "furo"

autodoc_default_options = {
    "member-order": "bysource",
    "undoc-members": True,
}
default_role = "any"
autodoc_typehints = "signature"
intersphinx_mapping = {"python": ("https://docs.python.org/3", None)}
