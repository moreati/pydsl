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


"""Tests the Grammar definition instances"""

__author__ = "Nestor Arocha"
__copyright__ = "Copyright 2008-2013, Nestor Arocha"
__email__ = "nesaro@gmail.com"

import unittest

@unittest.skip
class TestGrammarDefinitionRegularExpression(unittest.TestCase):
    """Regular expression method tests"""
    def setUp(self):
        self.grammardef = None

    def testEnumerate(self):
        self.grammardef.enum()

    def testFirst(self):
        self.grammardef.first

    def testMin(self):
        self.grammardef.minsize

    def testMax(self):
        self.grammardef.maxsize

    def testAlphabet(self):
        self.assertListEqual(self.grammardef.alphabet(), AlphabetDefinition)


class TestGrammarDefinitionBNF(unittest.TestCase):
    def setUp(self):
        from pydsl.contrib.bnfgrammar import productionset0
        self.grammardef = productionset0

    def testEnumerate(self):
        self.assertListEqual([x for x in self.grammardef.enum()], ["SR"])

    def testFirst(self):
        self.assertListEqual(self.grammardef.first, ["S"])

    def testMin(self):
        self.assertEqual(self.grammardef.minsize,2)

    def testMax(self):
        self.assertEqual(self.grammardef.maxsize,2)

    def testFirstLookup(self):
        from pydsl.Grammar.Symbol import NonTerminalSymbol, TerminalSymbol
        from pydsl.Grammar.Definition import StringGrammarDefinition
        print(self.grammardef.first_lookup(NonTerminalSymbol("exp"))[0])
        self.assertListEqual(self.grammardef.first_lookup(NonTerminalSymbol("exp")),[TerminalSymbol(StringGrammarDefinition("S"))])

    def testNextLookup(self):
        from pydsl.Grammar.Symbol import NonTerminalSymbol, EndSymbol
        print(self.grammardef.next_lookup(NonTerminalSymbol("exp"))[0])
        self.assertListEqual(self.grammardef.next_lookup(NonTerminalSymbol("exp")),[EndSymbol()])

    def testAlphabet(self):
        self.assertListEqual(self.grammardef.alphabet().grammar_list, AlphabetDefinition)

@unittest.skip
class TestGrammarDefinitionMongoDb(unittest.TestCase):
    def setUp(self):
        self.grammardef = None

    def testEnumerate(self):
        self.grammardef.enum()

    def testFirst(self):
        self.grammardef.first

    def testMin(self):
        self.grammardef.minsize

    def testMax(self):
        self.grammardef.maxsize

    def testAlphabet(self):
        self.assertListEqual(self.grammardef.alphabet(), AlphabetDefinition)

class TestGrammarDefinitionPLY(unittest.TestCase):
    def setUp(self):
        import plye
        from pydsl.Grammar.Definition import PLYGrammar
        self.grammardef = PLYGrammar(plye)

    @unittest.skip
    def testEnumerate(self):
        self.grammardef.enum()

    @unittest.skip
    def testFirst(self):
        self.grammardef.first

    @unittest.skip
    def testMin(self):
        self.grammardef.minsize

    @unittest.skip
    def testMax(self):
        self.grammardef.maxsize

    def testAlphabet(self):
        self.assertListEqual(self.grammardef.alphabet(), AlphabetDefinition)

class TestGrammarDefinitionJson(unittest.TestCase):
    def setUp(self):
        from pydsl.Grammar.Definition import JsonSchema
        self.grammardef = JsonSchema({})

    def testEnumerate(self):
        self.grammardef.enum()

    def testFirst(self):
        self.grammardef.first

    def testMin(self):
        self.grammardef.minsize

    def testMax(self):
        self.grammardef.maxsize

    def testAlphabet(self):
        self.assertListEqual(self.grammardef.alphabet(), AlphabetDefinition)

