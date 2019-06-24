#Collection of Overwatch Workshop function calls

#This module contains a number of functions callable from within
#OverScript. Each function takes a variable amount of arguments,
#however, it is always passed at least one argument, which is
#the current compiler instance. Thus, each function defined here
#has access to the complete compiler state, variable mappings,
#loop and function stacks and already defined rules and actions.
#The function then may insert an arbitrary amount of actions
#into the current rule before returning.
#Each function should return a string specifying the value or
#action requested for the current context.

#TODO: Extend this to cover all workshop actions and values

#Copyright (c) 2019 fredi_68

#Permission is hereby granted, free of charge, to any person obtaining a copy
#of this software and associated documentation files (the "Software"), to deal
#in the Software without restriction, including without limitation the rights
#to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
#copies of the Software, and to permit persons to whom the Software is
#furnished to do so, subject to the following conditions:

#The above copyright notice and this permission notice shall be included in all
#copies or substantial portions of the Software.

#THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
#IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
#FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
#AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
#LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
#OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
#SOFTWARE.

#make sure to define builtins that we will override
#so we can still access them later
_range = __builtins__["range"]
_input = __builtins__["input"]

#======================
#ACTIONS
#======================

def wait(ctx, time, cond=None):
    if cond is None:
        cond = "Ignore Condition"
    else:
        cond = ctx._parseExpr(cond)
    return "Wait(%s, %s)" % (ctx._parseExpr(time), cond)

def appendToArray(ctx, array, element):
    return "Append To Array(%s, %s)" % (ctx._parseExpr(array), ctx._parseExpr(element))

def applyImpulse(ctx, player, direction, speed, relative, motion):
    return "Apply Impulse(%s, %s, %s, %s, %s)" % (ctx._parseExpr(player), ctx._parseExpr(direction), ctx._parseExpr(speed), ctx._parseExpr(relative), ctx._parseExpr(motion))

def bigMessage(ctx, visibleTo, header):
    return "Big Message(%s, %s)" % (ctx._parseExpr(visibleTo), ctx._parseExpr(header))

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

def vector(ctx, x, y, z):
    return "Vector(%s, %s, %s)" % (ctx._parseExpr(x), ctx._parseExpr(y), ctx._parseExpr(z))

def hero(ctx, h):
    return "Hero(%s)" % ctx._parseExpr(h)

def backward(ctx):
    return "Backward"

def team(ctx, team):
    return "Team(%s)" % ctx._parseExpr(team)

def victim(ctx):
    return "Victim"

def attacker(ctx):
    return "Attacker"

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

def closestPlayerTo(ctx, center, team):
    return "Closest Player To(%s, %s)" % (ctx_parseExpr(center, team))

def countOf(ctx, array):
    return "Count Of(%s)" % ctx._parseExpr(array)

#======================
#BUILTIN PYTHON FUNCTIONS
#======================

#These functions are builtin Python functions,
#made available to workshop scripts for convenience.
#Unless stated otherwise, these functions do NOT convert
#to workshop instructions, but are merely shorthands for
#literal values or transformations on them.
#In most cases, passing non literal values as arguments
#will result in compiler errors.

def range(ctx, *args):

    #Bit dodgy this, may want to revise
    return ctx._create_1d_array(_range(*map(lambda x: int(ctx._parseExpr(x)), args)))

len = countOf

#======================
#OTHER
#======================

#I/O
def input(ctx, var, player=None):

    var = ctx._parseExpr(var)
    if var in ctx.used_vars:
        raise RuntimeError("Use of external variable %s prohibited: Variable is already in use by the compiler." % var)

    if player is not None:
        player = ctx._parseExpr(player)
        return "Player Variable(%s, %s)" % (player, var)

    return "Global Variable(%s)" % var

def output(ctx, value, var, player=None):

    var = ctx._parseExpr(var)
    if var in ctx.used_vars:
        raise RuntimeError("Use of external variable %s prohibited: Variable is already in use by the compiler." % var)

    if player is not None:
        player = ctx._parseExpr(player)
        return "Set Player Variable(%s, %s, %s)" % (player, var, ctx._parseExpr(value))

    return "Set Global Variable(%s, %s)" % (var, ctx._parseExpr(value))