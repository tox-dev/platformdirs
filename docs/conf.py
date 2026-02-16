# noqa: INP001
"""Configuration for Sphinx."""

from __future__ import annotations

from datetime import datetime, timezone

from platformdirs.version import __version__

author = "The platformdirs team"
project = "platformdirs"
copyright = "2021, The platformdirs team"  # noqa: A001

release = __version__
version = release
extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.autosectionlabel",
    "sphinx.ext.extlinks",
    "sphinx.ext.viewcode",
    "sphinx.ext.intersphinx",
    "sphinx_autodoc_typehints",
    "sphinx_copybutton",
    "sphinx_design",
    "sphinx_sitemap",
    "sphinxcontrib.mermaid",
    "sphinxext.opengraph",
]
html_theme = "furo"
html_title, html_last_updated_fmt = "platformdirs", datetime.now(tz=timezone.utc).isoformat()
pygments_style, pygments_dark_style = "sphinx", "monokai"
autoclass_content, autodoc_member_order, autodoc_typehints = "class", "bysource", "none"
autodoc_default_options = {
    "member-order": "bysource",
    "undoc-members": True,
    "show-inheritance": True,
}
default_role = "any"
autosectionlabel_prefix_document = True
intersphinx_mapping = {"python": ("https://docs.python.org/3", None)}
extlinks = {
    "issue": ("https://github.com/tox-dev/platformdirs/issues/%s", "issue #%s"),
    "pr": ("https://github.com/tox-dev/platformdirs/issues/%s", "PR #%s"),
    "user": ("https://github.com/%s", "@%s"),
}
copybutton_prompt_text = r">>> |\.\.\. |\$ "
copybutton_prompt_is_regexp = True
html_baseurl = "https://platformdirs.readthedocs.io/en/latest/"
sitemap_url_scheme = "{link}"
ogp_site_url = "https://platformdirs.readthedocs.io/en/latest/"
ogp_site_name = "platformdirs"
ogp_enable_meta_description = True
