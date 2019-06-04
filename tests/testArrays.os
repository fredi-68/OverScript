@event("global")
def test_arrays():

    """
    This test covers array literals, looping
    over arrays, arithmetic and nested for loops.
    It calculates the number 84 really inefficiently
    and stores it in the variable 'sum'
    """

    l = [2, 4, 8]
    sum = 0
    for i in l:
        for j in range(1, 4):
            prod = i * j
            sum += prod