import sphinx_rtd_theme

from platformdirs.version import __version__

author = "The platformdirs team"
project = "platformdirs"
copyright = "2021, The platformdirs team"

release = __version__
extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.autosectionlabel",
    "sphinx.ext.viewcode",
]
html_theme = "sphinx_rtd_theme"
html_theme_path = [sphinx_rtd_theme.get_html_theme_path()]
html_theme_options = {
    "canonical_url": "https://platformdirs.readthedocs.io/",
    "display_version": True,
    "prev_next_buttons_location": "bottom",
    "sticky_navigation": True,
}
