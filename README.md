# Steam VDF Tool

A command-line utility for managing Steam library data, non-Steam game shortcuts, and analyzing Steam storage usage.

## Features

- Display Steam library information and user accounts
- List and manage non-Steam game shortcuts
- Analyze storage usage of Steam and non-Steam directories
- Export VDF files to JSON format (for valid types)
- Binary VDF file support
- Restart Steam service
- Analyze storage of Steam and Non-Steam games

## Installation

```
pip install steam-vdf
```

## Usage

```
steam-vdf --help
```

Some commands (such as info), have additional help information:
```
steam-vdf info --help
```

## Development

### Install


Install a local version with:
```
# Install using pipenv (recommended)
pipenv install --dev
pipenv shell
```

### Build docs
```
pipenv run python setup.py build_sphinx
```

### Distribute

```
rm -rf dist/*
python3 -m build
twine check dist/*
twine upload dist/*
```

https://packaging.python.org/en/latest/tutorials/packaging-projects/
