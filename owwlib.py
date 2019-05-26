#Collection of Overwatch Workshop function calls
#TODO: Extend this to cover all workshop actions and values

#======================
#ACTIONS
#======================

def wait(ctx, time):
    return "Wait(%s, Ignore Condition)" % ctx._parseExpr(time)

def appendToArray(ctx, array, element):
    #TODO: This currently only works for global variables as array targets
    return ctx.modifyVariable(array.id, "Append To Array", ctx._parseExpr(element))

def applyImpulse(ctx, player, direction, speed, relative, motion):
    return "Apply Impulse(%s, %s, %s, %s, %s)" % (ctx._parseExpr(player), ctx._parseExpr(direction), ctx._parseExpr(speed), ctx._parseExpr(relative), ctx._parseExpr(motion))

#======================
#VALUES
#======================

#-----------
#Arithmetic
#-----------

def abs(ctx, x):
    return "Absolute Value(%s)" % ctx._parseExpr(x)

#-----------
#Datatypes
#-----------

def Vector(ctx, x, y, z):
    return "Vector(%s, %s, %s)" % (ctx._parseExpr(x), ctx._parseExpr(y), ctx._parseExpr(z))

def Hero(ctx, h):
    return "Hero(%s)" % ctx._parseExpr(h)

def Backward(ctx):
    return "Backward"

#-----------
#Other
#-----------

def heroOf(ctx, player):
    return "HeroOf(%s)" % ctx._parseExpr(player)

def isButtonHeld(ctx, player, button):
    return "Is Button Held(%s, %s)" % (ctx._parseExpr(player), ctx._parseExpr(button))

def allDeadPlayers(ctx, team):
    return "All Dead Players(%s)" % ctx._parseExpr(team)

def allHeroes(ctx):
    return "All Heroes()"

def allLivingPlayers(ctx, team):
    return "All Living Players(%s)" % ctx._parseExpr(team)

def allPlayers(ctx, team):
    return "All Players(%s)" % ctx._parseExpr(team)

def allPlayersNotOnObjective(ctx, team):
    return "All Players Not On Objective(%s)" % ctx._parseExpr(team)

def allPlayersOnObjective(ctx, team):
    return "All Players On Objective(%s)" % ctx._parseExpr(team)

def allowedHeroes(ctx, player):
    return "Allowed Heroes(%s)" % ctx._parseExpr(player)

def altitudeOf(ctx, player):
    return "Altitude Of(%s)" % ctx._parseExpr(player)

def angleDifference(ctx, value1, value2):
    return "Angle Difference(%s, %s)" % (ctx._parseExpr(value1), ctx._parseExpr(value2))

def arrayContains(ctx, array, value):
    return "Array Contains(%s, %s)" % (ctx._parseExpr(array), ctx._parseExpr(value))

def arraySlice(ctx, array, start, count):
    return "Array Slice(%s, %s, %s)" % (ctx._parseExpr(array), ctx._parseExpr(start), ctx._parseExpr(count))

#======================
#BUILTIN PYTHON FUNCTIONS
#======================

def range(ctx, start, end, step):

    return ctx._createArray(range(start, end, step))

#======================
#OTHER
#======================