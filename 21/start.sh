#!/bin/bash

# Назва головної папки проєкту
PROJECT_NAME="blackjack_pygame"

# Повідомлення про початок роботи
echo "Creating project structure for '$PROJECT_NAME'..."

# Створюємо головну папку проєкту і переходимо в неї
mkdir -p "$PROJECT_NAME"
cd "$PROJECT_NAME"

# 1. Створюємо основні папки: game_logic, ui, tests
mkdir -p game_logic ui tests

# 2. Створюємо вкладені папки всередині ui/assets
mkdir -p ui/assets/cards ui/assets/fonts ui/assets/other

# 3. Створюємо порожні файли .py за допомогою команди touch
# Використовуємо фігурні дужки для створення файлів у кількох папках одним рядком
touch {game_logic,ui,tests}/__init__.py

touch game_logic/card.py \
      game_logic/deck.py \
      game_logic/player.py \
      ui/components.py \
      tests/test_game_logic.py \
      main.py \
      requirements.txt

# 4. Додаємо pygame до файлу requirements.txt
echo "pygame" > requirements.txt

# Повідомлення про успішне завершення
echo "Project structure for '$PROJECT_NAME' has been created successfully."
echo

# 5. Виводимо створену структуру дерева папок (якщо утиліта tree встановлена)
if command -v tree &> /dev/null
then
    echo "Project structure:"
    tree .
else
    echo "Project structure created. Install 'tree' utility to visualize it."
    echo "On Debian/Ubuntu: sudo apt-get install tree"
    echo "On macOS: brew install tree"
fi

exit 0





