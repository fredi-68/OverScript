# OverScript - Overwatch Workshop Script Compiler for Python 3

This is a compiler, which turns Python 3 code into workshop rules
which can be pasted into the Overwatch Workshop (sometimes also called 'transpiler').

Currently supported features are:

	- Infinite variables
	- Named variables with implicit declaration
	- Basic control flow statements which work like you would expect (if/else, for, while)
	- Support for list literals
	- Support for many Python operators (assign, subscript, arithmetic, etc...)
	- automatic string building

Planned features include:

	- utility functions
	- support for elif clauses

Known issues:

	- Some operations currently only work on global variables
	- If your rule contains a loop, it will have a startup delay of 0.001 seconds.


# How to create scripts

OverScript files are normal Python modules with some restrictions.
To create a rule, simply create a new function.
The name of the function will determine the name of the rule. Now you can
write any code you want inside this rule and it will be converted to workshop
code during compilation. To access workshop values or actions, you can call them
as functions. In general most functions have the same name as their workshop
equivalent, sometimes abreviated. However, in case the function has more than
one word, I am using lowerCamelCase instead of spaces. Actions add the respective
action to the action list, values return the result of the function.

There are some special keywords and operators available as shorthands for commonly used values.

	-The values Event Player, Victim and Attacker can be referred to using the keywords
	player, victim and attacker respectively. Player variables may be accessed
	through dotted attribute access (e.g. player.objective_state)

	-The values Add, Subtract, Multiply, etc. are available through the standard
	Python operators +, -, *, etc. Augmentation assignments (like +=) are supported.

	-Value In Array is available through subscript (e.g. myList[0])

To edit the event or condition settings for a rule, you can use function decorators:

	- `@event` lets you specify the event type of this rule. You are only allowed
	to use this decorator once per rule. The event name is abbreviated, look up the
	mapping in `compiler.EVENTS`.
	`@event` expects all arguments to be strings. You are resposible for entering
	correct information here.

	- `@trigger` lets you specify the conditions that trigger a rule. You can have as
	many triggers as you want.
	All arguments inside the trigger decorator are expected to resolve to boolean
	expressions, that is, expressions that yield a boolean value (True or False).
	Be aware that the result of the condition will be checked against True, so if
	your input does NOT yield a boolean, this may lead to unexpected results.


# How to turn your script into a workshop rule

You can use the OverScript.py utility to compile your script. Simply run it
with a path to your script as the first argument and an optional second argument
specifying the destination path of the compiled file. You can then paste the
contents of this file into the overwatch workshop.