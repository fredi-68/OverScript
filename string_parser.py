#String Building algorithm for the Overwatch Workshop
#
#Heavily inspired by Deltins ParseString algorithm
#https://github.com/ItsDeltin/Overwatch-Script-To-Workshop/blob/91f6d89cae2dda77d40139a589c22077def7654f/Deltinteger/Deltinteger/Elements/Values.cs#L729
#Parts copied are used with permission.

import logging
import re

class StringParser():

    SYMBOLS = "-></*-+=()!?"
    PARAM_REPLACE_RE = re.compile("(\\\\{[0-9]+?\\\\})")
    PARAM_MATCH_RE = re.compile("^\\{([0-9]+?)\\}")
    PARAM_ONLY_RE = re.compile("^\\{([0-9]+?)\\}$")

    logger = logging.getLogger("OS.StringParser")

    def __init__(self, db_file="res/strings.txt"):
        
        self.words = []
        if db_file:
            self.loadWords(db_file)

    def loadWords(self, path):

        """
        Load words from a file.
        """

        with open(path, "r") as f:
            for line in f.readlines():
                if line.startswith("//"):
                    continue
                self.words.append(line.strip("\n").lower())

        self.sort()

    def sort(self):

        """
        Sort the internal list of words after
        certain criteria.
        """

        #Right so I don't have fancy incremental sorting like C# does.
        #What I *can* do is split the list into multiple lists, then merge

        hasParam = []
        for i in self.words[:]:
            if "{0}" in i:
                hasParam.append(i)
                self.words.remove(i)

        hasParamAndSymbol = []
        for i in hasParam[:]:
            for char in self.SYMBOLS:
                if char in i:
                    hasParamAndSymbol.append(i)
                    hasParam.remove(i)
                    break

        hasSymbol = []
        for i in self.words[:]:
            for char in self.SYMBOLS:
                if char in i:
                    hasSymbol.append(i)
                    self.words.remove(i)
                    break

        #Sorting key function
        def f(x):
            return len(x)

        hasParam.sort(key=f)
        hasParamAndSymbol.sort(key=f)
        hasSymbol.sort(key=f)
        self.words.sort(key=f)

        self.words.extend(hasSymbol)
        self.words.extend(hasParam)
        self.words.extend(hasParamAndSymbol)

        self.words.reverse()

    def parse(self, s, params):

        """
        Parse a string into a value understood by OWW.

        s should be an instance of str.
        You can specify parameters inside your string using 
        the {n} syntax. Parameters will be substituted in order
        of occurance.
        If s contains words or phrases not recognized by the parser,
        ValueError is raised.
        If params contains more items than s has parameters, the remaining
        items are silently dropped.
        If params contains less items than s has parameters, TypeError is raised.

        The returned value will be a string consisting of one or multiple calls
        to the String() OWW function.
        """

        final_string = ""

        #special case for when the string passed to the parse() method
        #is literally just "{n}"
        m = self.PARAM_ONLY_RE.fullmatch(s)
        if m is not None:
            return params[int(m.group(1))]

        for template in self.words:
            temp_re = "^%s$" % re.sub(self.PARAM_REPLACE_RE, "(.+)", re.escape(template))
            self.logger.debug("Testing string template '%s' (-> RE template '%s')..." % (template, temp_re))

            match = re.match(temp_re, s)
            if match is not None:
                try:
                    self.logger.debug("Match found: %s" % template)
                
                    string_args = ['"%s"' % template]
                    #check parameters
                    for group in match.groups():
                        #is parameter formatted?
                        self.logger.debug("Parsing group '%s'..." % group)
                        paramStr = re.fullmatch(self.PARAM_MATCH_RE, group)
                        if paramStr:
                            #substitute parameter
                            try:
                                string_args.append(params[int(paramStr.group(1))])
                            except IndexError:
                                raise TypeError("Not enough arguments to format string.")
                        else:
                            #keep parsing
                            string_args.append(self.parse(group, params))
                
                    string_args.extend(["null"] * (4 - len(string_args)))
                    final_string += "String(%s)" % ", ".join(string_args)

                    break
                except ValueError as e:
                    self.logger.debug("%s. Trying next template..." % str(e))
                    continue

        else:
            raise ValueError("Can't match string '%s': No matching template found." % s)

        return final_string
