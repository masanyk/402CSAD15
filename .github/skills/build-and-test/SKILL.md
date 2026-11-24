---
name: build-and-test
description: Налаштовує npm scripts для запуску проєкту та Jest для юніт-тестування.
applies_when: Проєкт вже проскафолджений і потрібно додати тести та команди складання.
---

# Skill: build-and-test

## Призначення
Налаштувати систему автоматизованої перевірки коду:
- npm scripts для запуску та тестування
- Юніт-тести на Jest для функцій `greet` та `add`/`subtract`

## Вхідні дані
| Параметр | Тип | Опис |
|----------|-----|------|
| `test_framework` | string | Завжди `jest` для цього варіанту |

## Очікуваний результат
```
tests/
  index.test.js   ← тести для greet()
  math.test.js    ← тести для add() та subtract()
scripts/
  build.js        ← складання: створює build/hello/hello та build/hello/hello.cmd
package.json      ← оновлений з "start", "build", "test", "test:coverage"
build/            ← результат складання (НЕ комітиться, є в .gitignore)
```

## Дії skill
1. Встановити Jest як devDependency:
   ```bash
   npm install --save-dev jest
   ```
2. Додати до `package.json` розділ `scripts`:
   ```json
   {
     "scripts": {
       "start": "node src/index.js",
       "build": "node scripts/build.js",
       "test": "jest",
       "test:coverage": "jest --coverage"
     },
     "jest": {
       "testEnvironment": "node"
     }
   }
   ```
3. Створити `tests/index.test.js`:
   ```javascript
   const { greet } = require('../src/index');
   describe('greet function', () => {
     test('returns Hello, World! for World input', () => {
       expect(greet('World')).toBe('Hello, World!');
     });
     test('returns correct greeting for any name', () => {
       expect(greet('Максим')).toBe('Hello, Максим!');
     });
   });
   ```
4. Створити `tests/math.test.js`:
   ```javascript
   const { add, subtract } = require('../src/math');
   describe('add function', () => {
     test('BasicAddition', () => {
       expect(add(1, 1)).toBe(2);
     });
     test('adds two numbers correctly', () => {
       expect(add(2, 3)).toBe(5);
     });
     test('subtracts two numbers correctly', () => {
       expect(subtract(10, 4)).toBe(6);
     });
   });
   ```
5. Створити `scripts/build.js` (Node.js, без сторонніх залежностей), який:
   - перестворює лише каталог `build/hello/`;
   - копіює `src/*.js` у `build/hello/lib/`;
   - створює виконуваний файл `build/hello/hello` (`#!/bin/sh` → `exec node "$DIR/lib/index.js"`, права 755);
   - створює `build/hello/hello.cmd` для Windows (`node "%~dp0lib\index.js" %*`).
6. Додати `build/` до `.gitignore` (якщо ще немає).

## Приклад входу
`test_framework = "jest"`, у репозиторії вже є `src/index.js` та `src/math.js`.

## Перевірка результату
```bash
npm test              # усі тести PASS, серед них BasicAddition
npm run build         # Build OK: build/hello
./build/hello/hello   # Hello, World!   (Windows: build\hello\hello.cmd)
git status --ignored  # build/ позначено як ignored
```

## Типовий сценарій помилки
**Помилка:** `Cannot find module '../src/index'`
**Причина:** Skill `project-scaffold` не був виконаний.
**Дія:** Спочатку виконати `/create-project`, потім повторити `/create-build`.
