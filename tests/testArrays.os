def on_global_testArrays():
    """Array Test"""

    #This test covers array literals, looping
    #over arrays, arithmetic and nested for loops.
    #It calculates the number 42 really inefficiently
    #and stores it in the variable 'sum'

    l = [2, 4, 8]
    sum = 0
    for i in l:
        for j in [1, 2, 3]:
            prod = i * j
        sum = sum + prod