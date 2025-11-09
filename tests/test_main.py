from src.simultaneousness_analysis.main import function_with_annotations


def test_function_with_annotations_adds_two_integers() -> None:
    assert function_with_annotations(2, 3) == 5
    assert function_with_annotations(-1, 1) == 0
    assert function_with_annotations(0, 0) == 0
    assert function_with_annotations(-5, -7) == -12
