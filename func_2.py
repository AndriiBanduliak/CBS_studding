def task2(a, b):
    if a > b:
        return 0
    return a + task2(a + 1, b)


a = int(input("Введите первое целое число (a): "))
b = int(input("Введите второе целое число (b): "))
result = task2(a, b)
print(f"Результат: {result}")