from typing import Union, Set
from copy import deepcopy
from collections import Counter


class Term:
    def __init__(self, subscript: Union[Counter, Set] = None,
                 superscript: Union[Counter, Set] = None,
                 is_zero: bool = False,
                 concatenated_terms=None,
                 ancestor=None):
        self.subscript = Counter(subscript) if subscript is not None else Counter()
        self.superscript = Counter(superscript) if superscript is not None else Counter()
        self.is_zero = is_zero
        self.concatenated_terms = concatenated_terms if concatenated_terms is not None else list()
        self.ancestor = ancestor

        if self.is_zero:
            self.nullify()

        if concatenated_terms:
            for concat_term in concatenated_terms:
                concat_term.ancestor = self

    def __repr__(self):
        if self.is_zero:
            return '0'
        else:
            superscript_str = ''
            subscript_str = ''
            concatenated_terms_str = ''
            if self.superscript:
                superscript_str = f'superscript={{{",".join(repr(n) for n in sorted(self.superscript.elements()))}}}'
            if self.subscript:
                subscript_str = f'subscript={{{",".join(repr(n) for n in sorted(self.subscript.elements()))}}}'
            if self.concatenated_terms:
                concatenated_terms_str = \
                    f'concatenated_terms=[{",".join([repr(term) for term in self.concatenated_terms])}]'
            nonempty_argument_strings = \
                [string for string in [superscript_str, subscript_str, concatenated_terms_str] if string]
            string_repr = f'Term({", ".join(nonempty_argument_strings)})'
        return string_repr

    def __str__(self):
        if self.is_zero:
            return '0'
        else:
            superscript_str = ''
            subscript_str = ''
            concatenated_terms_str = ''
            if self.superscript:
                superscript_str = f'^{{{",".join(str(n) for n in sorted(self.superscript.elements()))}}}'
            if self.subscript:
                subscript_str = f'_{{{",".join(str(n) for n in sorted(self.subscript.elements()))}}}'
            if self.concatenated_terms:
                concatenated_terms_str = \
                    f'[{",".join([str(term) for term in self.concatenated_terms])}]'
            nonempty_argument_strings = \
                [string for string in [superscript_str, subscript_str, concatenated_terms_str] if string]
            string_repr = f'e{"".join(nonempty_argument_strings)}'
        return string_repr

    def __mul__(self, other):
        return multiply_terms(first_term=self, second_term=other)

    def __rmul__(self, other):
        return multiply_terms(first_term=other, second_term=self)

    def __add__(self, other):
        return SumOfTerms((self, other))

    def __radd__(self, other):
        return SumOfTerms((other, self))

    def __eq__(self, other):
        if self.is_zero:
            return other.is_zero
        if not self.concatenated_terms:
            return self.superscript == other.superscript and self.subscript == other.subscript
        else:
            self_items = self.concatenated_terms
            other_items = other.concatenated_terms
            return len(self_items) == len(other_items) and all(x == y for x, y in zip(self_items, other_items))

    def get_total_numbers(self, recursive=False):
        """ Calculate and return total numbers count in both
            subscript and superscript and concatenated terms. """
        if self.is_zero:
            return Counter()
        total_numbers = self.superscript + self.subscript
        if recursive:
            for term in self.concatenated_terms:
                total_numbers += term.get_total_numbers(recursive=True)
        return total_numbers

    def nullify(self):
        """ If a term becomes zero, backtrack through its ancestor chain,
            turn them all to zeroes as well and delete connections. """
        self.is_zero = True
        self.subscript = None
        self.superscript = None
        self.concatenated_terms = None
        if self.ancestor is not None:
            self.ancestor.nullify()

    def search_term_by_number(self, number):
        """ Search a defined number in the term and its concatenated descendants
            and return the term where it is found. """
        if number in self.subscript or number in self.superscript:
            return self
        if not self.concatenated_terms:
            return None
        else:
            for search_term in self.concatenated_terms:
                search_result = search_term.search_term_by_number(number)
                if search_result:
                    return search_result


class SumOfTerms:
    def __init__(self, terms):
        self.terms = list()
        for term in terms:
            if isinstance(term, SumOfTerms):
                self.terms.extend(term.terms)
            else:
                if term.is_zero:
                    continue
                self.terms.append(term)

    def __repr__(self):
        string_repr = ' + '.join(repr(term) for term in self.terms)
        return string_repr

    def __str__(self):
        string_str = ' + '.join(str(term) for term in self.terms)
        return string_str

    def __add__(self, other):
        if isinstance(other, SumOfTerms):
            self.terms.extend(other.terms)
            return self
        elif isinstance(other, Term) and not other.is_zero:
            self.terms.append(other)
            return self

    def __mul__(self, other):
        return multiply_terms(first_term=self, second_term=other)

    def __rmul__(self, other):
        return multiply_terms(first_term=other, second_term=self)

    def __eq__(self, other):
        return isinstance(other, SumOfTerms) \
               and len(self.terms) == len(other.terms) \
               and all(x == y for x, y in zip(self.terms, other.terms))


class ScalarMultiplication:
    def __init__(self, scalar: int, term):
        self.scalar = scalar
        self.term = term

    def __repr__(self):
        string_repr = f'{self.scalar}*({str(self.term)})'
        return string_repr


def total(counter: Counter) -> int:
    """ Small helper function returning the sum of counter values"""
    return sum(counter.values())


def first(counter: Counter):
    """ Small helper function returning a value from the counter"""
    return next(iter(counter))


def multiply_elementary_terms(first_term: Term, second_term: Term) -> Union[Term, SumOfTerms]:
    """ Multiply two elementary (non-sum and non-concatenated) terms. """
    if first_term.is_zero or second_term.is_zero:
        return Term(is_zero=True)

    first_sub = first_term.subscript or Counter()
    second_sub = second_term.subscript or Counter()
    first_super = first_term.superscript or Counter()
    second_super = second_term.superscript or Counter()

    first_numbers = first_term.get_total_numbers(recursive=True)
    second_numbers = second_term.get_total_numbers(recursive=True)
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
        return Term(subscript=first_sub, superscript=(first_super + second_super))

    # If first subscript is a single number that is present in the second subscript,
    #   extend second superscript with the first superscript
    if total(first_sub) == 1 and total(second_sub) >= 1 and first(first_sub) in second_sub:
        return Term(subscript=second_sub, superscript=(second_super + first_super))

    if total(first_super) == 1 and first(first_super) in second_sub:
        main_term = Term(subscript=first_sub)
        concatenated_term = Term(superscript=second_super, subscript=second_sub, ancestor=main_term)
        main_term.concatenated_terms.append(concatenated_term)
        return main_term

    if total(second_super) == 1 and first(second_super) in first_sub:
        main_term = Term(superscript=first_super, subscript=first_sub)
        concatenated_term = Term(subscript=second_sub, ancestor=main_term)
        main_term.concatenated_terms.append(concatenated_term)
        return main_term

    if len(first_super) == 1 and first_super == second_super:
        first_main_term = Term(superscript=first_super, subscript=first_sub)
        first_concatenated_term = Term(subscript=second_sub, ancestor=first_main_term)
        first_main_term.concatenated_terms.append(first_concatenated_term)
        second_main_term = Term(subscript=first_sub)
        second_concatenated_term = Term(superscript=first_super, subscript=second_sub, ancestor=second_main_term)
        second_main_term.concatenated_terms.append(second_concatenated_term)
        return SumOfTerms((first_main_term, second_main_term))

    # The options above cover every defined path in the pdf, so if we reached this point, something went wrong
    raise ValueError(f'Error while multiplying terms: {str(first_term)} and {str(second_term)}')


def multiply_single_terms(first_term: Term, second_term: Term) -> Union[Term, SumOfTerms]:
    """ Multiply single terms that may have concatenated elements."""
    first_numbers = first_term.get_total_numbers(recursive=True)
    second_numbers = second_term.get_total_numbers(recursive=True)
    total_numbers_in_common = total(first_numbers & second_numbers)

    # If terms have two or more numbers in common, return 0
    if total_numbers_in_common > 1:
        return Term(is_zero=True)

    # If no numbers in common, return 0 and show a warning
    if total_numbers_in_common == 0:
        print(f'Warning: zero numbers in common between {str(first_term)} and {str(second_term)}')
        return Term(is_zero=True)

    if not first_term.concatenated_terms and not second_term.concatenated_terms:
        return multiply_elementary_terms(first_term, second_term)

    # Find the nodes in first and second trees that have a number in common,
    # replace that node in the first tree with the multiplication product of those nodes
    # then attach the rest of the second tree to that node, relative to its position in the second tree
    common_number = first(first_numbers & second_numbers)
    first_term_multiplication_node = first_term.search_term_by_number(common_number)
    second_term_multiplication_node = second_term.search_term_by_number(common_number)
    node_multiplication_product = multiply_elementary_terms(first_term_multiplication_node,
                                                            second_term_multiplication_node)
    if isinstance(node_multiplication_product, SumOfTerms):
        multiplication_products = node_multiplication_product.terms
    else:
        multiplication_products = [node_multiplication_product]

    overall_multiplication_products = list()
    for product_node in multiplication_products:
        if not product_node or product_node.is_zero:
            continue
        copied_first_term = deepcopy(first_term)
        copied_second_term = deepcopy(second_term)
        copied_first_node = copied_first_term.search_term_by_number(common_number)
        copied_second_node = copied_second_term.search_term_by_number(common_number)

        if copied_first_node.ancestor:
            copied_first_node.ancestor.concatenated_terms.remove(copied_first_node)
            product_node.ancestor = copied_first_node.ancestor
            copied_first_node.ancestor.concatenated_terms.append(product_node)
        else:
            copied_first_term = product_node

        # In case elementary multiplication returns not just a single term, but an already concatenated node X1~X2,
        # we want to attach the rest of the tree to the node X2, not X1
        extension_point = product_node.concatenated_terms
        if product_node.concatenated_terms:
            extension_point = product_node.concatenated_terms[0].concatenated_terms

        if copied_second_node.ancestor:
            reversed_second_ancestor_tree = reverse_tree(copied_second_node)
            extension_point.extend(reversed_second_ancestor_tree.concatenated_terms)

        if copied_first_node.concatenated_terms:
            extension_point.extend(copied_first_node.concatenated_terms)
        if copied_second_node.concatenated_terms:
            extension_point.extend(copied_second_node.concatenated_terms)

        overall_multiplication_products.append(copied_first_term)

    if len(overall_multiplication_products) == 0:
        return Term(is_zero=True)
    if len(overall_multiplication_products) == 1:
        return overall_multiplication_products[0]
    else:
        return SumOfTerms(terms=overall_multiplication_products)


def reverse_tree(root_node: Term):
    above_node = root_node.ancestor
    if above_node:
        above_node.concatenated_terms.remove(root_node)
        root_node.concatenated_terms.append(above_node)
        reverse_tree(root_node=above_node)
        above_node.ancestor = root_node
    return root_node


def multiply_terms(first_term: Union[Term, SumOfTerms], second_term: Union[Term, SumOfTerms]) -> \
        Union[Term, SumOfTerms]:
    """ Multiply simple and complex terms and their sums (the most general function)."""
    if not isinstance(first_term, SumOfTerms) and not isinstance(second_term, SumOfTerms):
        return multiply_single_terms(first_term, second_term)

    if isinstance(first_term, SumOfTerms):
        first_terms = first_term.terms
    else:
        first_terms = [first_term]
    if isinstance(second_term, SumOfTerms):
        second_terms = second_term.terms
    else:
        second_terms = [second_term]

    multiplication_products = list()
    for i in first_terms:
        for j in second_terms:
            product = i * j
            if isinstance(product, SumOfTerms):
                multiplication_products.extend(product.terms)
            elif isinstance(product, Term) and not product.is_zero:
                multiplication_products.append(i * j)

    if not multiplication_products:
        return Term(is_zero=True)
    elif len(multiplication_products) == 1:
        return multiplication_products[0]
    else:
        return SumOfTerms(multiplication_products)


def cobound_elementary_term(term: Term):
    """ Apply cobound function to a single elementary term. """
    if term.is_zero:
        return Term(is_zero=True)
    elif not term.superscript:
        max_subscript = Counter([max(term.subscript.elements())])
        subscript_without_max = term.subscript - max_subscript
        cobound_result = Term(superscript=max_subscript,
                              subscript=subscript_without_max,
                              concatenated_terms=term.concatenated_terms)
        if cobound_result.concatenated_terms:
            for concat_term in cobound_result.concatenated_terms:
                concat_term.ancestor = cobound_result
        return cobound_result
    else:
        # raise ValueError(f'Error while trying to apply cobound function to term: {str(term)}')
        return None


def cobound(term: Union[Term, SumOfTerms]):
    if isinstance(term, SumOfTerms):
        return SumOfTerms(terms=[cobound(summed_term) for summed_term in term.terms])

    if not term.superscript:
        return cobound_elementary_term(term)

    cobound_counter = 0  # ensure that the function is applied only once
    if term.concatenated_terms:
        for index, concat_term in enumerate(term.concatenated_terms):
            cobound_result = cobound(concat_term)
            if cobound_result:
                term.concatenated_terms[index] = cobound_result
                cobound_result.ancestor = term
                cobound_counter += 1
    if cobound_counter == 0:
        raise ValueError(f'No elements applicable for cobound fuction found in term {term}')
    if cobound_counter > 1:
        raise ValueError(f'Multiple cobound-applicable elements found in term {term}')
    return term


def fourfold(x1: Union[Term, SumOfTerms],
             x2: Union[Term, SumOfTerms],
             x3: Union[Term, SumOfTerms],
             x4: Union[Term, SumOfTerms]):
    """ The main fourfold function. """
    x12 = cobound(x1 * x2)
    x23 = cobound(x2 * x3)
    x34 = cobound(x3 * x4)
    x13 = cobound((x1 * x23) + (x12 * x3))
    x24 = cobound((x2 * x34) + (x23 * x4))
    x14 = (x1 * x24) + (x12 * x34) + (x13 * x4)
    return x12, x23, x34, x13, x24, x14


def main():
    x1 = Term(superscript={10}, subscript={4, 8, 9})
    x2 = Term(superscript={4}, subscript={1, 2, 3})
    x3 = Term(superscript={7}, subscript={3, 5, 6}) + Term(superscript={7}, subscript={4, 5, 6})
    x4 = Term(superscript={13}, subscript={7, 11, 12})
    # x5 = Term(superscript={13}, subscript={7, 11, 12}, concatenated_terms=[x3,x4]) - concatenation syntax

    x12, x23, x34, x13, x24, x14 = fourfold(x1, x2, x3, x4)
    print('Reprs:')
    print(f'x12={repr(x12)}')
    print(f'x23={repr(x23)}')
    print(f'x34={repr(x34)}')
    print(f'x13={repr(x13)}')
    print(f'x24={repr(x24)}')
    print(f'x14={repr(x14)}')

    print('\nStrs:')
    print(f'x12={str(x12)}')
    print(f'x23={str(x23)}')
    print(f'x34={str(x34)}')
    print(f'x13={str(x13)}')
    print(f'x24={str(x24)}')
    print(f'x14={str(x14)}')


if __name__ == '__main__':
    main()
