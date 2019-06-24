#AST walker for Python that creates Overwatch Workshop scripts

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


import ast
import logging
import json

import owwlib
from string_parser import StringParser

EVENTS = {
    "player": "Ongoing - Each Player",
    "global": "Ongoing - Global",
    "elimination": "Player earned elimination",
    "final_blow": "Player dealt final blow",
    "damage_dealt": "Player dealt damage",
    "damage_taken": "Player took damage",
    "death": "Player Died"
    }

OPERATORS = {
    "Eq": "==",
    "Lt": "<",
    "NotEq": "!=",
    "Gt": ">",
    "LtE": "<=",
    "GtE": ">="
    }

class FunctionReturned(Exception):

    """
    Exception that is raised when a function returns
    """

    def __init__(self, value):
        self.value = value
        return super().__init__()

class TOS():

    """
    Top Of Stack wrapper class providing
    mutable integers because I'm lazy
    """

    def __init__(self):

        self.i = 0

class Rule():

    """
    Dataclass for Overwatch Workshop rules
    """

    def __init__(self, name, events, docstring=""):

        """
        Create a new rule.
        name is the name of the rule and will be displayed in
        the rule browser in the game.
        events should be a tuple containing string arguments
        used for determining event type.
        docstring if provided, should be a string which will
        be inserted into the final code as a comment
        """

        self.name = name
        self.docstring = docstring
        self.events = events
        self.conditions = []
        self.actions = []
        self.lastLoopBranch = 0
        self.loopCount = 0

    def isGlobal(self):

        """
        Check whether or not this rule uses global or player specific events.
        """

        return self.events[0] == EVENTS["global"]

    def __str__(self):

        events = """\tevent\n\t{\n\t\t%s\n\t}\n""" % "\n\t\t".join(map(lambda x: x.title()+";", self.events))
        conditions = """\tconditions\n\t{\n\t\t%s\n\t}\n""" % "\n\t\t".join(map(lambda x: x+";", self.conditions))
        actions = """\tactions\n\t{\n\t\t%s\n\t}\n""" % "\n\t\t".join(map(lambda x: x, self.actions))

        docstring = ""
        if self.docstring:
            docstring = "/*\n%s\n*/\n" % self.docstring

        return """rule("%s")\n%s{\n%s\n%s\n%s}\n""" % (self.name, docstring, events, conditions, actions)

class OverScriptCompiler():

    """
    OverScript Python to Overwatch Workshop compiler.

    This compiler is capable of turning simple Python scripts
    into code understood by the Overwatch Workshop scripting engine.
    It offers a number of convenience features such as automatic
    variable substitution, theoretically unlimited variables, utility
    functions, high level control structures and an overall simpler
    and easier to read code syntax.

    In OverScript, programmers don't usually access game variables
    directly but using proxy variables. These do not have to be declared
    explicitly, instead, the compiler will create variables for you when
    you need them.
    High level control structures such as loops and conditionals are
    supported and implemented using standard Python syntax.

    The OWW rules created by OSC require some variables and additional
    rules. This is important to know and respect if you plan on mixing
    OverScript and traditional OWW rules.
    The register assignment is as follows:

        A - [Array] Variables
        B - [Array] Loop branch state
        C - [Array] Loop iteration state
        D - [Array] Array assembly stack
        E - Array assembly source
        F - Array assembly target
    """

    VS_VAR = "A"
    VS_LBS = "B"
    VS_LIS = "C"
    VS_AAS = "D"
    VS_ASR = "E"
    VS_AAT = "F"

    logger = logging.getLogger("OSCompiler")

    def __init__(self, optimize=False, parseUnknownFunctions=False):

        """
        Create a new compiler instance.

        optimize controls the level of output space optimization performed by the compiler.
            The compiler always uses all code optimizations available, but many things such as
            comments or additional linebreaks and spaces for better readability may be omitted
            if optimize=False.
        """

        self.optimize = optimize
        self.parseUnknownFunctions = parseUnknownFunctions
        self.used_vars = (self.VS_VAR, self.VS_LBS, self.VS_LIS, self.VS_AAS, self.VS_ASR, self.VS_AAT)

        self._prepare()
        self.stringParser = StringParser()
        self.HAS_JSON = True
        self.logger.debug("Trying to load workshop.json...")
        try:
            self._load_workshop_json()
        except OSError:
            self.logger.debug("workshop.json not found, WSJSON not available")
            self.HAS_JSON = False

    def _load_workshop_json(self, path="res/workshop.json"):

        self.workshop_functions = {}
        with open(path, "r") as f:
            d = json.load(f)

        def camelCase(x):
            words = x.split(" ")
            if len(words) < 2:
                return words[0].lower()
            return "".join((words[0].lower(), *map(str.title, words[1:])))

        for action in d["actions"]:
            self.workshop_functions[camelCase(action["name"])] = (action["name"].title(), len(action["args"]))

        for value in d["values"]:
            self.workshop_functions[camelCase(value["name"])] = (value["name"].title(), len(value["args"]))

    def _prepare(self):

        self.logger.debug("Clearing cache...")
        self.rules = []
        self._utilityFunctions = {}
        self._usedFunctions = set() #keeps track of functions used in current call stack
        self._currentRule = None
        self._currentComment = ""

        self.global_var_names = {}
        self.player_var_names = {}
        self.func_local_var_names = {}

        self.code = ""

        self._curLoopBranch = 0

    def currentLine(self):

        """
        Returns the current action index.
        """

        return len(self._currentRule.actions)

    def ruleID(self):

        """
        Returns the ID for the current rule.
        """

        return len(self.rules) - 1

    def addAction(self, action):

        """
        Adds an action to the current rule
        """

        self._currentRule.actions.append(action + ";" + (" //" + self._currentComment if self._currentComment and not self.optimize else ""))
        self._currentComment = ""

    def setVariable(self, name, value, player=None):

        """
        Sets a global or player specific variable.
        The variable will be created if it doesn't exist already.
        """

        self._currentComment += "var %s; " % name
        if player is None:
            self.logger.debug("Setting global variable '%s'..." % name)
            if name in self.global_var_names:
                i = self.global_var_names[name]
            else:
                i = len(self.global_var_names)
                self.global_var_names[name] = i
            return "Set Global Variable At Index(A, %i, %s)" % (i, value)

        else:
            self.logger.debug("Setting player variable '%s' for '%s'..." % (name, player))
            if name in self.player_var_names:
                i = self.player_var_names[name]
            else:
                i = len(self.player_var_names)
                self.player_var_names[name] = i
            return "Set Player Variable At Index(%s, A, %i, %s)" % (player, i, value)

    def getVariable(self, name, player=None):

        """
        Gets a global or player specific variable.
        
        """

        self._currentComment += "var %s; " % name
        if player is None:
            if not name in self.global_var_names:
                #create variable

                #we don't actually do anything with the returned string,
                #we just want to update the mapping
                self.setVariable(name, 0, player) 
                #raise NameError("Name '%s' is not defined" % name)
            return "Value In Array(Global Variable(A), %i)" % self.global_var_names[name]
        else:
            if not name in self.player_var_names:
                self.setVariable(name, 0, player)
                #raise NameError("Name '%s' is not defined" % name)
            return "Value In Array(Player Variable(%s, A), %i)" % (player, self.player_var_names[name])

    def modifyVariable(self, name, action, element, player=None):

        """
        Modify a global variable.
        """

        if player is None:
            if not name in self.global_var_names:
                raise NameError("Name '%s' is not defined" % name)
            return "Modify Global Variable At Index(A, %i, %s, %s)" % (self.global_var_names[name], action, element)
        else:
            if not name in self.player_var_names:
                raise NameError("Name '%s' is not defined" % name)
            return "Modify Player Variable At Index(A, %i, %s, %s)" % (self.player_var_names[name], action, element)

    def setLoopBranch(self, instruction):

        """
        Sets the loop branch state to the specified instruction.
        """

        ind = self.ruleID()
        if self._currentRule.isGlobal():
            self.addAction("Set Global Variable At Index(B, %i, %s)" % (ind, instruction))
        else:
            self.addAction("Set Player Variable At Index(Event Player, B, %i, %s)" % (ind, instruction))
        self._curLoopBranch = instruction

    def setLoopIteration(self, iteration):

        """
        Sets the loop iteration state to the specified value.
        """

        #TODO: Clean this up, break it down into multiple steps so it is easier to understand
        ind = self.ruleID()
        if self._currentRule.isGlobal():
            self.addAction("Set Global Variable At Index(C, %i, Append To Array(Array Slice(Value In Array(Global Variable(C), %i), 0, Subtract(Count Of(Value In Array(Global Variable(C), %i)), 1)), %s))" % (ind, ind, ind, iteration))
        else:
            self.addAction("Set Player Variable At Index(Event Player, C, %i, Append To Array(Array Slice(Value In Array(Player Variable(Event Player, C), %i), 0, Subtract(Count Of(Value In Array(Player Variable(Event Player, C), %i)), 1)), %s))" % (ind, ind, ind, iteration))

    def getLoopIteration(self):

        """
        Returns the current loop iteration.
        """

        ind = self.ruleID()
        if self._currentRule.isGlobal():
            return "Last Of(Value In Array(Global Variable(C), %i))" % ind
        else:
            return "Last Of(Value In Array(Player Variable(Event Player, C), %i))" % ind

    def pushLoopIteration(self):
        
        """
        Pushes a loop frame.
        """

        #TODO: Clean this up, break it down into multiple steps so it is easier to understand
        ind = self.ruleID()
        if self._currentRule.isGlobal():
            self.addAction("Set Global Variable At Index(C, %i, Append To Array(Value In Array(Global Variable(C), %i), 0))" % (ind, ind))
        else:
            self.addAction("Set Player Variable At Index(Event Playet, C, %i, Append To Array(Value In Array(Player Variable(Event Player, C), %i), 0))" % (ind, ind))

    def pullLoopIteration(self):

        """
        Pulls a loop frame.
        """

        #TODO: Clean this up, break it down into multiple steps so it is easier to understand
        ind = self.ruleID()
        if self._currentRule.isGlobal():
            self.addAction("Set Global Variable At Index(C, %i, Array Slice(Value In Array(Global Variable(C), %i), 0, Subtract(Count Of(Value In Array(Global Variable(C), %i)), 1)))" % (ind, ind, ind))
        else:
            self.addAction("Set Player Variable At Index(Event Player, C, %i, Array Slice(Value In Array(Player Variable(Event Player, C), %i), 0, Subtract(Count Of(Value In Array(Player Variable(Event Player, C), %i)), 1)))" % (ind, ind, ind))

    def compile(self, source):

        """
        Parses Python source code into an AST and compiles it
        into a script understood by the Overwatch Workshop.
        returns the compiled workshop script.
        """

        self._prepare()
        self.logger.debug("Parsing AST...")
        tree = ast.parse(source)
        assert isinstance(tree, ast.Module)
        self.logger.debug("Reading function definitions...")
        rules = []
        for rule in tree.body:
            if isinstance(rule, ast.FunctionDef):
                if rule.decorator_list:
                    #Event handler function
                    rules.append(rule)
                else:
                    self._parseFunctionDefAsUtility(rule)

        self.logger.debug("Building ruleset...")
        
        #do this after parsing utility functions to prevent issues
        for rule in rules: 
            self._parseFunctionDefAsRule(rule)

        self.code += "\n\n".join(map(str, self.rules))

        self.logger.debug("Done!")
        return self.code

    def _parseFunctionDefAsRule(self, node):

        """
        Parse a function definition as a new rule.
        """

        fName = node.name
        self.logger.debug("Creating new rule from function '%s'" % fName)
        self.logger.debug("Processing rule decorators...")

        event_type = ()
        conditions = []

        for dec in node.decorator_list:
            f = dec.func
            if f.id == "event":
                if not event_type:
                    try:
                        args = list(map(lambda x: x.s, dec.args))
                    except AttributeError:
                        raise TypeError("Event value must be of type str")
                    if args:
                        event_type = (EVENTS[args[0]], *args[1:])
                    else:
                        raise ValueError("@event needs at least one argument")
                else:
                    raise RuntimeError("Only one instance of 'event' decorator allowed per rule.")
            elif f.id == "trigger":
                for arg in dec.args:
                    conditions.append(self._parseExpr(arg) + " == True")
            else:
                raise ValueError("Only 'event' and 'trigger' are allowed as function decorators.")

        #Cleanup
        #conditions may be empty but event_type may not. If it is,
        #we can either raise an exception or substitute a default value.
        #We will use the default Ongoing - Global
        if not event_type:
            event_type = ("Ongoing - Global;",)

        docstr = ast.get_docstring(node)
        skip_docstr = bool(docstr)
        if self.optimize or not skip_docstr:
            docstr = ""

        #create rule
        rule = Rule(fName, event_type, docstring=docstr)
        rule.conditions = conditions
        self._currentRule = rule
        self.rules.append(rule)

        #Parse actions
        for expr in node.body[skip_docstr:]:
            self._parseBody(expr)

        if rule.loopCount > 0:
            #Setup loop branch instruction
            if rule.isGlobal():
                skipAction = "Value In Array(Global Variable(B), %i)" % self.ruleID()
            else:
                skipAction = "Value In Array(Player Variable(%s, B), %i)" % ("Event Player", self.ruleID())
            rule.actions.insert(0, "Skip(%s);" % skipAction)
            rule.actions.insert(0, "Wait(0.001, Ignore Condition);")

    def _resolveUtilityFunction(self, func_name, args, kwargs):

        """
        Resolves a name to a sequence of actions depending on the
        specified func_name function.
        """

        if not func_name in self._utilityFunctions:
            raise ValueError("No such function: '%s'" % func_name)

        if func_name in self._usedFunctions:
            raise RecursionError("Recursion not allowed in utility functions.")

        self._usedFunctions.add(func_name)

        #safety check for recursion
        func = self._utilityFunctions[func_name]

        try:
            for instr in func.body:
                self._parseBody(instr)
        except FunctionReturned as e:
            self._usedFunctions.discard(func_name)
            return e.value
        self._usedFunctions.discard(func_name)
        return None

    def _parseFunctionDefAsUtility(self, node):

        """
        Parse a function definition node as a utility function.
        """

        self._utilityFunctions[node.name] = node
        self.logger.debug("Registered '%s' as utility function." % node.name)

    def _parseBody(self, node):

        """
        Parse a rule body.
        """
        
        if isinstance(node, ast.Assign):
            self.addAction(self._assign(node))
        elif isinstance(node, ast.While):
            self._parseWhile(node)
        elif isinstance(node, ast.If):
            self._parseIf(node)
        elif isinstance(node, ast.Expr):
            self.addAction(self._parseExpr(node.value))
        elif isinstance(node, ast.AugAssign):
            #Since we already have assignment and binary ops wokring,
            #I'm just gonna cheese this one...
            binOpNode = ast.BinOp()
            binOpNode.left = node.target
            binOpNode.right = node.value
            binOpNode.op = node.op
            assignNode = ast.Assign()
            assignNode.targets = [node.target]
            assignNode.value = binOpNode
            self.addAction(self._assign(assignNode))
        elif isinstance(node, ast.For):
            self._parseFor(node)
        elif isinstance(node, ast.Return):
            raise FunctionReturned(self._parseExpr(node.value))
        else:
            raise RuntimeError("Unsupported node %s" % str(node))

    def _parseIf(self, node):

        """
        Parses an If node.
        """

        #If nodes a complicated.
        #An If node has a boolean expression which needs to be evaluated.
        #If it is True, the If block gets executed.
        #If the If node has an optional Orelse node attached, this is
        #executed if the expression evaluates to False.
        
        #However, the OWW works slightly different. It is more akin to
        #how assemblers deal with if statements, that is by branching and
        #jumping. What we need to do is first create the action block for the
        #If block, then check where it starts and ends. Once we have these values
        #we can create the if condition itself using the Skip If action to skip past
        #the if block if the condition isn't met. If we have an else block we insert
        #it here. After that we need to skip the if block in the else block and vice
        #versa.
        
        #First we create the if and else blocks
        body = node.body
        orelse = node.orelse
        ifInd = self.currentLine()
        self.addAction("PLACEHOLDER") #this will later test the condition and skip the else block
        if orelse:
            for i in orelse:
                self._parseBody(i)
        elseInd = self.currentLine()
        self.addAction("PLACEHOLDER") #this will later skip the if block if the else block was executed
        for i in body:
            self._parseBody(i)
        end = self.currentLine()

        self._currentRule.actions[elseInd] = "Skip(%i);" % (end - elseInd - 1) #skip if block in else block

        #Now that we know what our action pointers need to be set to,
        #we can create the actual If statement

        expr = self._parseCompare(node.test)
        self._currentRule.actions[ifInd] = "Skip If(%s, %i);" % (expr, elseInd - ifInd)

    def _parseCompare(self, node):

        """
        Parses a comparison, which is a boolean expression.
        """

        left = self._parseExpr(node.left)
        ops = node.ops
        if len(ops) > 1:
            raise NotImplementedError("Multiple comparison operators are not supported by OverScript.")
        opName = ops[0].__class__.__name__
        if opName in OPERATORS:
            op = OPERATORS[opName]
        elif opName == "In":
            #special case for use with Array Contains
            array = self._parseExpr(node.comparators[0])
            return "Array Contains(%s, %s)" % (array, left)
        else:
            raise NotImplementedError("Unknown operator '%s'." % opName)
        comps = node.comparators
        if len(comps) > 1:
            raise NotImplementedError("Multiple comparators are not supported by OverScript.")
        comp = self._parseExpr(comps[0])
        return "Compare(%s, %s, %s)" % (left, op, comp)

    def _parseWhile(self, node):

        """
        Parses a While node.
        """

        #If you though that If nodes where complicated, think again.
        #The only way (that I can tell) to do while statements in OWW is by abusing
        #the Loop If action. Unfortunately, this always loops from the start of the
        #action list. There is however something we can do to mitigate this, which is
        #keeping track of all loops in the current rule and having a branch at the start
        #which skips to whatever instruction the current loop starts at every time we jump
        #to the beginning. To do this, we would keep track of the target instruction using
        #a variable that we set at the beginning of the action list. Each loop would write
        #its starting position to this variale which then determines the jump target for
        #each loop iteration.
        #something like this:
        #
        #   init array b = 0 //the first action index is 0 because it is what is called by default when no loop is running (no skip)
        #   skip b //skip to wherever the current loop is
        #   ...
        #   [line 24] set b = 24 //this is where the loop starts
        #   ...
        #   Loop If <some condition> //this loops back to the beginning, which will then immediately jump back to line 24
        #   set b = 0 //loop is complete, reset b to make sure the rule can run properly next iteration
        #
        #The problem once again is that we cannot use one variable for all rules since it
        #would introduce race conditions if multiple rules are using loops at the same time.
        #To mitigate this, the variable would have to be an array instead, storing one value
        #for each rule. Ideally, we would even use player variables to store these array for player
        #specific events like Ongoing - Each Player to prevent collisions.
        #
        #So it turns out that there is another problem with this system.
        #OWW does not allow you to put a Skip instruction in front of a Wait instruction, if there is not
        #already another Wait instruction before it. This means we can't skip into the loop from the top unless
        #we add a slight delay to the entire function (at least 0.25 seconds). Currently thinking of how to
        #circumvent this behavior but I don't think there is one.

        self._currentRule.loopCount += 1
        lastLoopBranch = self._curLoopBranch

        #set loop branch target
        expr = self._parseExpr(node.test)
        
        currentInd = self.currentLine() #This is where we jump to
        self.addAction("PLACEHOLDER") #where we skip the loop if the condition doesn't hold
        self.setLoopBranch(currentInd - 1)
        
        #parse instruction block
        for i in node.body:
            self._parseBody(i)

        #add loop instruction
        self.addAction("Loop()")
        #replace placeholder with condition test
        self._currentRule.actions[currentInd] = "Skip If(Not(%s), %i);" % (expr, (self.currentLine() - currentInd) - 1)
        #reset loop branch target
        self.setLoopBranch(lastLoopBranch)

    def _parseFor(self, node):

        """
        Parse a for loop node.
        """

        #For loops essentially use the same looping system that while loops use, except that
        #we don't check for a condition but iterate over an array until all elements have been exhausted.
        #To do this, we create a while loop with the condition of the index being less than the array length,
        #which we get with Count Of. The only issue here is that while the loop is running, other loops
        #using the same variable to store the current loop element would override each other, potentially
        #introducing race conditions.

        self._currentRule.loopCount += 1
        lastBranch = self._curLoopBranch #cache current loop branch to allow for nested loops

        #push loop iteration index
        self.pushLoopIteration()

        #set loop branch target
        currentInd = self.currentLine() #This is where we jump to
        self.setLoopBranch(currentInd)

        #get target and iterator from node
        iter = self._parseExpr(node.iter)
        target = node.target

        #use skip here to make sure we don't run the loop if the condition doesn't hold.
        skipInd = self.currentLine()
        self.addAction("PLACEHOLDER")
        #Set loop variable to store current array element
        self.addAction(self.setVariable(target.id, "Value In Array(%s, %s)" % (iter, self.getLoopIteration())))
        
        #parse instruction block
        for i in node.body:
            self._parseBody(i)

        #increment array pointer
        self.setLoopIteration("Add(%s, %i)" % (self.getLoopIteration(), 1))

        #add loop instruction
        self.addAction("Loop()")
        #replace skip placeholder
        self._currentRule.actions[skipInd] = "Skip If(Compare(Count Of(%s), <=, %s), %i);" % (iter, self.getLoopIteration(), (self.currentLine() - skipInd) - 1)
        #reset loop branch target and loop index
        self.setLoopBranch(lastBranch)
        self.pullLoopIteration()

    def _parseCall(self, node):

        """
        Parse a function call node.
        """

        #Function calls usually indicate that the programmer wants to
        #run some sort of function from the Workshop. In most cases,
        #we delegate these objects to the specific function implementation
        #to resolve into text and just return the result.

        funcName = node.func.id


        #prepare arguments
        args = node.args
        kwargs = {}
        for keyword in node.keywords:
            kwargs[keyword.arg] = self._parseExpr(keyword.value)

        #utility functions
        if funcName in self._utilityFunctions:
            return self._resolveUtilityFunction(funcName, args, kwargs)

        if not hasattr(owwlib, funcName):

            self.logger.debug("Parsing arguments as expression nodes...")
            parsed_args = list(map(self._parseExpr, args))
            if kwargs:
                self.logger.warn("Found non empty kwargs for unknown function, kwargs will be passed as positional args instead.")
                parsed_args.extend(kwargs.values())
            if self.HAS_JSON:
                #use workshop.json to find function definition
                if funcName in self.workshop_functions:
                    canon_name, arg_count = self.workshop_functions[funcName]
                    if len(parsed_args) != arg_count:
                        raise TypeError("Unexpected number of arguments for function '%s' (%s): Expected %i but was %i." % (funcName, canon_name, arg_count, len(parsed_args)))
                    func = "%s(%s)" % (canon_name, ", ".join(parsed_args))
                    self.logger.debug("Calling WSJSON function '%s'" % (func))
                    return func

            if not self.parseUnknownFunctions:
                raise NotImplementedError("The function '%s' is not implemented." % funcName)
            else:
                self.logger.info("Function '%s' not found, guessing signature from call node..." % funcName)

                func = "%s(%s)" % (funcName, ", ".join(parsed_args))
                self.logger.debug("Calling unknown function '%s'" % (func))
                return func

        #call function and return
        func = getattr(owwlib, funcName)
        return func(self, *args, **kwargs)

    def _parseExpr(self, node, parse_array=True):

        """
        Parse an expression yielding some value.
        """

        if isinstance(node, ast.Call):
            value = self._parseCall(node)
        elif isinstance(node, ast.Name):
            if node.id == "player":
                value = "Event Player"
            else:
                value = self.getVariable(node.id)
        elif isinstance(node, ast.Subscript):
            array = self._parseExpr(node.value)
            ind = self._parseExpr(node.slice.value)
            value = "Value In Array(%s, %s)" % (array, ind)
        elif isinstance(node, (ast.List, ast.Tuple)):
            value = self._parseArray(node, parse_array)
        elif isinstance(node, ast.BinOp):
            value = self._parseBinaryOp(node)
        elif isinstance(node, ast.Compare):
            value = self._parseCompare(node)
        elif isinstance(node, ast.Attribute):
            base = node.value
            attr = node.attr
            if base.id == "player":
                player = "Event Player"
            else:
                player = base.id
            value = self.getVariable(attr, player)
        else:
            value = str(ast.literal_eval(node))

        return value

    def _parseBinaryOp(self, node):

        left = self._parseExpr(node.left)
        right = self._parseExpr(node.right)
        op = node.op
        if isinstance(op, ast.Add):
            return "Add(%s, %s)" % (left, right)
        elif isinstance(op, ast.Sub):
            return "Subtract(%s, %s)" % (left, right)
        elif isinstance(op, ast.Mult):
            return "Multiply(%s, %s)" % (left, right)
        elif isinstance(op, ast.Div):
            return "Divide(%s, %s)" % (left, right)
        elif isinstance(op, ast.Mod):
            return "Modulo(%s, %s)" % (left, right)
        elif isinstance(op, ast.Pow):
            return "Raise To Power(%s, %s)" % (left, right)
        elif isinstance(op, ast.And):
            return "And(%s, %s)" % (left, right)
        elif isinstance(op, ast.Or):
            return "Or(%s, %s)" % (left, right)
        elif isinstance(op, ast.LShift):
            #<< is used for string formatting.
            #This requires the left side argument to be a string and
            #the right side to be a tuple of elements
            if not isinstance(node.left, ast.Str):
                raise TypeError("Can't use string format operator here; Expected target of type '%s' but was '%s'" % (str(ast.Str), str(node.left.__class__)))
            if not isinstance(node.right, ast.Tuple):
                raise TypeError("Expected string format list of type '%s' but was '%s'" % (str(ast.Tuple), str(node.right.__class__)))
            parameters = list(map(self._parseExpr, node.right.elts))
            return self.stringParser.parse(self._parseExpr(node.left).lower(), parameters)
        else:
            raise RuntimeError("Unrecognized binary operator '%s'" % str(op))

    def _assign(self, node):

        """
        Perform an assign opperation.
        This is used to set global variables.
        """

        targets = node.targets
        if len(targets) > 1:
            raise SyntaxError("List unpacking is not supported by OverScript.")
        target = targets[0]
        
        value = self._parseExpr(node.value)

        #Determine target
        if isinstance(target, ast.Name):
            return self.setVariable(target.id, value)
        elif isinstance(target, ast.Attribute):
            base = target.value
            attr = target.attr
            if base.id == "player":
                player = "Event Player"
            else:
                player = base.id
            return self.setVariable(attr, value, player)
        else:
            raise RuntimeError("Unexpected assignment target node type: '%s'" % str(target.__class__))
        
    #==================
    #ARRAY ASSEMBLY
    #==================
        
    def _array_clear(self, target, player=None):

        """
        Clears the specified variable.
        """

        if player:
            self.addAction("Set Player Variable(%s, %s, Empty Array)" % (player, target))
        else:
            self.addAction("Set Global Variable(%s, Empty Array)" % target)

    def _array_esc(self, source, target, player=None):
        
        """
        'escape' a value by embedding it into an array
        """

        self._array_clear(target, player)
        if player:
            self.addAction("Set Player Variable At Index(%s, %s, 0, Player Variable(%s, %s))" % (player, target, player, source))
        else:
            self.addAction("Set Global Variable At Index(%s, 0, Global Variable(%s))" % (target, source))

    def _array_esc_val(self, source, target, player=None):

        """
        same as _array_esc but using a value instead of a variable for the source
        """

        self._array_clear(target, player)
        if player:
            self.addAction("Set Player Variable At Index(%s, %s, 0, %s)" % (player, target, source))
        else:
            self.addAction("Set Global Variable At Index(%s, 0, %s)" % (target, source))

    def _array_ata(self, source, target, index, player=None):

        """
        append to array
        """

        if player:
            return "Append To Array(%s, Value In Array(Player Variable(%s, %s), %i))" % (target, player, source, index)
        else:
            return "Append To Array(%s, Value In Array(Global Variable(%s), %i))" % (target, source, index)

    def _array_set(self, target, value, player=None):

        """
        Set variable
        """

        if player:
            self.addAction("Set Player Variable(%s, %s, %s)" % (player, target, value))
        else:
            self.addAction("Set Global Variable(%s, %s)" % (target, value))

    def _array_push_stack(self, target, source, index, player=None):

        """
        Stack insertion operations.
        Inserts the value in variable source into the stack in variable
        target at the specified index.
        """

        if player:
            self.addAction("Set Player Variable At Index(%s, %s, %i, Player Variable(%s, %s))" % (player, target, index, player, source))
        else:
            self.addAction("Set Global Variable At Index(%s, %i, Global Variable(%s))" % (target, index, source))

    def _array_build(self, tos, array):

        """
        build an n dimensional array
        """

        player = None if self._currentRule.isGlobal() else "Event Player"

        #if this is a literal, return escape directly
        if not isinstance(array, list):
            self._array_set("E", array, player)
            self._array_esc("E", "F", player)
            self._array_push_stack("D", "F", tos.i, player)
            tos.i += 1
            return

        #otherwise, build all subarrays
        for i in range(len(array)):
            self._array_build(tos, array[i])

        #build next array
        value = "Empty Array"
        ind = tos.i - len(array)
        for i in range(len(array)):
            value = self._array_ata("D", value, ind+i, player)
        tos.i -= len(array)
        self._array_esc_val(value, "F", player)
        self._array_push_stack("D", "F", tos.i, player)
        tos.i += 1
        return

    def _create_1d_array(self, l):

        """
        Create a 1-dimensional array using a simpler algorithm
        """

        value = "Empty Array"
        
        for v in l:
            value = "Append To Array(%s, %s)" % (value, v)
        return value

    def _parseArray(self, node, parse_array=True):

        """
        Create an array from a literal.
        if parse_array is True, this will parse the array into a
        value string and return it. Otherwise, the Python list
        object will be returned instead.
        """

        elements = node.elts[:]
        l = list(map(self._parseExpr, elements, [False] * len(elements)))
        if not parse_array:
            return l

        #check dimensions
        for e in l:
            if isinstance(e, (tuple, list)):
                break
        else:
            #one dimensional array, use normal array assembly
            return self._create_1d_array(l)

        #n dimensional array
        #NOTE: I'm using TOS as a wrapper class to get mutable
        #integers. This could be done with just normal integers
        #by returning the stack offsets and then calculating the
        #new one based on that but I couldn't be bothered
        self._array_build(TOS(), l)

        if self._currentRule.isGlobal():
            return "Value In Array(Value In Array(Global Variable(D), 0), 0)"
        return "Value In Array(Value In Array(Player Variable(Event Player, D), 0), 0)"
