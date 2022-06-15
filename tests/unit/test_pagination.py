from unittest import mock

from frost_shard.domain.repository import paginate


def test_paginate_list() -> None:
    """Check that pagination returns correct entries."""
    numbers = list(range(10))

    first_three = paginate(numbers, page=0, limit=3)
    assert list(first_three) == numbers[:3]

    second_three = paginate(numbers, page=1, limit=3)
    assert list(second_three) == numbers[3:6]

    last_five = paginate(numbers, page=1, limit=5)
    assert list(last_five) == numbers[5:]


def test_paginate_generator() -> None:
    """Check that pagination does not over iterate."""
    # Mocked function that returns 'True' for even numbers
    func = mock.MagicMock(side_effect=lambda number: number % 2 == 0)

    gen = (number for number in range(10) if func(number))
    result = list(paginate(gen, page=0, limit=3))

    # Pagination needed to pass 5 numbers to get 3 even ones (0, 2, 4)
    assert func.call_count == 5
    assert len(result) == 3
