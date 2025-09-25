from abc import ABC, abstractmethod
from typing import List


class Observer(ABC):
    """
    Інтерфейс Спостерігача.
    Оголошує метод update, який використовується суб'єктами для сповіщення.
    """
    @abstractmethod
    # Використовуємо лапки 'Product', тому що клас Product ще не оголошено
    def update(self, product: 'Product') -> None:
        """Отримує оновлення від об'єкта товару."""
        pass


class Subject(ABC):
    """
    Інтерфейс Суб'єкта.
    Оголошує набір методів для керування підписниками (спостерігачами).
    """
    @abstractmethod
    def attach(self, observer: Observer) -> None:
        """Додає спостерігача до списку."""
        pass

    @abstractmethod
    def detach(self, observer: Observer) -> None:
        """Видаляє спостерігача зі списку."""
        pass

    @abstractmethod
    def notify(self) -> None:
        """Сповіщає всіх спостерігачів про події."""
        pass


class Product(Subject):
    """
    Конкретний клас Товару, який реалізує інтерфейс Subject.
    Він відстежує свою кількість на складі та сповіщає підписників,
    коли товар знову з'являється в наявності.
    """
    def __init__(self, name: str, stock: int = 0):
        self._name = name
        self._stock = stock
        self._observers: List[Observer] = []
        print(f"Створено товар: '{self._name}'. Початкова кількість: {self._stock}")

    def attach(self, observer: Observer) -> None:
        print(f"До товару '{self._name}' додано нового спостерігача.")
        self._observers.append(observer)

    def detach(self, observer: Observer) -> None:
        self._observers.remove(observer)

    def notify(self) -> None:
        """Запускає оновлення в кожному підписнику."""
        print(f"Сповіщення всіх спостерігачів для товару '{self._name}'...")
        for observer in self._observers:
            observer.update(self)

    @property
    def name(self) -> str:
        return self._name

    @property
    def stock(self) -> int:
        return self._stock

    @stock.setter
    def stock(self, new_stock: int) -> None:
        """
        Встановлює нову кількість товару.
        Перевіряє, чи змінилася кількість з 0 на щось більше.
        """
        old_stock = self._stock
        self._stock = new_stock
        print(f"Оновлення складу '{self._name}': було {old_stock}, стало {self._stock}.")

        # Ключова умова завдання: сповіщати ТІЛЬКИ якщо кількість змінилася з 0 на >0
        if old_stock == 0 and new_stock > 0:
            print(f"\n>>> УВАГА! Товар '{self._name}' знову в наявності!")
            self.notify()


class Customer(Observer):
    """
    Конкретний клас Клієнта, який реалізує інтерфейс Observer.
    """
    def __init__(self, name: str, email: str):
        self._name = name
        self._email = email

    def update(self, product: Product) -> None:
        """
        Реалізація методу update.
        Виводить повідомлення в консоль, як вимагалось у завданні.
        """
        print(f"📩 Привіт, {self._name}! Товар '{product.name}' знову в наявності. Поспішайте зробити замовлення!")


if __name__ == "__main__":
    # 1. Створюємо товар, якого немає в наявності (0 штук)
    playstation = Product("PlayStation 5", stock=0)
    print("-" * 40)

    # 2. Створюємо клієнтів (спостерігачів)
    customer1 = Customer("Олексій", "alex@example.com")
    customer2 = Customer("Марія", "maria@example.com")

    # 3. Клієнти підписуються на оновлення товару
    playstation.attach(customer1)
    playstation.attach(customer2)
    print("-" * 40)

    # 4. Сценарій 1: Оновлюємо склад, але товару все ще немає (0 -> 0)
    # Сповіщення НЕ має бути
    playstation.stock = 0
    print("-" * 40)

    # 5. Сценарій 2: Товар надійшов на склад (0 -> 10)
    # Сповіщення МАЄ бути відправлено обом клієнтам
    playstation.stock = 10
    print("-" * 40)

    # 6. Сценарій 3: Кількість товару зменшилась, але він ще є (10 -> 5)
    # Сповіщення НЕ має бути
    playstation.stock = 5
    print("-" * 40)

    # 7. Сценарій 4: Товар закінчився (5 -> 0)
    # Сповіщення НЕ має бути
    playstation.stock = 0
    print("-" * 40)

    # 8. Сценарій 5: Товар ЗНОВУ надійшов (0 -> 3)
    # Сповіщення МАЄ бути відправлено
    playstation.stock = 3
    print("-" * 40)
    
 