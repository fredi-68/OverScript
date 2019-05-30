@event("player", "all", "all")
def myNewRule():
    player.my_variable = [1, 2, 3]
    appendToArray(player.my_variable, 4)

def testUtilityFunction(a, b):
    return a + b