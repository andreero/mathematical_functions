import pytest
from functions import Term, multiply_elementary_terms

term_zero = Term(is_zero=True)
term_1 = Term(subscript={1}, superscript={2, 3, 4})
term_2 = Term(subscript={3}, superscript={2, 5, 6})
term_3 = Term(subscript={1, 2}, superscript={4, 5})
term_4 = Term(subscript={2, 3}, superscript={6, 7})
term_5 = Term(subscript={2}, superscript={8, 9})
term_3x5 = Term(subscript={1, 2}, superscript={4, 5, 8, 9})
term_5x4 = Term(subscript={2, 3}, superscript={6, 7, 8, 9})


class TestMultiplication:
    def test_multiply_by_zero(self):
        assert term_1 * term_zero == term_zero
        assert term_zero * term_2 == term_zero

    def test_multiply_two_numbers_in_common(self):
        assert term_1 * term_2 == term_zero

    def test_multiply_subscripts_coincide(self):
        assert term_3 * term_4 == term_zero

    def test_second_subscript_in_first_subscript(self):
        assert term_3 * term_5 == term_3x5

    def test_first_subscript_in_second_subscript(self):
        assert term_5 * term_4 == term_5x4
