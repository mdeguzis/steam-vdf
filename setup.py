from setuptools import setup, find_packages

setup(
    name="steam-vdf",
    version="0.1.0",
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
