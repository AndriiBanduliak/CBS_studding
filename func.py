"""def func_short(text, times):

  return (text + '\n') * times


print(func_short('hello world', 3)) """


def task3(text):
    if not text: return (None, 0)
    el_count = {}
    for char in text:
        el_count[char] = el_count.get(char, 0) + 1
        most_common = max(el_count, key=el_count.get)
        repetitions = el_count[most_common]
    return (most_common, repetitions)

my_string = 'hello____ world_______'
char, count = task3(my_string)
print(f"The most common character is '{char}' with {count} repetitions.")
                            