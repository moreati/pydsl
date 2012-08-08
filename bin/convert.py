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

"""
Converts a filetype to another filetype
"""

__author__ = "Néstor Arocha Rodríguez"
__copyright__ = "Copyright 2008-2012, Néstor Arocha Rodríguez"
__email__ = "nesaro@gmail.com"


import logging
LOG = logging.getLogger(__name__)
from pydsl.Exceptions import BadFileFormat

if __name__ == "__main__":
    import argparse
    from pydsl.Config import VERSION
    TUSAGE = "usage: %(prog)s [options] [filename]"
    PARSER = argparse.ArgumentParser(usage = TUSAGE)
    PARSER.add_argument("-d", "--debuglevel", action="store", type=int, dest="debuglevel", help="Sets debug level")
    PARSER.add_argument("inputfile", action="store", help="input filename dict")
    PARSER.add_argument("outputfile", action="store", help="output filename dict")
    PARSER.add_argument("-i", "--inputformat", nargs='?', action="store", dest="inputformat", help="input format")
    PARSER.add_argument("-f", "--destformat", nargs='?', action="store", dest="destformat", help="destination format")
    PARSER.add_argument('--version', action='version', version = VERSION)
    ARGS = PARSER.parse_args()
    import sys
    DEBUGLEVEL = logging.WARNING
    if ARGS.debuglevel:
        DEBUGLEVEL = ARGS.debuglevel
    logging.basicConfig(level = DEBUGLEVEL)
    #from pydsl.Interaction.Interpreter import Interpreter
    #MANAGER = Interpreter(ARGS)
    destformat = ARGS.destformat
    if not destformat:
        from pydsl.Memory.Storage.Directory.DirStorage import getFileTuple
        _,_,_,destformat = getFileTuple(ARGS.outputfile)
        destformat = destformat[1:] #Quitamos el punto

    LOG.warning("Destination format:" + destformat)
    if (ARGS.inputfile and ARGS.outputfile):
        import os
        if not os.path.exists(ARGS.inputfile):
            print("input file doesn't exists")
            sys.exit(-1)
        inputfile = "file://" + ARGS.inputfile
        inputformat = ARGS.inputformat 
        if not inputformat:
            from pydsl.Memory.Storage.Dict import FileTypeDictStorage
            ftdl = FileTypeDictStorage()
            from pydsl.Guess import guess
            inputformat = guess(inputfile, [ftdl])
            if len(inputformat) == 0:
                print("Input format not found")
                sys.exit(-1)
            elif len(inputformat) > 1:
                print("Several input formats found, please use -i argument")
                sys.exit(-1)
            inputformat = inputformat.pop()

        LOG.warning("Inputformat:" + inputformat)
        from pydsl.Memory.Storage.Directory.Function import TransformerDirStorage 
        from pydsl.Search.Searcher import MemorySearcher
        from pydsl.Search.Indexer import Indexer
        searcher = MemorySearcher([Indexer(TransformerDirStorage())])
        print(searcher.search("output="+destformat+"&&input="+inputformat))
        searchresult = searcher.search("output="+destformat+"&&input="+inputformat)
        if not searchresult:
            print("No conversion available from "+ inputformat + " to " + destformat)
            sys.exit(-1)
        firstresult = searchresult.pop()
        from pydsl.Memory.Storage.Loader import load_transformer
        finstance = load_transformer(firstresult["identifier"])
        result = finstance({"inputfile":inputfile,"outputfile":ARGS.outputfile})
        sys.exit(0)
        #sys.exit(int(str(result["output"])))
    else:
        print(TUSAGE)
        sys.exit(0)
    sys.exit(0)
