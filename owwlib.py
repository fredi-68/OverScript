#Collection of Overwatch Workshop function calls
#TODO: Extend this to cover all workshop actions and values

#======================
#ACTIONS
#======================

def wait(time, ctx):
    return "Wait(%s, Ignore Condition)" % ctx._parseExpr(time)

def appendToArray(array, element, ctx):
    #TODO: This currently only works for global variables as array targets
    return ctx.modifyVariable(array.id, "Append To Array", ctx._parseExpr(element))

def applyImpulse(player, direction, speed, relative, motion, ctx):
    return "Apply Impulse(%s, %s, %s, %s, %s)" % (ctx._parseExpr(player), ctx._parseExpr(direction), ctx._parseExpr(speed), ctx._parseExpr(relative), ctx._parseExpr(motion))

#======================
#VALUES
#======================

#-----------
#Arithmetic
#-----------
def add(target, value, ctx):
    return "Add(%s, %s)" % (ctx._parseExpr(target), ctx._parseExpr(value))

def mult(value1, value2, ctx):
    return "Multiply(%s, %s)" % (ctx._parseExpr(value1), ctx._parseExpr(value2))

#-----------
#Datatypes
#-----------

def Vector(x, y, z, ctx):
    return "Vector(%s, %s, %s)" % (ctx._parseExpr(x), ctx._parseExpr(y), ctx._parseExpr(z))

def Hero(h, ctx):
    return "Hero(%s)" % ctx._parseExpr(h)

#-----------
#Other
#-----------

def heroOf(player, ctx):
    return "HeroOf(%s)" % ctx._parseExpr(player)

def isButtonHeld(player, button, ctx):
    return "Is Button Held(%s, %s)" % (ctx._parseExpr(player), ctx._parseExpr(button))

#======================
#BUILTIN PYTHON FUNCTIONS
#======================

def range(start, end, step, ctx):

    return ctx._createArray(range(start, end, step))

#======================
#OTHER
#======================