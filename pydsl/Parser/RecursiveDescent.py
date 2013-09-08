#!/usr/bin/python
# -*- coding: utf-8 -*-
#This file is part of pydsl.
#
#pydsl is free software: you can redistribute it and/or modify
#it under the terms of the GNU General Public License as published by
#the Free Software Foundation, either version 3 of the License, or
#(at your option) any later version.
#
#pydsl is distributed in the hope that it will be useful,
#but WITHOUT ANY WARRANTY; without even the implied warranty of
#MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#GNU General Public License for more details.
#
#You should have received a copy of the GNU General Public License
#along with pydsl.  If not, see <http://www.gnu.org/licenses/>.

"""Recursive descent parser"""

__author__ = "Nestor Arocha"
__copyright__ = "Copyright 2008-2013, Nestor Arocha"
__email__ = "nesaro@gmail.com"

import logging
LOG = logging.getLogger(__name__)
from .Parser import TopDownParser, terminal_symbol_reducer
from pydsl.Grammar.Tree import ParseTree, Tree

#Errors are stored elsewhere. If another alternative covers this error, we discard this alternative.
#If not, we choose the alternative which covers more amount of input

class RecursiveDescentResultTree(Tree):
    """Stores alternatives generated by the parser. Internal use only"""
    def __init__(self, content):
        Tree.__init__(self)
        if content is not None and not isinstance(content, ParseTree):
            raise TypeError
        self.content = content

    def get_lists(self):
        """Converts the tree into a list of lists"""
        result = []
        mylist = [self.content]
        if not self.childlist and self.content:
            return [mylist]
        for child in self.childlist:
            x = child.get_lists()
            for li in x:
                assert(isinstance(li, list))
                if self.content is None:
                    result.append(li)
                elif self.content.rightpos == li[0].leftpos or self.content.rightpos == self.content.leftpos:
                    result.append(mylist + li)
        return result

    def append(self, content, startpos):
        if not isinstance(content, ParseTree):
            raise TypeError
        if self.content is None and startpos == 0:
            self.childlist.append(RecursiveDescentResultTree(content))
            return True
        elif not self.childlist and self.content.rightpos == startpos:
            self.childlist.append(RecursiveDescentResultTree(content))
            return True
        elif content.rightpos == content.leftpos and self.content is not None and self.content.rightpos == startpos:
            self.childlist.append(RecursiveDescentResultTree(content))
            return True
        elif self.content is not None and self.childlist and startpos == self.content.rightpos and content.rightpos != content.leftpos:
            self.childlist.append(RecursiveDescentResultTree(content))
            return True
        elif self.childlist:
            success = False
            for x in self.childlist:
                if x.append(content, startpos):
                    success = True
            return success
        elif content == self.content:
            LOG.debug("duplicated content")
            return False
        else:
            #TODO:Raise an exception? 
            return False

    def right_limit_list(self):
        """Returns a list with every right limit (inorder)"""
        result = []
        if self.content and self.content.rightpos:
            result.append(self.content.rightpos)
        for x in self.childlist:
            result += x.right_limit_list()
        if not result:
            result = [0]
        return list(set(result))


class RecursiveDescentParser(TopDownParser):
    """Recursive descent parser class"""
    def get_trees(self, data, showerrors = False): # -> list:
        """ returns a list of trees with valid guesses """
        if not isinstance(data, str):
            data = str(data).strip()
        result = self.__recursive_parser(self._productionset.initialsymbol, data, self._productionset.main_production, showerrors)
        finalresult = []
        for eresult in result:
            if eresult.leftpos == 0 and eresult.rightpos == len(data) and eresult not in finalresult:
                finalresult.append(eresult)        
        return finalresult

    def __recursive_parser(self, onlysymbol, data, production, showerrors = False):
        """ Aux function. helps check_word"""
        LOG.debug("__recursive_parser: Begin ")
        if not data:
            return []
        from pydsl.Grammar.Symbol import TerminalSymbol, NullSymbol, NonTerminalSymbol
        if isinstance(onlysymbol, TerminalSymbol):
            #Locate every occurrence of word and return a set of results. Follow boundariesrules
            LOG.debug("Iteration: terminalsymbol")
            result = terminal_symbol_reducer(onlysymbol, data, production, fixed_start=True)
            if showerrors and not result:
                return [ParseTree(0,len(data), [onlysymbol] , data, onlysymbol, valid = False)]
            return result
        elif isinstance(onlysymbol, NullSymbol):
            return [ParseTree(0, 0, [onlysymbol], "", production)]
        elif isinstance(onlysymbol, NonTerminalSymbol):
            validstack = []
            invalidstack = []
            for alternative in self._productionset.getProductionsBySide([onlysymbol]): #Alternative
                alternativetree = RecursiveDescentResultTree(None)
                alternativeinvalidstack = []
                for symbol in alternative.rightside: # Symbol
                    symbol_success = False
                    for totalpos in alternativetree.right_limit_list(): # Right limit
                        if totalpos >= len(data):
                            continue
                        thisresult =  self.__recursive_parser(symbol, data[totalpos:], alternative, showerrors)
                        if thisresult and all(thisresult):
                            symbol_success = True
                            for x in thisresult:
                                x.shift(totalpos)
                                success = alternativetree.append(x, totalpos)
                                if not success:
                                    #TODO: Add as an error to the tree or to another place
                                    LOG.debug("Discarded symbol :" + str(symbol) + " position:" + str(totalpos))
                                else:
                                    LOG.debug("Added symbol :" + str(symbol) + " position:" + str(totalpos))
                        else:
                            alternativeinvalidstack += [x for x in thisresult if not x]

                    if not symbol_success:
                        LOG.debug("Symbol doesn't work" + str(symbol))
                        break #Try next alternative
                else: # Alternative success (no break happened)
                    invalidstack += alternativeinvalidstack

                for x in alternativetree.get_lists():
                    validstack.append(x)

            result = []

            LOG.debug("iteration result collection finished:" + str(validstack))
            for alternative in self._productionset.getProductionsBySide([onlysymbol]):
                nullcount = alternative.rightside.count(NullSymbol())
                for results in validstack:
                    nnullresults = 0
                    leftpos = results[0].leftpos
                    rightpos = results[-1].rightpos
                    for y in [x.symbollist for x in results]:
                        nnullresults += y.count(NullSymbol())
                    if len(results) - nnullresults != len(alternative.rightside) - nullcount:
                        LOG.debug("Discarded: incorrect number of non null symbols")
                        continue
                    if rightpos > len(data):
                        LOG.debug("Discarded: length mismatch")
                        continue
                    for x in range(min(len(alternative.rightside), len(results))):
                        if results[x].content != alternative.rightside[x]:
                            LOG.debug("Discarded: rule doesn't match partial result")
                            continue
                    childlist = [x for x in results]
                    allvalid = all([x.valid for x in childlist])
                    if allvalid:
                        newresult = ParseTree(0, rightpos - leftpos, [onlysymbol],
                                data[leftpos:rightpos], production, childlist)
                        newresult.valid = True
                        result.append(newresult)
            if showerrors and not result:
                erroresult = ParseTree(0,len(data), [onlysymbol] , data, production, valid = False)
                for invalid in invalidstack:
                    current_symbol = invalid.production if isinstance(invalid.production, (TerminalSymbol, NullSymbol)) else invalid.production.leftside[0]
                    if current_symbol in production.rightside:
                        erroresult.append_child(invalid)
                return [erroresult]
            return result
        raise Exception("Unknown symbol:" + str(onlysymbol))
