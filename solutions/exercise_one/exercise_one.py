"""
This file is a proposed solution to a task number one from TE-MPE-CB - coding exercise one.

The task is:
Write a function that detects all duplicate elements in a list: given a list of objects,
it returns a list that contains only those that are duplicated, in the order that they appeared
for the first time in the original list.

For example, for the input ["b", "a", "c", "c", "e", "a", "c", "d", "c", "d"], the answer should be ["a", "c", "d"].

Assumptions taken:
    - since the function is type hinted, one can assume the function will be indeed given a list, and no runtime typechecking will be done,
    - since it was not specified, we cannot assume list will contain objects of uniform data type,
    - we also assume that objects given may not be hashable, which prohibits use of more efficient
      built-in types such as sets for the solution,
    - some types have direct typecasting strategy that suggest equivalence of content, while the type itself is different,
      this function will uphold this automatic pythonic typecasting strategy (e.g. `1. == 1` , `1 == True` etc.).

Improvement ideas:
    - if we are given hashable objects, we could immediately go to dicts and reduce complexity to O(n) if optimistic, O(n2) if pessimistic
    - one could make checking stricter (with performance consequences) to prevent, situations like in list3 example, where gets
      duplicates detected, due to typecasting
"""


# system imports
# third-party imports
# local imports

def detect_duplicate_elements(elements: list) -> list:
    """Detects duplicate objects in a given list and returns them in order defined by their respective occurrence.

    Args:
        elements (list): list of objects with possible duplicates

    Returns:
        list: list of duplicate objects in the `elements` list ordered in FIFO.
              If there are no duplicates, returns an empty list.

    """

    duplicate_list = []                          # define duplicate list to hold duplicate objects
    ordered_unique_list = []                     # define ordered list of unique objects

    for element in elements:
        if element not in ordered_unique_list:
            # adding unique elements while respecting their ordering
            ordered_unique_list.append(element)
        else:
            if element not in duplicate_list:
                # adding duplicate elements
                duplicate_list.append(element)

    # one liner which creates desired output by selecting duplicate elements from ordered unique object list
    output_list = [unique_element
                   for unique_element in ordered_unique_list
                   if unique_element in duplicate_list]
    return output_list


# examples
if __name__ == "__main__":
    list1 = ["b", "a", "c", "c", "e", "a", "c", "d", "c", "d"]
    assert detect_duplicate_elements(list1) == ["a", "c", "d"]

    list2: list = []
    assert detect_duplicate_elements(list2) == []

    list3 = ["a", 0, 0., "a", True, [], (), ["a"], None, (1,), 1]
    assert detect_duplicate_elements(list3) == ["a", 0, 1]

    list4 = [('a',), 'a']
    assert detect_duplicate_elements(list4) == []

    list5 = [[1, 2, 3], 1, 2, 3, [1, 2], [1, 2, 3]]
    assert detect_duplicate_elements(list5) == [[1, 2, 3]]
