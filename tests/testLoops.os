@event("global")
def my_function():
    some_var = []
    i = 0
    while i < 10:
        appendToArray(some_var, i)
        i += 1