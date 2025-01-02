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
# Clone the repository
git clone https://github.com/yourusername/steam-vdf.git
cd steam-vdf

# Install using pipenv (recommended)
pipenv install
pipenv shell

# Or install using pip
pip install -e .
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
```
# Install using pipenv (recommended)
pipenv install --dev
pipenv shell
```

### Build docs
```
pipenv run python setup.py build_sphinx
```
