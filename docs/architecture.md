# Архітектура AI-агента build-engineer

## Яку проблему вирішує агент

Ручне налаштування нового JavaScript проєкту з тестами та CI/CD займає багато
часу і схильне до помилок. Агент `build-engineer` автоматизує цей процес:
від створення файлів до перевірки, що все працює на трьох ОС.

## Схема взаємодії компонентів

```
Користувач
    │
    │ /init (orchestrator)
    ▼
┌──────────────────────────────────────────────────┐
│              init.prompt.md                      │
│         (Orchestrator Command)                   │
│                                                  │
│  1. /git-init → git-init.prompt.md              │
│  2. /create-project → create-project.prompt.md  │
│  3. /create-build → create-build.prompt.md      │
│  4. /create-actions → create-actions.prompt.md  │
│  5. /check → check.prompt.md                    │
└──────────────────────────────────────────────────┘
         │              │              │
         ▼              ▼              ▼
  project-scaffold  build-and-test  github-actions
    (SKILL.md)       (SKILL.md)      (SKILL.md)
         │              │              │
         ▼              ▼              ▼
    src/index.js   tests/*.test.js   ci.yml
    src/math.js    package.json      ci.sh / ci.bat
```

## Skills

| Skill | Вхід | Вихід |
|-------|------|-------|
| `project-scaffold` | назва проєкту, мова | `src/`, `package.json`, `.gitignore` |
| `build-and-test` | тестовий фреймворк | `tests/`, оновлений `package.json` |
| `github-actions` | версія Node, тригери | `ci.yml`, `ci.sh`, `ci.bat` |

## Commands

| Command | Передумова | Дія |
|---------|-----------|-----|
| `/git-init` | Репозиторій існує | Перевірка + `.gitignore` |
| `/create-project` | `/git-init` виконано | Scaffold проєкту |
| `/create-build` | `/create-project` виконано | Тести + npm scripts |
| `/create-actions` | `/create-build` виконано | CI workflow |
| `/check` | Будь-який стан | Лише перевірка (без змін) |
| `/init` | Чистий репозиторій | Запускає 1→2→3→4→check |

## Передача даних між етапами

- `/git-init` перевіряє наявність `.git/` → передає статус до `/create-project`
- `/create-project` створює `src/` → `/create-build` використовує ці файли
- `/create-build` встановлює Jest → `/create-actions` може посилатися на `npm test`
- `/check` читає всі файли і звітує про їх стан

## Обробка помилок оркестратором

Оркестратор (`/init`) зупиняється при першій помилці та виводить:
- Який крок завершився помилкою
- Причину помилки
- Рекомендовану дію

Він **не** продовжує виконання при помилці і **не** приховує помилки.

## Відповідність файлів ролям

Методичка вимагає певну структуру. Ось відповідність:

| Роль | Файл у цьому проєкті |
|------|---------------------|
| Agent manifest | `.github/agents/build-engineer.agent.md` |
| Skill (scaffold) | `.github/skills/project-scaffold/SKILL.md` |
| Skill (test) | `.github/skills/build-and-test/SKILL.md` |
| Skill (CI) | `.github/skills/github-actions/SKILL.md` |
| Command git-init | `.github/prompts/git-init.prompt.md` |
| Command create-project | `.github/prompts/create-project.prompt.md` |
| Command create-build | `.github/prompts/create-build.prompt.md` |
| Command create-actions | `.github/prompts/create-actions.prompt.md` |
| Command check | `.github/prompts/check.prompt.md` |
| Orchestrator | `.github/prompts/init.prompt.md` |
