# Команда: /check

## Призначення
Перевіряє повноту та коректність проєкту БЕЗ внесення змін.
Ця команда лише читає і звітує — вона не змінює жодних файлів.

## Передумови
Немає. Можна запускати на будь-якому етапі.

## Дії (лише перевірка, без змін)

### 1. Перевірка агента
- [ ] Існує `.github/agents/build-engineer.agent.md`
- [ ] Manifest містить: роль, skills, commands, заборонені дії, критерії завершення

### 2. Перевірка skills
- [ ] `.github/skills/project-scaffold/SKILL.md` існує та містить: входи, виходи, перевірку
- [ ] `.github/skills/build-and-test/SKILL.md` існує та містить: входи, виходи, перевірку
- [ ] `.github/skills/github-actions/SKILL.md` існує та містить: входи, виходи, перевірку

### 3. Перевірка commands
- [ ] Існують усі 6 файлів у `.github/prompts/`
- [ ] `init.prompt.md` викликає інші команди у правильному порядку

### 4. Перевірка проєкту
- [ ] `src/index.js` існує та виводить "Hello, World!"
- [ ] `tests/index.test.js` та `tests/math.test.js` існують
- [ ] `npm test` виконується успішно (всі тести PASS)
- [ ] `npm start` виводить "Hello, World!"

### 5. Перевірка CI
- [ ] `.github/workflows/ci.yml` існує
- [ ] Матриця містить: ubuntu-latest, windows-latest, macos-latest
- [ ] `ci.yml` викликає `ci.sh` / `ci.bat`, а не прямі npm команди
- [ ] `ci.sh` та `ci.bat` існують

### 6. Перевірка Git
- [ ] `node_modules/` відсутній у Git (`git ls-files node_modules` — порожньо)
- [ ] `.gitignore` містить: `node_modules/`, `*.log`, `.env`, `coverage/`
- [ ] Немає uncommitted секретів або токенів

### 7. Перевірка документації
- [ ] `docs/architecture.md` існує
- [ ] `docs/usage.md` містить команди запуску агента та проєкту

## Звіт
Після перевірки вивести:
```
=== CHECK REPORT ===
✅ Agent manifest: OK
✅ Skills (3/3): OK
✅ Commands (6/6): OK
✅ Project builds: OK
✅ Tests pass: OK
✅ CI workflow: OK
✅ Git hygiene: OK
===================
Статус: READY ✅
```
або з переліком того, що потребує виправлення.
