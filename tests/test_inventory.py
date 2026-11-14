import pytest

from src.inventory import (
    Inventory,
    Item,
    OutOfStockError,
    UnknownItemError,
)


@pytest.fixture
def inventory():
    inv = Inventory()
    inv.add(Item("apple", 10.0), quantity=10)
    return inv


@pytest.fixture
def populated_inventory():
    inv = Inventory()
    inv.add(Item("pear", 12.345), quantity=2)
    inv.add(Item("apple", 5.5), quantity=5)
    inv.add(Item("banana", 3.0), quantity=6)
    inv.add(Item("apricot", 8.0), quantity=1)
    return inv


def test_item_creation_valid_sets_fields():
    item = Item("apple", 10.5, quantity=3)
    assert item.name == "apple"
    assert item.price == pytest.approx(10.5)
    assert item.quantity == 3


def test_item_creation_zero_price_and_quantity_allowed():
    item = Item("freebie", 0.0)
    assert item.price == pytest.approx(0.0)
    assert item.quantity == 0


@pytest.mark.parametrize(
    "name, price, quantity",
    [
        ("", 10.0, 1),
        ("apple", -0.01, 1),
        ("apple", 10.0, -1),
    ],
)
def test_item_creation_invalid_raises_value_error(name, price, quantity):
    with pytest.raises(ValueError):
        Item(name, price, quantity)


def test_add_new_item_stores_with_default_quantity():
    inv = Inventory()
    inv.add(Item("orange", 4.5))
    found = inv.find("orange")
    assert found.quantity == 1


def test_add_existing_item_increases_quantity(inventory):
    inventory.add(Item("apple", 10.0), quantity=5)
    assert inventory.find("apple").quantity == 15


@pytest.mark.parametrize("quantity", [0, -1, -5])
def test_add_non_positive_quantity_raises_value_error(inventory, quantity):
    with pytest.raises(ValueError):
        inventory.add(Item("banana", 2.0), quantity=quantity)


def test_remove_partial_quantity_decreases_stock(inventory):
    inventory.remove("apple", quantity=4)
    assert inventory.find("apple").quantity == 6


def test_remove_exact_quantity_deletes_item(inventory):
    inventory.remove("apple", quantity=10)
    with pytest.raises(UnknownItemError):
        inventory.find("apple")


def test_remove_unknown_item_raises(inventory):
    with pytest.raises(UnknownItemError):
        inventory.remove("banana")


def test_remove_more_than_available_raises_out_of_stock(inventory):
    with pytest.raises(OutOfStockError):
        inventory.remove("apple", quantity=11)


@pytest.mark.parametrize("quantity", [0, -2])
def test_remove_non_positive_quantity_raises_value_error(inventory, quantity):
    with pytest.raises(ValueError):
        inventory.remove("apple", quantity=quantity)


def test_find_existing_item_returns_item(inventory):
    item = inventory.find("apple")
    assert item.name == "apple"
    assert item.price == pytest.approx(10.0)


def test_find_unknown_item_raises_unknown_item_error(inventory):
    with pytest.raises(UnknownItemError):
        inventory.find("grape")


def test_total_value_empty_inventory_returns_zero():
    inv = Inventory()
    assert inv.total_value() == pytest.approx(0.0)


def test_total_value_multiple_items_returns_rounded_sum(populated_inventory):
    # 2*12.345 + 5*5.5 + 6*3.0 + 1*8.0 = 24.69 + 27.5 + 18.0 + 8.0 = 78.19
    assert populated_inventory.total_value() == pytest.approx(78.19)


def test_low_stock_default_threshold_returns_sorted_names(populated_inventory):
    assert populated_inventory.low_stock() == ["apple", "apricot", "pear"]


def test_low_stock_explicit_threshold_filters_correctly(populated_inventory):
    assert populated_inventory.low_stock(threshold=1) == ["apricot"]
    assert populated_inventory.low_stock(threshold=0) == []


def test_low_stock_negative_threshold_raises_value_error(inventory):
    with pytest.raises(ValueError):
        inventory.low_stock(threshold=-1)


@pytest.mark.parametrize(
    "percent, expected",
    [
        (0, 100.0),
        (10, 90.0),
        (100, 0.0),
    ],
)
def test_apply_discount_valid_percent(inventory, percent, expected):
    assert inventory.apply_discount(percent) == pytest.approx(expected)


@pytest.mark.parametrize("percent", [-0.1, -10, 100.1, 150])
def test_apply_discount_invalid_percent_raises_value_error(inventory, percent):
    with pytest.raises(ValueError):
        inventory.apply_discount(percent)
