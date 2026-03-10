from typing import List


def func_add(a: int, b: int) -> int:
    return a + b


def func_filter_even(numbers: List[int]) -> List[int]:
    return [n for n in numbers if n % 2 == 0]


def multiply(a: int, b: int) -> int: 
    return a * b


def greet(name: str) -> str: 
    return f"Hello, {name}!"


def func_average(numbers: List[float]) -> float:
    if not numbers:
        return 0.0
    return sum(numbers) / len(numbers)


def run_demo() -> None:  # does not follow the `func_` prefix rule
    nums = [1, 2, 3, 4, 5, 6]
    print("Add:", func_add(3, 7))
    print("Even numbers:", filter_even(nums))
    print("Multiply:", func_multiply(4, 5))
    print("Greeting:", greet("Andrew"))
    print("Average:", func_average([10.0, 20.0, 30.0]))


if __name__ == "__main__":
    run_demo()