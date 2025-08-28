def filter_even_numbers_comprehension(numbers_list):  
    return [number for number in numbers_list if number % 2 == 0]

my_numbers = [11, 22, 33, 44, 55, 66]
even_only = filter_even_numbers_comprehension(my_numbers)

print(even_only)  