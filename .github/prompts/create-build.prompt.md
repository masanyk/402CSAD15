# Команда: /create-build

## Призначення
Викликає skill `build-and-test` та створює конфігурацію складання і
юніт-тести за допомогою Jest.

## Передумови
- Виконана команда `/create-project`
- Існують файли `src/index.js` та `src/math.js`

## Дії
1. Застосувати skill `.github/skills/build-and-test/SKILL.md`.
2. Встановити `jest` як devDependency: `npm install --save-dev jest`.
3. Оновити `package.json`: додати scripts (`start`, `test`, `test:coverage`).
4. Створити `tests/index.test.js` та `tests/math.test.js`.
5. Запустити `npm test` і переконатися, що всі тести проходять.
6. Закомітити зміни з повідомленням: `feat: add Jest unit tests and npm scripts`.

## Очікувані файли після виконання
```
tests/index.test.js
tests/math.test.js
package.json        ← оновлений з jest конфігурацією
node_modules/       ← НЕ комітити!
```

## Команди перевірки
```bash
npm test
# Очікується: PASS tests/index.test.js, PASS tests/math.test.js
```

## Повторний запуск
Якщо `tests/` вже існує — перевірити наявність тестів і не дублювати їх.

## Повідомлення про помилку
> Помилка: `Cannot find module '../src/index'`
> Причина: Не виконана команда `/create-project`.
> Дія: Спочатку виконай `/create-project`.
