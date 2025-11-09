def main() -> None:
    """Main function."""
    print("Hello from simultaneousness-analysis!")


# def function_without_annotations(a, b):
#     return a + b


def function_with_annotations(a: int, b: int) -> int:
    """Adds and returns two integers.

    Args:
        a (int): first integer
        b (int): second integer

    Returns:
        int: result of addition
    """
    return a + b


if __name__ == "__main__":
    main()
