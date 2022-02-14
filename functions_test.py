import pytest
from functions import Term, cobound, fourfold

term_zero = Term(is_zero=True)
term_1 = Term(subscript={1}, superscript={2, 3, 4})
term_2 = Term(subscript={3}, superscript={2, 5, 6})
term_3 = Term(subscript={1, 2}, superscript={4, 5})
term_4 = Term(subscript={2, 3}, superscript={6, 7})
term_5 = Term(subscript={2}, superscript={8, 9})
term_3x5 = Term(subscript={1, 2}, superscript={4, 5, 8, 9})
term_5x4 = Term(subscript={2, 3}, superscript={6, 7, 8, 9})
x1 = Term(superscript={10}, subscript={4, 8, 9})
x2 = Term(superscript={4}, subscript={1, 2, 3})
x3 = Term(superscript={7}, subscript={3, 5, 6}) + Term(superscript={7}, subscript={4, 5, 6})
x4 = Term(superscript={13}, subscript={7, 11, 12})

x12 = Term(superscript={10}, subscript={4, 8, 9},
           concatenated_terms=[Term(superscript={3}, subscript={1, 2})])

x23 = Term(superscript={3}, subscript={1, 2},
           concatenated_terms=[Term(superscript={7}, subscript={4, 5, 6})])

x34 = Term(superscript={6}, subscript={3, 5},
           concatenated_terms=[Term(superscript={13}, subscript={7, 11, 12})]) \
      + Term(superscript={6}, subscript={4, 5},
             concatenated_terms=[Term(superscript={13}, subscript={7, 11, 12})])

x13 = Term(superscript={10}, subscript={4, 8, 9},
           concatenated_terms=[Term(superscript={2}, subscript={1},
                                    concatenated_terms=[Term(superscript={7}, subscript={3, 5, 6})])])

x24 = Term(superscript={3}, subscript={1, 2},
           concatenated_terms=[Term(superscript={6}, subscript={4, 5},
                                    concatenated_terms=[Term(superscript={13}, subscript={7, 11, 12})])]) \
      + Term(superscript={3}, subscript={1, 2},
             concatenated_terms=[Term(superscript={6}, subscript={4, 5},
                                      concatenated_terms=[Term(superscript={13}, subscript={7, 11, 12})])])

x14 = Term(superscript={10}, subscript={4, 8, 9},
           concatenated_terms=[Term(subscript={1, 2},
                                    concatenated_terms=[Term(superscript={6}, subscript={3, 5},
                                                             concatenated_terms=[
                                                                 Term(superscript={13}, subscript={7, 11, 12})])])]) \
      + Term(superscript={10}, subscript={4, 8, 9},
             concatenated_terms=[Term(superscript={2}, subscript={1},
                                      concatenated_terms=[Term(subscript={3, 5, 6},
                                                               concatenated_terms=[
                                                                   Term(superscript={13}, subscript={7, 11, 12})])])])


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


cobound_term_1 = Term(subscript={1, 2, 3})
cobound_result_1 = Term(superscript={3}, subscript={1, 2})


class TestCobound:
    def test_cobound_zero(self):
        assert cobound(term_zero) == term_zero

    def test_cobound_simple(self):
        assert cobound(cobound_term_1) == cobound_result_1


cobound_result_x12 = Term(superscript={10}, subscript={4, 8, 9},
                          concatenated_terms=[Term(superscript={3}, subscript={1, 2})])
cobound_result_x23 = Term(superscript={3}, subscript={1, 2},
                          concatenated_terms=[Term(superscript={7}, subscript={4, 5, 6})])


class TestCombination:
    def test_cobound_and_multiplication_simple(self):
        assert cobound(x1 * x2) == cobound_result_x12

    def test_cobound_and_multiplication_and_addition(self):
        assert cobound(x2 * x3) == cobound_result_x23


class TestFourfold:
    def test_fourfold(self):
        test_x12, test_x23, test_x34, test_x13, test_x24, test_x14 = fourfold(x1, x2, x3, x4)
        assert test_x12 == x12
        assert test_x23 == x23
        assert test_x34 == x34
        assert str(test_x13) == str(x13)
        assert str(test_x24) == str(x24)
        assert str(test_x14) == str(x14)
