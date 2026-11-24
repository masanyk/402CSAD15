# Журнал взаємодії з AI

**Студент:** Процак Максим Степанович, КІ-402, варіант 15 (JavaScript + npm scripts + Jest)
**Репозиторій:** https://github.com/masanyk/402CSAD15

Журнал фіксує запити до AI, важливі відповіді, помилки та прийняті рішення.
Кожен результат AI переглядався вручну і перевірявся запуском (`npm test`,
`npm run build`, `bash ci.sh` / `ci.bat`, GitHub Actions).

---

## Сесія 1 — 05.10.2026, GitHub Copilot Chat (VS Code)

### 1. Проєктування агента
- **Запит (суть):** створити agent manifest `build-engineer` для варіанту JavaScript + npm
  scripts + Jest: роль, область відповідальності, правила роботи з файлами, заборонені дії,
  критерії завершення; три skills (`project-scaffold`, `build-and-test`, `github-actions`)
  і commands `git-init`, `create-project`, `create-build`, `create-actions`, `check`,
  оркестратор `init`.
- **Відповідь / результат:** файли в `.github/agents/`, `.github/skills/`, `.github/prompts/`,
  `docs/architecture.md`, `docs/usage.md`.
- **Перевірка:** вручну звірено зі структурою з методички (розділ 5) — усі ролі файлів присутні.
- **Коміт:** `9a911dd feat: add AI agent (manifest, skills, commands, orchestrator, docs)` → гілка `develop`.

### 2. Генерація проєкту через агента (`/init`)
- **Запит:** запуск оркестратора `/init` на гілці `feature/lab1`.
- **Результат:** `src/index.js` (`greet`), `src/math.js` (`add`, `subtract`), тести Jest,
  `package.json`, `ci.sh`, `ci.bat`, `.github/workflows/ci.yml`, `.gitattributes`.
- **Перевірка:** `npm test` — 2 test suites, 8 тестів PASS; `npm start` → `Hello, World!`.
- **Коміт:** `d60dc7c feat: add JavaScript Hello World project with Jest tests and CI workflow`.

### 3. Помилка CI на Windows та її виправлення
- **Симптом:** запуски CI
  [#1](https://github.com/masanyk/402CSAD15/actions) (push) і
  [#2](https://github.com/masanyk/402CSAD15/actions/runs/37314775486) (pull_request)
  завершилися з `failure`: job `windows-latest` падав на кроці запуску `ci.bat`,
  Ubuntu та macOS проходили.
- **Причина:** на Windows runner крок `run:` за замовчуванням виконується в PowerShell,
  а скрипт потрібно запускати інтерпретатором `cmd`.
- **Запит до AI (суть):** пояснити помилку Windows job і виправити workflow, не додаючи
  прямих npm-команд у `ci.yml`.
- **Рішення:** додано `shell: cmd` до кроку `Run CI script (Windows)`.
- **Перевірка:** запуски #3 і #4 — `success` на всіх трьох ОС.
- **Коміт:** `0c5d47e fix: add shell: cmd for Windows CI step to run ci.bat correctly`.

### 4. Pull requests
- PR [#1 `lab1/finish`](https://github.com/masanyk/402CSAD15/pull/1): `feature/lab1` → `develop`, CI зелений, змерджено.
- PR [#2](https://github.com/masanyk/402CSAD15/pull/2): `develop` → `main`, CI зелений, змерджено.

---

## Сесія 2 — 24.11.2026, AI-асистент Claude Code: перевірка відповідності методичці

### 5. Аудит репозиторію за методичкою
- **Запит:** «глянь першу лабу і подивись, чи я там все зробив».
- **Знайдені невідповідності:**
  1. Немає журналу взаємодії з AI (цей файл).
  2. CI не публікує виконавчих файлів: `ci.sh`/`ci.bat` лише ставили залежності й запускали
     тести, а крок upload шукав `coverage/`, якого `npm test` не створює → артефактів не було.
  3. Немає тесту з назвою `BasicAddition`, яку згадує методичка.
  4. Посилання на стару назву репозиторію `apks-lab1` у README / usage.
- **Рішення, прийняте разом зі студентом:** виправити всі пункти через інструкції агента
  (skills / commands), а не лише ручною правкою результату.

### 6. Складання виконуваного файлу `hello`
- **Варіанти, що розглядалися:** (а) `pkg` / Node SEA — справжній бінарник без Node.js,
  але додаткові залежності й підпис на macOS ускладнюють CI; (б) скрипт складання без
  залежностей, що генерує лаунчери. Обрано (б) як надійний на всіх трьох ОС.
- **Результат:** `scripts/build.js` → `build/hello/hello` (Linux/macOS, права 755),
  `build/hello/hello.cmd` (Windows), `build/hello/lib/*.js`; `npm run build`.
- `ci.sh` / `ci.bat`: `npm ci` → `npm run build` → smoke-тест запуску `hello` (вивід має
  дорівнювати `Hello, World!`) → `npm run test:coverage`.
- `ci.yml`: артефакт `hello-<os>` (job падає, якщо файлу немає) і `coverage-<os>`.
- `build/` додано до `.gitignore`.
- Оновлено skills `build-and-test`, `github-actions`, commands `create-build`,
  `create-actions`, `check` і manifest, щоб повторний запуск агента відтворював цей результат.

### 7. Тест `BasicAddition`
- Додано `test('BasicAddition', ...)` у `tests/math.test.js` (і в шаблон skill `build-and-test`).

### 8. Помилка під час локальної перевірки нового `ci.bat`
- **Симптом 1:** `cmd` виводив `'…ться' is not recognized as an internal or external command`.
  **Причина:** кириличний коментар `REM` у UTF-8 ламав розбір рядків у `cmd`.
  **Рішення:** коментарі в `ci.bat` лише ASCII.
- **Симптом 2:** `hello.cmd` виводив `Hello, World!`, але скрипт повідомляв
  `ERROR: unexpected output`. **Причина:** `findstr /x` не знаходив рядок, бо Node.js
  завершує вивід лише `LF`, без `CR`. **Рішення:** порівняння через
  `set /p HELLO_OUT=<hello-output.txt` і `if not "%HELLO_OUT%"=="Hello, World!"`.
- Обидва сценарії додано в skill `github-actions` (розділ «Типовий сценарій помилки»).
- **Навмисно зламана перевірка:** заміна `greet("World")` на `greet("Broken")` →
  `ci.sh` виводить `ERROR: unexpected output from hello executable`, код виходу 1.

### 9. Перевірка
- Локально (Windows): `npm test` — 9 тестів PASS (серед них `BasicAddition`);
  `ci.bat` — `CI script completed successfully`; `build\hello\hello.cmd` → `Hello, World!`;
  `git status --ignored` — `build/` ignored.
- GitHub Actions: результат запуску для нового PR — див. PR `feature/lab1` → `develop`.
