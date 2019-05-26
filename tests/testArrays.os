def on_global_testArrays():
    """Array Test"""

    l = [2, 4, 8]
    sum = 0
    for i in l:
        for j in [1, 2, 3]:
            prod = mult(i, j)
        sum = add(sum, prod)