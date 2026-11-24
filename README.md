# 402CSAD15 — Лабораторна робота №1 (АПКС)

**Студент:** Процак Максим Степанович  
**Група:** КІ-402  
**Варіант:** 15 (JavaScript + npm scripts + Jest)  
**Дисципліна:** Автоматизація проєктування комп'ютерних систем

## Опис проєкту

Кросплатформний JavaScript проєкт Hello World, створений за допомогою AI-агента
`build-engineer`. Агент автоматизує весь процес: від ініціалізації репозиторію
до налаштування CI/CD на трьох операційних системах.

## Структура гілок

| Гілка | Вміст |
|-------|-------|
| `develop` | AI-агент з інструкціями (manifest, skills, commands) |
| `feature/lab1` | Реальний JavaScript проєкт (src, tests, CI workflow) |

## Як запустити AI-агента

Детальні інструкції у [`docs/usage.md`](docs/usage.md).

**Коротко:**
1. Відкрий репозиторій у VS Code
2. Відкрий Copilot Chat (`Ctrl+Alt+I`)
3. Напиши `@workspace /init` або завантаж файл `init.prompt.md`

## Як запустити проєкт локально

```bash
# Встановити залежності
npm install

# Запустити Hello World
npm start

# Запустити тести
npm test

# Зібрати виконуваний файл і запустити його
npm run build
./build/hello/hello        # Windows: buildhellohello.cmd
```

## Документація

- [Архітектура агента](docs/architecture.md)
- [Інструкція запуску](docs/usage.md)
- [Журнал роботи з AI](docs/ai-log.md)

## CI/CD

GitHub Actions автоматично запускає збірку і тести при кожному push до `develop`.

[![CI](https://github.com/masanyk/402CSAD15/actions/workflows/ci.yml/badge.svg)](https://github.com/masanyk/402CSAD15/actions/workflows/ci.yml)

Перевіряються три операційні системи:
- ✅ Ubuntu (Linux)
- ✅ Windows
- ✅ macOS
