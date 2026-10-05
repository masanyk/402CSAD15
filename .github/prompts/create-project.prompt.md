# Команда: /create-project

## Призначення
Викликає skill `project-scaffold` та створює початкову структуру
JavaScript проєкту Hello World.

## Передумови
- Виконана команда `/git-init`
- `package.json` ще не існує (або він порожній)

## Дії
1. Застосувати skill `.github/skills/project-scaffold/SKILL.md`.
2. Створити файли: `src/index.js`, `src/math.js`, `package.json`, `.gitignore`.
3. Переконатися, що `node src/index.js` виводить `Hello, World!`.
4. Закомітити зміни з повідомленням: `feat: scaffold JavaScript Hello World project`.

## Очікувані файли після виконання
```
src/index.js
src/math.js
package.json
.gitignore
```

## Команди перевірки
```bash
node src/index.js
# Очікується: Hello, World!
```

## Повторний запуск
Якщо `src/index.js` вже існує — пропустити створення і повідомити,
що файл вже є. Не перезаписувати.

## Повідомлення про помилку
> Помилка: `src/index.js` вже існує.
> Щоб перестворити проєкт — видали файли вручну або використай нову гілку.
