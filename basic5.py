print("Програма для обчислення суми та середнього чисел в діапазоні.")
start_num = int(input("Введіть перше (початкове) число: "))
end_num = int(input("Введіть останнє (кінцеве) число: "))

if start_num > end_num:
    start_num, end_num = end_num, start_num

numbers_in_range = list(range(start_num, end_num + 1))
total_sum = sum(numbers_in_range)
count = len(numbers_in_range)
average_num = total_sum / count if count != 0 else 0

print(f"Сума чисел від {start_num} до {end_num}: {total_sum}")
print(f"Середнє число в діапазоні: {average_num}")
