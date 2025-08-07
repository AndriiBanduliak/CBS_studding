import math

operation_chosen = ''

while operation_chosen != 'q':
    print("=" * 30)
    print("Виберіть операцію:")
    print("1. Розрахунок периметра трикутника")
    print("2. Розрахунок площі прямокутника")
    print("3. Розрахунок об'єму паралелепіпеда")
    print("4. Розрахунок площі круга")
    print("q. Вийти")
    print("=" * 30)

    operation_chosen = input("Введіть номер операції (1, 2, 3, 4 або q): ").lower()

    if operation_chosen == '1':
        print("\n--- Розрахунок периметра трикутника ---")
        a_str = input("Введіть довжину першої сторони (a): ")
        try:
            a = float(a_str)
            b_str = input("Введіть довжину другої сторони (b): ")
            b = float(b_str)
            c_str = input("Введіть довжину третьої сторони (c): ")
            c = float(c_str)
            perimeter = a + b + c
            print(f"Результат: Периметр трикутника дорівнює: {perimeter}")
        except ValueError:
            print("Некоректне введення. Будь ласка, введіть число.")

    elif operation_chosen == '2':
        print("\n--- Розрахунок площі прямокутника ---")
        length_str = input("Введіть довжину прямокутника: ")
        try:
            length = float(length_str)
            width_str = input("Введіть ширину прямокутника: ")
            width = float(width_str)
            area = length * width
            print(f"Результат: Площа прямокутника дорівнює: {area}")
        except ValueError:
            print("Некоректне введення. Будь ласка, введіть число.")

    elif operation_chosen == '3':
        print("\n--- Розрахунок об'єму паралелепіпеда ---")
        length_str = input("Введіть довжину паралелепіпеда: ")
        try:
            length = float(length_str)
            width_str = input("Введіть ширину паралелепіпеда: ")
            width = float(width_str)
            height_str = input("Введіть висоту паралелепіпеда: ")
            height = float(height_str)
            volume = length * width * height
            print(f"Результат: Об'єм паралелепіпеда дорівнює: {volume}")
        except ValueError:
            print("Некоректне введення. Будь ласка, введіть число.")

    elif operation_chosen == "4":
        print("\n--- Розрахунок площі круга ---")
        radius_str = input("Введіть радіус круга: ")
        try:
            radius = float(radius_str)
            circle_area = math.pi * (radius ** 2)
            print(f"Результат: Площа круга дорівнює: {round(circle_area, 2)}")
        except ValueError:
            print("Некоректне введення. Будь ласка, введіть число.")

    if operation_chosen != 'q':
        input("Натисніть Enter, щоб продовжити...")

print("\nПрограма завершена.")