from typing import Union
from collections import Counter


class Term:
    def __init__(self, subscript=None, superscript=None, is_zero=False, concatenated_terms=None):
        self.subscript = Counter(subscript) if subscript is not None else Counter()
        self.superscript = Counter(superscript) if superscript is not None else Counter()
        self.is_zero = is_zero
        self.concatenated_terms = concatenated_terms if concatenated_terms is not None else list()

        if self.is_zero:
            self.subscript = None
            self.superscript = None
            self.concatenated_terms = None

    def __str__(self):
        if self.is_zero:
            return '0'
        else:
            superscript_str = ''
            subscript_str = ''
            concatenated_terms_str = ''
            if self.superscript:
                superscript_str = f'superscript={{{",".join(str(n) for n in self.superscript.elements())}}}'
            if self.subscript:
                subscript_str = f'subscript={{{",".join(str(n) for n in self.subscript.elements())}}}'
            if self.concatenated_terms:
                concatenated_terms_str = \
                    f'concatenated_terms=[{",".join([str(term) for term in self.concatenated_terms])}]'
            nonempty_argument_strings = \
                [string for string in [superscript_str, subscript_str, concatenated_terms_str] if string]
            string_repr = f'Term({", ".join(nonempty_argument_strings)})'
        return string_repr

    def __mul__(self, other):
        return multiply_elementary_terms(first_term=self, second_term=other)

    def __rmul__(self, other):
        return multiply_elementary_terms(first_term=other, second_term=self)

    def __eq__(self, other):
        if self.is_zero:
            return other.is_zero
        if not self.concatenated_terms:
            return self.superscript == other.superscript and self.subscript == other.subscript

    def get_total_numbers(self, recursive=False):
        """ Calculate and return the set of total numbers """
        total_numbers = self.superscript + self.subscript
        if recursive:
            for term in self.concatenated_terms:
                total_numbers += term.get_total_numbers(recursive=True)
        return total_numbers


class SumOfTerms:
    def __init__(self, *terms):
        self.terms = list(terms) if terms is not None else list()

    def __str__(self):
        string_repr = ' + '.join(str(term) for term in self.terms)
        return string_repr

    def __add__(self, other):
        if isinstance(other, SumOfTerms):
            self.terms.extend(other.terms)
            return self.terms
        elif isinstance(other, Term):
            self.terms.append(other)
            return self.terms


class ScalarMultiplication:
    def __init__(self, scalar: int, term):
        self.scalar = scalar
        self.term = term

    def __str__(self):
        string_repr = f'{self.scalar}*({str(self.term)})'
        return string_repr


def total(counter: Counter) -> int:
    """ Small helper function returning the sum of counter values"""
    return sum(counter.values())


def first(counter: Counter):
    """ Small helper function returning a random value from the counter"""
    return next(iter(counter))


def multiply_elementary_terms(first_term: Term, second_term: Term) -> \
        Union[Term, SumOfTerms]:
    """ Multiply two elementary (non-concatenated) terms and return the result. """
    if first_term.is_zero or second_term.is_zero:
        return Term(is_zero=True)

    first_sub = first_term.subscript or Counter()
    second_sub = second_term.subscript or Counter()
    first_super = first_term.superscript or Counter()
    second_super = second_term.superscript or Counter()

    first_numbers = first_term.get_total_numbers()
    second_numbers = second_term.get_total_numbers()
    total_numbers_in_common = total(first_numbers & second_numbers)

    # If terms have two or more numbers in common, return 0
    if total_numbers_in_common > 1:
        return Term(is_zero=True)

    # If both subscripts are longer than 1 and coincide in at least one number, return 0
    if total(first_sub) > 1 and total(second_sub) > 1 and total(first_sub & second_sub) > 0:
        return Term(is_zero=True)

    # If second subscript is a single number that is present in the first subscript,
    #   extend first superscript with the second superscript
    if total(second_sub) == 1 and total(first_sub) >= 1 and first(second_sub) in first_sub:
        return Term(subscript=first_sub, superscript=first_super.union(second_super))

    # If first subscript is a single number that is present in the second subscript,
    #   extend second superscript with the first superscript
    if total(first_sub) == 1 and total(second_sub) >= 1 and next(iter(first_sub)) in second_sub:
        return Term(subscript=second_sub, superscript=second_super.union(first_super))

    if len(first_super) == 1 and len(second_super) > 1 and next(iter(first_super)) in second_sub:
        main_term = Term(subscript=first_sub)
        concatenated_term = Term(superscript=second_super, subscript=second_sub)
        main_term.concatenated_terms.append(concatenated_term)
        return main_term

    if len(second_super) == 1 and len(first_super) > 1 and next(iter(second_super)) in first_sub:
        main_term = Term(superscript=first_super, subscript=first_sub)
        concatenated_term = Term(subscript=second_sub)
        main_term.concatenated_terms.append(concatenated_term)
        return main_term

    if len(first_super) == 1 and first_super == second_super:
        first_main_term = Term(superscript=first_super, subscript=first_sub)
        first_concatenated_term = Term(subscript=second_sub)
        first_main_term.concatenated_terms.append(first_concatenated_term)
        second_main_term = Term(subscript=first_sub)
        second_concatenated_term = Term(superscript=first_super, subscript=second_sub)
        second_main_term.concatenated_terms.append(second_concatenated_term)
        return SumOfTerms(first_main_term, second_main_term)

    # The options above cover every defined path in the pdf, so if we reached this point, something went wrong
    raise ValueError('Error while multiplying terms')


def fourfold():
    pass
