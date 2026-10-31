#!/usr/bin/env sh
set -eu

if ! command -v node >/dev/null 2>&1; then
  echo "Node.js 20 or newer is required: https://nodejs.org/"
  exit 1
fi

if [ ! -f .env ]; then
  cp .env.example .env
  echo "Created .env from .env.example (MOCK_MODE=true)."
fi

if [ ! -d node_modules ]; then
  echo "Installing npm dependencies..."
  npm install
fi

npm start
