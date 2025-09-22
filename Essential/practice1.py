from typing import List, Generator,Union

NestedList = List[Union[int, 'NestedList']]

def flatten_list(nested_list: List[List[int]]) -> Generator[int, None, None]:
    for item in nested_list:
        if isinstance(item, list):
            yield from flatten_list(item)
        else:
            yield item

my_nested_list = [1, 2, [3, 4, [5, 6]], 7, [8, [9, 10]], 11]

print(list(flatten_list(my_nested_list)))

flat_generator = flatten_list(my_nested_list)

print(type(flat_generator))
print("--"*45)

for _ in flat_generator:
    print(_, end=" ")
print("\n"+"--"*45)