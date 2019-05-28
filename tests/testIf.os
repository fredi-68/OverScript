@event("player", "all", "all")
def my_second_function():
    if heroOf(player) == Hero("Lúcio"):
        bestHero = True
    else:
        bestHero = False

@event("player", "all", "all")
def my_third_function():
    if heroOf(player) == Hero("Lúcio"):
        bestHero = True