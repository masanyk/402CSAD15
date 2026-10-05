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
package.json      ← оновлений з "test": "jest", "start": "node src/index.js"
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
   describe('math functions', () => {
     test('adds two numbers correctly', () => {
       expect(add(2, 3)).toBe(5);
     });
     test('subtracts two numbers correctly', () => {
       expect(subtract(10, 4)).toBe(6);
     });
   });
   ```

## Перевірка результату
```bash
npm test
# Усі тести повинні пройти (PASS)
```

## Типовий сценарій помилки
**Помилка:** `Cannot find module '../src/index'`
**Причина:** Skill `project-scaffold` не був виконаний.
**Дія:** Спочатку виконати `/create-project`, потім повторити `/create-build`.
