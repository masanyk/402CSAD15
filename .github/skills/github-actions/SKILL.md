---
name: github-actions
description: Створює CI workflow для GitHub Actions з матрицею трьох операційних систем.
applies_when: Проєкт готовий локально і потрібно налаштувати автоматичну перевірку на GitHub.
---

# Skill: github-actions

## Призначення
Створити `.github/workflows/ci.yml` та скрипти `ci.sh` / `ci.bat`, які
автоматично збирають та тестують проєкт на Ubuntu, Windows і macOS.

## Вхідні дані
| Параметр | Тип | Опис |
|----------|-----|------|
| `node_version` | string | Версія Node.js (наприклад, `"20"`) |
| `triggers` | array | Гілки, при push/PR до яких запускається CI |

## Очікуваний результат
```
.github/
  workflows/
    ci.yml         ← workflow з matrix: ubuntu, windows, macos
ci.sh              ← скрипт для Linux/macOS
ci.bat             ← скрипт для Windows
```

## Важливе правило
`ci.yml` не повинен містити прямих команд (`npm install`, `npm test`).
Натомість він викликає лише `ci.sh` або `ci.bat` залежно від ОС.
Саме ці скрипти виконують встановлення залежностей, складання і тестування.

## Дії skill

Скрипти виконують повний цикл: `npm ci` → `npm run build` (створює виконуваний
файл `build/hello/hello` / `hello.cmd`) → smoke-тест запуску `hello` →
`npm run test:coverage`. Будь-яка помилка зупиняє скрипт з ненульовим кодом.

### 1. Створити `ci.sh` (Linux/macOS), закомітити з правом виконання:
```bash
#!/bin/bash
# CI script for Linux and macOS
# Викликається з GitHub Actions workflow: встановлення → складання → запуск → тести
set -e

echo "=== Installing dependencies ==="
npm ci

echo "=== Building executable ==="
npm run build

echo "=== Smoke test: running build/hello/hello ==="
OUTPUT="$(./build/hello/hello)"
echo "$OUTPUT"
if [ "$OUTPUT" != "Hello, World!" ]; then
  echo "ERROR: unexpected output from hello executable"
  exit 1
fi

echo "=== Running unit tests (with coverage) ==="
npm run test:coverage

echo "=== CI script completed successfully ==="
```

### 2. Створити `ci.bat` (Windows, CRLF):
```bat
@echo off
REM CI script for Windows
REM Called from GitHub Actions workflow: install -> build -> run hello -> unit tests

echo === Installing dependencies ===
call npm ci
if %ERRORLEVEL% neq 0 (
    echo ERROR: npm ci failed
    exit /b %ERRORLEVEL%
)

echo === Building executable ===
call npm run build
if %ERRORLEVEL% neq 0 (
    echo ERROR: build failed
    exit /b %ERRORLEVEL%
)

echo === Smoke test: running build\hello\hello.cmd ===
call build\hello\hello.cmd > hello-output.txt
if %ERRORLEVEL% neq 0 (
    echo ERROR: hello executable failed
    exit /b %ERRORLEVEL%
)
set /p HELLO_OUT=<hello-output.txt
echo %HELLO_OUT%
if not "%HELLO_OUT%"=="Hello, World!" (
    echo ERROR: unexpected output from hello executable
    exit /b 1
)
del hello-output.txt

echo === Running unit tests (with coverage) ===
call npm run test:coverage
if %ERRORLEVEL% neq 0 (
    echo ERROR: npm test failed
    exit /b %ERRORLEVEL%
)

echo === CI script completed successfully ===
```

### 3. Створити `.github/workflows/ci.yml`:
Workflow викладає виконуваний файл як артефакт `hello-<os>` (якщо його немає — job падає)
та звіт покриття `coverage-<os>`.
```yaml
name: CI

on:
  push:
    branches: [develop, master, main, feature/lab1]
  pull_request:
    branches: [develop, master, main]

jobs:
  build-and-test:
    name: Build & Test (${{ matrix.os }})
    runs-on: ${{ matrix.os }}
    strategy:
      fail-fast: false
      matrix:
        os: [ubuntu-latest, windows-latest, macos-latest]

    steps:
      - name: Checkout repository
        uses: actions/checkout@v4

      - name: Setup Node.js
        uses: actions/setup-node@v4
        with:
          node-version: '20'

      - name: Run CI script (Linux / macOS)
        if: runner.os != 'Windows'
        run: bash ci.sh

      - name: Run CI script (Windows)
        if: runner.os == 'Windows'
        shell: cmd
        run: ci.bat

      - name: Upload executable (hello)
        uses: actions/upload-artifact@v4
        with:
          name: hello-${{ matrix.os }}
          path: build/hello/
          if-no-files-found: error

      - name: Upload coverage report
        if: always()
        uses: actions/upload-artifact@v4
        with:
          name: coverage-${{ matrix.os }}
          path: coverage/
          if-no-files-found: warn
```

## Приклад входу
`node_version = "20"`, `triggers = [develop, master, main, feature/lab1]`.

## Перевірка результату
- `ci.yml` існує та містить усі три ОС у матриці
- `ci.sh` є виконуваним (`chmod +x ci.sh` на Linux/macOS)
- Workflow запускається при push і pull_request до `develop` / `master` / `main`
- Локально: `bash ci.sh` (або `ci.bat`) завершується з `CI script completed successfully`
- На GitHub у кожному з 3 jobs є артефакти `hello-<os>` і `coverage-<os>`

## Типовий сценарій помилки
**Помилка:** Windows job падає на кроці `ci.bat` (`is not recognized` / дивні символи)
**Причина:** крок виконується в PowerShell або `ci.bat` містить UTF-8 кирилицю / LF-закінчення.
**Дія:** `shell: cmd` у кроці workflow, лише ASCII у `ci.bat`, `ci.bat text eol=crlf` у `.gitattributes`.

**Помилка:** `ci.sh: Permission denied` на Ubuntu
**Причина:** Файл не має прав на виконання у репозиторії.
**Дія:** Додати `.gitattributes` з `ci.sh text eol=lf` або встановити права перед комітом.
