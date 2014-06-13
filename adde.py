
#!/usr/bin/env python
# encoding: utf-8
"""adde.py


Created by rayg on 13 Jun 2014.
Copyright (c) 2014 University of Wisconsin SSEC. All rights reserved.
"""

import sys
import logging
import ctypes as C
import socket
import unittest

# every module should have a LOG object
# e.g. LOG.warning('my dog has fleas')
LOG = logging.getLogger(__name__)


inaddr_t = C.c_uint8 * 4

class adde_preamble_t(C.BigEndianStructure):
    """
    Preamble data structure at the start of an ADDE request.
    """
    _pack_ = 1
    _fields_ = (
        ('version', C.c_uint32),
        ('server_address', inaddr_t),
        ('port', C.c_uint32),
        ('service', C.c_char * 4)
    )

class adde_aget_t(C.BigEndianStructure):
    """
    data structure representing an ADDE AGET request.
    """
    _pack_ = 1
    _fields_ = (
        ('preamble', adde_preamble_t),
        ('server_address', inaddr_t),
        ('server_port', C.c_uint32),
        ('client_address', inaddr_t),
        ('user', C.c_char * 4),
        ('project', C.c_int32),
        ('password', C.c_char * 12),
        ('service', C.c_char * 4),
        ('input_length', C.c_int32),
        ('text', C.c_char*120)
    )



def form_aget(text, host, port, user, project, password):
    """
    Return a data structure that can be sent to network.

    :param host: server address, string
    :param port: port number of server
    :param user: username to embed in request, up to 4 characters
    :param project: project number, integer
    :param password:
    :param text:
    :return: adde_aget_t structure

    """

    server = inaddr_t.from_buffer_copy(socket.inet_aton(list(socket.gethostbyaddr(host))[2][0]))
    client = inaddr_t.from_buffer_copy(socket.inet_aton(list(socket.gethostbyaddr(socket.gethostname()))[2][0]))

    req = adde_aget_t()
    req.preamble.version = 1
    req.preamble.server_address = server
    req.preamble.port = port
    req.preamble.service = 'AGET'

    req.server_address = server
    req.server_port = port
    req.client_address[:] = client
    req.user = user.ljust(4,' ')
    req.project = project
    req.password = password.ljust(12,' ')
    req.service = 'AGET'
    req.input_length = len(text)
    req.text = text.ljust(120, ' ')

    return req




def _test_request():
    """
    return a request after writing binary data to /tmp/request.bin
    od -t x1 /tmp/request.bin
    :return:
    """

    req_string = ("EASTL FD -1 EC 45 90 X 480 640 STYPE=VISR BAND= 1 TRACE=0 TIME="
                  "X X I SPAC=1 UNIT=BRIT AUX=YES NAV= DAY= DOC=NO VERSION=1")

    return form_aget(req_string,
                     'eastl.ssec.wisc.edu',
                     112,
                     'RKG',
                     6999,
                     '')



class test_adde(unittest.TestCase):
    def setUp(self):
        # FUTURE: consolidate test patterns where we can build them into here, then knock them down later
        pass

    def test_aget(self):
        pass





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
        print("running _test_request, writing request to /tmp/request.bin (next try 'od -t x1 /tmp/request.bin')")
        req = _test_request()
        with open('/tmp/request.bin', 'wb') as fp:
            fp.write(req)
        parser.error("incorrect arguments, try -h or --help.")
        return 9

    # FIXME - main() logic code here
    return 0


if __name__=='__main__':
    sys.exit(main())


