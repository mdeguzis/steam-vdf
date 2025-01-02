from setuptools import setup, find_packages
from setuptools import setup, Command
from sphinx.cmd.build import build_main


class BuildDoc(Command):
    description = "Build documentation using Sphinx"
    user_options = []

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        build_main(["-b", "html", "docs", "docs/_build"])


cmdclass = {
    "build_sphinx": BuildDoc,
}

name = "steam-vdf"
version = "0.1"
command_options = {
    "build_sphinx": {
        "project": ("setup.py", name),
        "version": ("setup.py", version),
        "release": ("setup.py", version),
        "source_dir": ("setup.py", "docs/source"),
        "build_dir": ("setup.py", "docs/build"),
        "all_files": ("setup.py", True),
    }
}

setup(
    name="steam-vdf",
    version="0.1.0",
    cmdclass={
        "build_sphinx": BuildDoc,
    },
    packages=find_packages(),
    install_requires=[
        "vdf",
    ],
    entry_points={
        "console_scripts": [
            "steam-vdf=steam_vdf.cli:main",  # Updated entry point for cli.py
        ],
    },
    author="Michael DeGuzis",
    author_email="mdeguzis@gmail.com",
    description="Do fun things with Steam VDF data files",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    python_requires=">=3.6",
)
