# Команда: /create-actions

## Призначення
Викликає skill `github-actions` та створює CI workflow для автоматичної
перевірки проєкту на трьох операційних системах.

## Передумови
- Виконана команда `/create-build`
- `npm test` проходить локально

## Дії
1. Застосувати skill `.github/skills/github-actions/SKILL.md`.
2. Створити `ci.sh` (для Linux/macOS) та `ci.bat` (для Windows).
3. Створити `.github/workflows/ci.yml` з матрицею: ubuntu-latest, windows-latest, macos-latest.
4. Переконатися, що `ci.yml` викликає лише `ci.sh` або `ci.bat`, а не прямі npm-команди.
5. Закомітити зміни з повідомленням: `feat: add GitHub Actions CI workflow`.
6. Запушити зміни і перевірити, що Actions запустились на GitHub.

## Очікувані файли після виконання
```
ci.sh
ci.bat
.github/workflows/ci.yml
```

## Перевірка
- Відкрити вкладку "Actions" на GitHub
- Переконатися, що є три зелені галочки (Ubuntu, Windows, macOS)

## Повторний запуск
Якщо `ci.yml` вже існує — не перезаписувати. Порівняти наявний файл
із вимогами і повідомити, чи потрібні зміни.

## Повідомлення про помилку
> Помилка: `Error: ci.sh: Permission denied` на Ubuntu runner.
> Дія: Додати до репозиторію `.gitattributes` з рядком `ci.sh text eol=lf`.
