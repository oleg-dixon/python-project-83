### Hexlet tests and linter status:
[![Actions Status](https://github.com/oleg-dixon/python-project-83/actions/workflows/hexlet-check.yml/badge.svg)](https://github.com/oleg-dixon/python-project-83/actions) [![Python CI](https://github.com/oleg-dixon/python-project-83/actions/workflows/pyci.yml/badge.svg)](https://github.com/oleg-dixon/python-project-83/actions/workflows/pyci.yml)

# Page Analyzer
[Page Analyzer](https://python-project-83-q1kp.onrender.com) is a site that analyzes the specified pages for SEO suitability.

## Access
Application is deployed to [render.com](https://render.com/)
[Page Analyzer](https://python-project-83-q1kp.onrender.com)

## Requirements
Python 3.12+

## Local Installation
### Clone repository
```bash
git clone https://github.com/oleg-dixon/python-project-83.git
cd python-project-83
make install # Install dependencies
make build # Buld package
```

### Install uv
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
source $HOME/.local/bin/env
```

### Install application
```bash
make install
```

### Put secrets to .env file
```
echo SECRET_KEY="{flask_secret_key}"
echo DATABASE_URL="postgresql://{user}:{password}@127.0.0.1:5432/sites"
```

### Start development application
```
make dev
```