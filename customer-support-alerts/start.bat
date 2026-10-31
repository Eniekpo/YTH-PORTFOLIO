@echo off
where node >nul 2>nul
if errorlevel 1 (
  echo Node.js 20 or newer is required: https://nodejs.org/
  exit /b 1
)

if not exist .env (
  copy .env.example .env >nul
  echo Created .env from .env.example ^(MOCK_MODE=true^).
)

if not exist node_modules (
  echo Installing npm dependencies...
  call npm install
  if errorlevel 1 exit /b 1
)

call npm start
