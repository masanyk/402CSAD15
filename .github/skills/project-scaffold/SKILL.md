---
name: project-scaffold
description: Створює мінімальний JavaScript Hello World проєкт із коректною структурою каталогів, package.json та .gitignore.
applies_when: Потрібно ініціалізувати новий JavaScript проєкт з нуля.
---

# Skill: project-scaffold

## Призначення
Створити мінімальну структуру JavaScript-проєкту, готову до подальшого
налаштування складання та тестування.

## Вхідні дані
| Параметр | Тип | Опис |
|----------|-----|------|
| `project_name` | string | Назва проєкту (використовується в `package.json`) |
| `language` | string | Завжди `javascript` для цього варіанту |

## Очікуваний результат
Після виконання skill у репозиторії повинні з'явитися:
```
src/
  index.js        ← головний файл із виводом "Hello, World!"
  math.js         ← допоміжний модуль для тестування
tests/
  (порожня папка, .gitkeep)
docs/
  (порожня папка, .gitkeep)
package.json      ← з полями name, version, scripts, jest config
.gitignore        ← node_modules, *.log, .env
README.md         ← оновлений з описом проєкту
```

## Дії skill
1. Перевірити, чи існує `package.json`. Якщо так — не перезаписувати.
2. Створити `src/index.js` з кодом:
   ```javascript
   function greet(name) {
     return `Hello, ${name}!`;
   }
   console.log(greet("World"));
   module.exports = { greet };
   ```
3. Створити `src/math.js` з допоміжними функціями для тестів:
   ```javascript
   function add(a, b) { return a + b; }
   function subtract(a, b) { return a - b; }
   module.exports = { add, subtract };
   ```
4. Створити `package.json` зі scripts та jest конфігурацією.
5. Оновити `.gitignore`.

## Перевірка результату
```bash
node src/index.js
# Очікується: Hello, World!
```
Файли `src/index.js` та `package.json` повинні існувати.

## Типовий сценарій помилки
**Помилка:** `package.json` вже існує і має інші scripts.
**Дія:** Не перезаписувати. Повідомити користувача і запропонувати злиття вручну.
