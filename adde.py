
#!/usr/bin/env python
# encoding: utf-8
"""adde.py


Created by rayg on 13 Jun 2014.
Copyright (c) 2014 University of Wisconsin SSEC. All rights reserved.
"""

import sys
import logging
import numpy as np


# every module should have a LOG object
# e.g. LOG.warning('my dog has fleas')
LOG = logging.getLogger(__name__)


def main():
    import argparse
    description = """A boilerplate script for basic python module appearance.
Doesn't actually do anything.
"""
    parser = argparse.ArgumentParser(description=description)
    parser.add_argument('-t', '--test', dest="self_test",
                        action="store_true", default=False, help="run self-tests")
    parser.add_argument('-v', '--verbose', dest='verbosity', action="count", default=0,
                        help='each occurrence increases verbosity 1 level through ERROR-WARNING-INFO-DEBUG')
    # http://docs.python.org/2.7/library/argparse.html#nargs
    #parser.add_argument('--stuff', nargs='5', dest='my_stuff',
    #                    help="one or more random things")
    parser.add_argument('pos_args', nargs='*',
                        help="positional arguments don't have the '-' prefix")
    args = parser.parse_args()


    if args.self_test:
        # FIXME - run any self-tests
        # import doctest
        # doctest.testmod()
        return 2


    levels = [logging.ERROR, logging.WARN, logging.INFO, logging.DEBUG]
    logging.basicConfig(level=levels[min(3, args.verbosity)])


    if not args.pos_args:
        parser.error("incorrect arguments, try -h or --help.")
        return 9

    # FIXME - main() logic code here
    return 0


if __name__=='__main__':
    sys.exit(main())


