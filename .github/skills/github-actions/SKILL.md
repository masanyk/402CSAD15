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

### 1. Створити `ci.sh` (Linux/macOS):
```bash
#!/bin/bash
set -e
npm install
npm test
```

### 2. Створити `ci.bat` (Windows):
```bat
@echo off
call npm install
if %ERRORLEVEL% neq 0 exit /b %ERRORLEVEL%
call npm test
if %ERRORLEVEL% neq 0 exit /b %ERRORLEVEL%
```

### 3. Створити `.github/workflows/ci.yml`:
```yaml
name: CI

on:
  push:
    branches: [develop, master, main]
  pull_request:
    branches: [develop, master, main]

jobs:
  build-and-test:
    name: Build & Test (${{ matrix.os }})
    runs-on: ${{ matrix.os }}
    strategy:
      matrix:
        os: [ubuntu-latest, windows-latest, macos-latest]
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: '20'
      - name: Run CI script (Linux/macOS)
        if: runner.os != 'Windows'
        run: bash ci.sh
      - name: Run CI script (Windows)
        if: runner.os == 'Windows'
        run: ci.bat
      - name: Upload test results
        if: always()
        uses: actions/upload-artifact@v4
        with:
          name: test-results-${{ matrix.os }}
          path: |
            coverage/
          if-no-files-found: ignore
```

## Перевірка результату
- `ci.yml` існує та містить усі три ОС у матриці
- `ci.sh` є виконуваним (`chmod +x ci.sh` на Linux/macOS)
- Workflow запускається при push до `develop`

## Типовий сценарій помилки
**Помилка:** `ci.sh: Permission denied` на Ubuntu
**Причина:** Файл не має прав на виконання у репозиторії.
**Дія:** Додати `.gitattributes` з `ci.sh text eol=lf` або встановити права перед комітом.
