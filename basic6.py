inv = []
inv_add =["морковь", "картофель", "брокколи", "капуста", "лук", "чеснок"]
for i in inv_add:
    inv.append(i)

add_item = int(input('введите количкстов твоара которое хотите добавить: '))
for i in range(add_item):
    item = input('введите название товара: ')
    inv.append(item)

if not inv:
    print('список товаров пуст')
else:
    for i, item in enumerate(inv):
        print(f'{i + 1}. {item}')
while True:
    item_to_check = input('введите название товара для проверки: (или exit чтоб пойти дальше ) ')
    if item_to_check.lower() == "exit":
        break
while True:
    item_to_remove = input('введите название товара для удаления: (или exit для завершения) ')
    if item_to_remove.lower() == "exit":
        break
    if item_to_remove in inv:
        inv.remove(item_to_remove)
        print(f"Товар '{item_to_remove}' удален из инвентаря.")
        if not inv:
            print("Инвентарь пуст.")
        else:
            for i, item in enumerate(inv):
                print(f"{i + 1}. {item}")
    else:
        print(f"Товар '{item_to_remove}' не найден в инвентаре.")
    
unique_items = set(inv)
print(f"\nОбщее количество уникальных товаров в инвентаре: {len(unique_items)}")
      