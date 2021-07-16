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
html_theme = "furo"
