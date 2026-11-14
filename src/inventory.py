"""Модуль складского учёта для лабораторной работы по модульному тестированию.

Студентам необходимо покрыть тестами все публичные методы и свойства,
включая обработку исключений и граничные значения.
"""

from dataclasses import dataclass


class OutOfStockError(Exception):
    """Выбрасывается при попытке списать больше, чем есть на складе."""


class UnknownItemError(Exception):
    """Выбрасывается при обращении к отсутствующей позиции."""


@dataclass
class Item:
    """Позиция на складе."""

    name: str
    price: float
    quantity: int = 0

    def __post_init__(self):
        if not self.name:
            raise ValueError("name must not be empty")
        if self.price < 0:
            raise ValueError("price must be non-negative")
        if self.quantity < 0:
            raise ValueError("quantity must be non-negative")


class Inventory:
    """Складской учёт."""

    def __init__(self):
        self._items: dict[str, Item] = {}

    def add(self, item: Item, quantity: int = 1) -> None:
        """Добавить позицию или увеличить количество существующей."""
        if quantity <= 0:
            raise ValueError("quantity must be positive")
        if item.name in self._items:
            self._items[item.name].quantity += quantity
        else:
            item.quantity = quantity
            self._items[item.name] = item

    def remove(self, name: str, quantity: int = 1) -> None:
        """Списать позицию. Удаляет позицию при обнулении количества."""
        if quantity <= 0:
            raise ValueError("quantity must be positive")
        if name not in self._items:
            raise UnknownItemError(name)
        item = self._items[name]
        if item.quantity < quantity:
            raise OutOfStockError(
                f"{name}: have {item.quantity}, need {quantity}"
            )
        item.quantity -= quantity
        if item.quantity == 0:
            del self._items[name]

    def find(self, name: str) -> Item:
        """Найти позицию по имени."""
        if name not in self._items:
            raise UnknownItemError(name)
        return self._items[name]

    def total_value(self) -> float:
        """Суммарная стоимость склада, округлённая до 2 знаков."""
        return round(
            sum(i.price * i.quantity for i in self._items.values()), 2
        )

    def low_stock(self, threshold: int = 5) -> list[str]:
        """Имена позиций с количеством не выше порога (отсортированы)."""
        if threshold < 0:
            raise ValueError("threshold must be non-negative")
        return sorted(
            n for n, i in self._items.items() if i.quantity <= threshold
        )

    def apply_discount(self, percent: float) -> float:
        """Стоимость склада с учётом скидки в процентах."""
        if not 0 <= percent <= 100:
            raise ValueError("percent must be in 0..100")
        return round(self.total_value() * (1 - percent / 100), 2)