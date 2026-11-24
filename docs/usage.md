# Інструкція з використання

## Запуск AI-агента (develop гілка)

### Спосіб 1: через GitHub Copilot Chat у VS Code

1. Відкрий репозиторій у VS Code на гілці `develop`
2. Відкрий Copilot Chat: `Ctrl+Alt+I` або клацни іконку чату на бічній панелі
3. Щоб запустити повний сценарій:
   ```
   @workspace /init
   ```
   або відкрий файл `.github/prompts/init.prompt.md` і натисни "Run in Chat"

4. Щоб запустити окрему команду:
   ```
   @workspace /create-project
   @workspace /check
   ```

### Спосіб 2: ручний запуск окремих команд

Відкрий будь-який файл із `.github/prompts/` і скопіюй його вміст у Copilot Chat.

### Порядок команд (якщо запускаєш вручну)
```
1. /git-init
2. /create-project
3. /create-build
4. /create-actions
5. /check
```

---

## Запуск проєкту локально (feature/lab1 гілка)

### Передумови
- Node.js v20+ встановлено (`node --version`)
- npm встановлено (`npm --version`)

### Встановлення залежностей
```bash
npm install
```

### Запуск Hello World
```bash
npm start
# Виводить: Hello, World!
```

### Запуск тестів
```bash
npm test
```
Очікуваний результат:
```
PASS tests/index.test.js
PASS tests/math.test.js

Test Suites: 2 passed, 2 total
Tests:       9 passed, 9 total
```

### Складання виконуваного файлу hello
```bash
npm run build
./build/hello/hello          # Linux / macOS → Hello, World!
```
```cmd
buildhellohello.cmd        :: Windows → Hello, World!
```
Каталог `build/` в `.gitignore` і не комітиться.

Готовий виконуваний файл для кожної ОС можна завантажити з GitHub Actions:
відкрий запуск workflow → секція **Artifacts** → `hello-<os>`.
Після розпакування на Linux/macOS поверни право виконання: `chmod +x hello`
(архів артефактів GitHub не зберігає біт виконання). Потрібен встановлений Node.js.

### Запуск тестів з покриттям коду
```bash
npm run test:coverage
```

---

## Перевірка CI скриптів локально

### Linux / macOS
```bash
bash ci.sh
```

### Windows
```cmd
ci.bat
```

---

## GitHub Actions

Після push до гілки `develop` або `feature/lab1`:
1. Зайди на `https://github.com/masanyk/402CSAD15/actions`
2. Знайди запущений workflow "CI"
3. Переконайся, що всі три матричні задачі (Ubuntu, Windows, macOS) зелені ✅
4. Внизу сторінки запуску в **Artifacts** мають бути `hello-*` та `coverage-*`
