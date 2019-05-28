@event("player", "all", "all")
def my_second_function():
    """Testing Control Flow"""
    if heroOf(player) == Hero("Lúcio"):
        bestHero = True
    else:
        bestHero = False

@event("player", "all", "all")
def my_third_function():
    """Testing Control Flow 2"""
    if heroOf(player) == Hero("Lúcio"):
        bestHero = True