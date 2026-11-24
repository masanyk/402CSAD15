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
3. Оновити `package.json`: додати scripts (`start`, `build`, `test`, `test:coverage`).
4. Створити `tests/index.test.js` та `tests/math.test.js` (включно з тестом `BasicAddition`).
5. Створити `scripts/build.js`, що генерує виконуваний файл `build/hello/hello` (+ `hello.cmd`).
6. Додати `build/` до `.gitignore`.
7. Запустити `npm test` і `npm run build`, переконатися, що тести проходять, а `hello` виводить `Hello, World!`.
8. Закомітити зміни з повідомленням: `feat: add Jest unit tests, build script and npm scripts`.

## Очікувані файли після виконання
```
tests/index.test.js
tests/math.test.js
scripts/build.js
package.json        ← оновлений з jest конфігурацією
node_modules/       ← НЕ комітити!
build/hello/        ← результат складання, НЕ комітити!
```

## Команди перевірки
```bash
npm test
# Очікується: PASS tests/index.test.js, PASS tests/math.test.js (з BasicAddition)
npm run build && node build/hello/lib/index.js
# Очікується: Hello, World!
```

## Повторний запуск
Якщо `tests/` вже існує — перевірити наявність тестів і не дублювати їх.

## Повідомлення про помилку
> Помилка: `Cannot find module '../src/index'`
> Причина: Не виконана команда `/create-project`.
> Дія: Спочатку виконай `/create-project`.
