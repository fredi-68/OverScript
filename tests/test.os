@event("player", "all", "all")
def myNewRule():
    player.my_variable = [1, 2, 3]
    my_global = player.my_variable[0]

def testUtilityFunction(a, b):
    return a + b