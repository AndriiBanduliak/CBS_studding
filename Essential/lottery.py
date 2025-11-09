import random
from itertools import combinations

# --- Настройки лотереи и стратегии Гессе ---
MAIN_NUMBERS_COUNT = 5
MAIN_NUMBERS_TOTAL = 50
EURO_NUMBERS_COUNT = 2
EURO_NUMBERS_TOTAL = 12
MIN_SUM_MAIN_NUMBERS = 130 # Адаптированное правило суммы Гессе

def print_combination(main_nums, euro_nums, combo_num=None):
    """Аккуратно форматирует и выводит одну комбинацию."""
    main_str = ", ".join(map(str, sorted(main_nums)))
    euro_str = ", ".join(map(str, sorted(euro_nums)))
    
    header = f"Комбинация {combo_num}:" if combo_num else "Ваша комбинация:"
    print(header)
    print(f"  Основные номера: {main_str}")
    print(f"  Еврономера:       {euro_str}\n")

def generate_random_combination():
    """Генерирует одну случайную комбинацию по правилу суммы Гессе."""
    while True:
        main_numbers = random.sample(range(1, MAIN_NUMBERS_TOTAL + 1), MAIN_NUMBERS_COUNT)
        if sum(main_numbers) >= MIN_SUM_MAIN_NUMBERS:
            break
            
    euro_numbers = random.sample(range(1, EURO_NUMBERS_TOTAL + 1), EURO_NUMBERS_COUNT)
    return main_numbers, euro_numbers

def get_user_numbers(prompt, count, max_num):
    """Получает и проверяет числа, введенные пользователем."""
    while True:
        try:
            print(prompt)
            user_input = input(f"> Введите {count} чисел от 1 до {max_num} через пробел: ")
            nums = [int(n) for n in user_input.split()]

            if len(nums) != count:
                print(f"Ошибка: Нужно ввести ровно {count} чисел.")
                continue
            if len(set(nums)) != count:
                print("Ошибка: Числа не должны повторяться.")
                continue
            if not all(1 <= n <= max_num for n in nums):
                print(f"Ошибка: Все числа должны быть в диапазоне от 1 до {max_num}.")
                continue
            
            return nums
        except ValueError:
            print("Ошибка: Пожалуйста, вводите только числа, разделенные пробелом.")

def main():
    """Главная функция с меню выбора стратегий."""
    print("--- Интерактивный генератор комбинаций Eurojackpot ---")
    print("Пожалуйста, выберите одну из стратегий, основанных на методах Кристиана Гессе:\n")

    print("--- [ A ] Стратегия «Минималист» ---")
    print("    Цель: Максимизировать выигрыш в случае победы, не деля его с другими.")
    print("    Действие: Генерируется ОДНА 'умная' комбинация с непопулярными числами.\n")

    print("--- [ B ] Стратегия «Регулярный игрок» ---")
    print("    Цель: Увеличить количество ставок, сохраняя принцип 'умного' выбора.")
    print("    Действие: Генерируется НЕСКОЛЬКО случайных 'умных' комбинаций.\n")
    
    print("--- [ C ] Стратегия «Системный игрок» (Systemspiel '5 из 6') ---")
    print("    Цель: Повысить шансы на частые выигрыши в средних категориях.")
    print("    Действие: Вы сами выбираете 6 основных номеров, а скрипт создает из них все 6 возможных комбинаций.\n")

    while True:
        choice = input("Какую стратегию вы выбираете? (Введите A, B или C): ").strip().upper()
        if choice in ['A', 'B', 'C']:
            break
        else:
            print("Неверный ввод. Пожалуйста, выберите A, B или C.")

    print("-" * 50)

    # --- Логика для каждой стратегии ---

    if choice == 'A':
        print("Выбрана Стратегия А: «Минималист».\nГенерирую одну 'умную' комбинацию...\n")
        main_nums, euro_nums = generate_random_combination()
        print_combination(main_nums, euro_nums)

    elif choice == 'B':
        print("Выбрана Стратегия B: «Регулярный игрок».\n")
        while True:
            try:
                num_combos = int(input("Сколько 'умных' комбинаций сгенерировать? (например, 3): "))
                if num_combos > 0:
                    break
                else:
                    print("Введите положительное число.")
            except ValueError:
                print("Введите корректное число.")
        
        print(f"\nГенерирую {num_combos} комбинаций...\n")
        for i in range(num_combos):
            main_nums, euro_nums = generate_random_combination()
            print_combination(main_nums, euro_nums, combo_num=i + 1)

    elif choice == 'C':
        print("Выбрана Стратегия C: «Системный игрок».\n")
        print("Эта система ('5 из 6') превращает 6 выбранных вами номеров в 6 лотерейных полей.")
        print("Если из ваших 6 номеров выпадут 5 выигрышных, вы гарантированно выиграете джекпот!")
        
        # Получаем номера от пользователя
        user_main_numbers = get_user_numbers(
            "Шаг 1: Выберите ваши 6 основных 'системных' номеров.",
            6, MAIN_NUMBERS_TOTAL
        )
        user_euro_numbers = get_user_numbers(
            "Шаг 2: Выберите ваши 2 еврономера (они будут одинаковы для всех комбинаций).",
            2, EURO_NUMBERS_TOTAL
        )

        # Генерируем все комбинации 5 из 6
        system_combinations = list(combinations(user_main_numbers, 5))

        print("\nВот 6 комбинаций, которые нужно вписать в ваш системный билет:")
        print("-" * 50)
        for i, main_combo in enumerate(system_combinations):
            print_combination(list(main_combo), user_euro_numbers, combo_num=i + 1)

    print("Желаю удачи!")


if __name__ == "__main__":
    main()