
#!/usr/bin/env python
# encoding: utf-8
"""adde.py


Created by rayg on 13 Jun 2014.
Copyright (c) 2014 University of Wisconsin SSEC. All rights reserved.
"""

import os, sys
import logging
import ctypes as C
import socket
import struct
import unittest
from collections import namedtuple

CARD_SIZE = 80

# every module should have a LOG object
# e.g. LOG.warning('my dog has fleas')
LOG = logging.getLogger(__name__)

inaddr_t = C.c_uint8 * 4


# http://www.ssec.wisc.edu/mcidas/doc/prog_man/current/formats-1.html#13797
AREA_HEADER_FIELDS = (
    # words 1-8
    ('relative_position_within_dataset', C.c_int32),
    ('image_type', C.c_int32),
    ('sensor_source_number', C.c_int32),
    ('yyyddd', C.c_int32),
    ('hhmmss', C.c_int32),
    ('line_ul', C.c_int32),
    ('element_ul', C.c_int32),
    ('_reserved1', C.c_int32),

    # 9-16
    ('lines', C.c_int32),
    ('elements', C.c_int32),
    ('bytes_per_element', C.c_int32),
    ('line_res', C.c_int32),
    ('element_res', C.c_int32),
    ('spectral_band_count', C.c_int32),
    ('line_prefix_length', C.c_int32),
    ('project', C.c_int32),

    # 17-24
    ('file_yyyddd', C.c_int32),
    ('file_hhmmss', C.c_int32),
    ('spectral_band_map_1_32', C.c_int32),
    ('spectral_band_map_33_64', C.c_int32),
    ('sensor_specific', C.c_int32 * 4),

    # 25-32
    ('memo', C.c_char * 32),

    # 33-36
    ('_reserved2', C.c_int32),
    ('data_block_offset', C.c_int32),
    ('nav_block_offset', C.c_int32),
    ('validity_code', C.c_int32),

    # 37-44
    ('program_data_load', C.c_int32 * 8),

    # 45-48
    ('band8_source_goesaa', C.c_int32),
    ('image_yyyddd', C.c_int32),
    ('image_hhmmss_or_ms', C.c_int32),
    ('start_scan', C.c_int32),

    # 49-56
    ('prefix_doc_length', C.c_int32),
    ('prefix_cal_length', C.c_int32),
    ('prefix_band_length', C.c_int32),
    ('source_type', C.c_char * 4),
    ('cal_type', C.c_char * 4),
    ('_reserved3', C.c_int32 * 3),

    # 57-64
    ('original_source_type', C.c_int32),
    ('units', C.c_int32),
    ('scaling', C.c_int32),
    ('aux_block_offset', C.c_int32),
    ('aux_block_length', C.c_int32),
    ('_reserved4', C.c_int32),
    ('cal_block_offset', C.c_int32),
    ('comment_count', C.c_int32)
)

TABLE_BPE_TO_TYPE = { 1: C.c_int8,
                      2: C.c_int16,
                      4: C.c_int32
}

def _recv_length_word(sock):
    total_bytes, = struct.unpack('>l', sock._sock.recv(4))
    return total_bytes


def _recv_all(sock, toread, buffer=None):
    # ref http://stackoverflow.com/questions/15962119/using-bytearray-with-socket-recv-into
    LOG.debug('about to recv %d bytes' % toread)
    buf = buffer if (buffer is not None) else bytearray(toread)
    view = memoryview(buf)
    while toread:
        n_got = sock.recv_into(view, toread)
        LOG.debug('got %d bytes' % n_got)
        view = view[n_got:]
        toread -= n_got
    return buf



class area_header_t(C.Structure):
    """
    """
    _pack_ = 1
    _fields_ = AREA_HEADER_FIELDS


class adde_header_t(C.BigEndianStructure):
    """an area header received over an ADDE socket
    """
    _pack_ = 1
    _fields_ = AREA_HEADER_FIELDS



#
# aget image requests
#

def _fields_repr(ctype):
    from pprint import pformat
    return pformat(dict( (name, getattr(ctype, name)) for (name,_) in ctype._fields_ ))


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

    __repr__ = _fields_repr

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

    __repr__ = _fields_repr


def form_aget(text, host, port, user, project, password, server_inaddr=None, client_inaddr=None):
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
    server = server_inaddr if (server_inaddr is not None) else inaddr_t.from_buffer_copy(socket.inet_aton(list(socket.gethostbyaddr(host))[2][0]))
    client = client_inaddr if (client_inaddr is not None) else inaddr_t.from_buffer_copy(socket.inet_aton(list(socket.gethostbyaddr(socket.gethostname()))[2][0]))

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


block_loc_t = namedtuple('block_loc_t', ('offset', 'length'))
NOWHERE = block_loc_t(0, 0)

def _find_blocks(hdr):
    "return start_offset,length pairs for aux, cal, nav based on 64-word header content"
    has_nav = hdr.nav_block_offset != 0
    has_aux = hdr.aux_block_offset != 0
    has_cal = hdr.cal_block_offset != 0
    nav_length = (hdr.cal_block_offset or hdr.data_block_offset) - hdr.nav_block_offset
    aux_length = hdr.aux_block_length
    cal_length = hdr.data_block_offset - hdr.cal_block_offset
    aux = block_loc_t(hdr.aux_block_offset, aux_length) if has_aux else NOWHERE
    nav = block_loc_t(hdr.nav_block_offset, nav_length) if has_nav else NOWHERE
    cal = block_loc_t(hdr.cal_block_offset, cal_length) if has_cal else NOWHERE
    return aux, cal, nav



def recv_aget(sock):
    """
    create a structure holding the AGET outcome
    this type should then be mapped over received ADDE data
    http://www.ssec.wisc.edu/mcidas/doc/prog_man/current/servers-5.html#25171
    """
    total_bytes = _recv_length_word(sock)
    blob = _recv_all(sock, total_bytes)
    view = memoryview(blob)

    # start building a data structure schema for the block of data we just received
    fields = list(AREA_HEADER_FIELDS)

    # copy a chunk of data that we know is the header
    header = adde_header_t.from_buffer_copy(view[:256])

    #comments_field = ('comments', (C.c_char * 80) * header.comment_count)
    aux, cal, nav = _find_blocks(header)

    if nav.length > 0:
        # FIXME for now just put in a block of characters - eventually this is a separate structure
        fields.append(('_nav_raw', C.c_char * nav.length))

    if cal.length > 0:
        # FIXME for now a placeholder for a set of cal fields
        fields.append(('_cal_raw', C.c_char * cal.length))

    # FIXME add aux handling - for now just error out if somebody slips us some aux or cal
    assert(aux.length == 0)

    data_block_length = total_bytes - header.data_block_offset - (header.comment_count * CARD_SIZE)
    element_typ = TABLE_BPE_TO_TYPE[header.bytes_per_element]
    assert((data_block_length % header.bytes_per_element)==0)
    total_elements = data_block_length / header.bytes_per_element
    assert(total_elements == header.lines * header.elements)
    fields.append( ('image', (element_typ * header.elements) * header.lines) )

    comment_field = ('comments', (C.c_char * CARD_SIZE) * header.comment_count)
    fields.append(comment_field)

    class _adde_aget_result(C.BigEndianStructure):
        _pack_ = 1
        _fields_ = fields

    return _adde_aget_result.from_buffer(view)








#
# image directory requests
#

def structure_adde_image_dir_entry(total_bytes):
    """
    create a directory entry type for ADDE, given the number of bytes received.
    this type should then be mapped over received ADDE data
    http://www.ssec.wisc.edu/mcidas/doc/prog_man/current/servers-5.html#25171
    """
    comment_count = int((total_bytes - 260) / CARD_SIZE)
    if (total_bytes - 260) % CARD_SIZE != 0:
        raise ValueError('total_bytes %d does not match header + integral comments' % total_bytes)
    comment_fields = (('comments', (C.c_char * CARD_SIZE) * comment_count), )
    fields = (('area_number', C.c_int32), ) + area_header_t._fields_ + comment_fields
    class adde_image_dir_entry(C.BigEndianStructure):
        _pack_ = 1
        _fields_ = fields
    return adde_image_dir_entry

def recv_adde_image_dir(sock):
    """
    receive an ADDE image directory from a socket
    """
    # receive total_bytes and convert to native word order
    # FIXME: how do we know when the directory is done sending?
    total_bytes, = _recv_length_word(sock)
    cls = structure_adde_image_dir_entry(total_bytes)
    bfr = bytes(sock.recv(total_bytes))
    return cls.from_buffer(bfr)
    
    



class Session(object):
    """
    ADDE Session convenience abstraction, holding credentials and cached state
    """
    host = None
    user = None
    port = None
    project = None
    password = None
    # _sock = None
    _server_inaddr = None
    _client_inaddr = None

    def _connect(self, timeout=None):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((self.host, self.port))
        s.settimeout(timeout)
        return s


    def __init__(self, host, port, user, project, password):
        self.host = host
        self.port = port
        self.user = user
        self.project = project
        self.password = password
        self._server_inaddr = inaddr_t.from_buffer_copy(socket.inet_aton(list(socket.gethostbyaddr(host))[2][0]))
        self._client_inaddr = inaddr_t.from_buffer_copy(socket.inet_aton(list(socket.gethostbyaddr(socket.gethostname()))[2][0]))


    def aget(self, request_string, timeout=10):

        bfr = form_aget(request_string, self.host, self.port, self.user, self.project, self.password,
                        server_inaddr=self._server_inaddr, client_inaddr=self._client_inaddr)
        LOG.debug(repr(bfr))
        s = self._connect(timeout)
        s.send(bfr)
        zult = recv_aget(s)
        s.close()
        return zult

TEST_REQ_STRING = ("EASTL FD -1 EC 45 90 X 480 640 STYPE=VISR BAND= 1 TRACE=0 TIME="
                       "X X I SPAC=1 UNIT=BRIT AUX=YES NAV= DAY= DOC=NO VERSION=1")


def _test_request():
    """
    return a request after writing binary data to /tmp/request.bin
    od -t x1 /tmp/request.bin
    :return:
    """
    req = form_aget(TEST_REQ_STRING,
                     'eastl.ssec.wisc.edu',
                     112,
                     'RKG',
                     6999,
                     '')
    with open('/tmp/request.bin', 'wb') as fp:
        fp.write(req)
    return req


def _test_smoke():
    logging.basicConfig(level=logging.DEBUG)
    ses = Session('eastl.ssec.wisc.edu',
                       112,
                       'RKG',
                       6999,
                       '')
    return ses.aget(TEST_REQ_STRING)


class test_adde(unittest.TestCase):
    ses = None
    def setUp(self):
        # FUTURE: consolidate test patterns where we can build them into here, then knock them down later
        self.ses = Session('eastl.ssec.wisc.edu',
                           112,
                           'RKG',
                           6999,
                           '')

    def test_aget(self):
        zult = self.ses.aget(TEST_REQ_STRING)
        return zult






def main():
    import argparse
    description = """A boilerplate script for basic python module appearance.
Doesn't actually do anything.
"""
    parser = argparse.ArgumentParser(description=description)
    # parser.add_argument('-t', '--test', dest="self_test",
    #                     action="store_true", default=False, help="run self-tests")
    parser.add_argument('-v', '--verbose', dest='verbosity', action="count", default=0,
                        help='each occurrence increases verbosity 1 level through ERROR-WARNING-INFO-DEBUG')
    # http://docs.python.org/2.7/library/argparse.html#nargs
    #parser.add_argument('--stuff', nargs='5', dest='my_stuff',
    #                    help="one or more random things")
    parser.add_argument('pos_args', nargs='*',
                        help="positional arguments don't have the '-' prefix")
    args = parser.parse_args()


    if not args.pos_args:
        unittest.main()
        return 0

    levels = [logging.ERROR, logging.WARN, logging.INFO, logging.DEBUG]
    if 'DEBUG' in os.environ:
        verb = 3
    else:
        verb = args.verbosity
    logging.basicConfig(level=levels[min(3, verb)])


    # if not args.pos_args:
    #     print("running _test_request, writing request to /tmp/request.bin (next try 'od -t x1 /tmp/request.bin')")
    #     req = _test_request()
    #     with open('/tmp/request.bin', 'wb') as fp:
    #         fp.write(req)
    #     parser.error("incorrect arguments, try -h or --help.")
    #     return 9

    # FIXME - main() logic code here
    return 0


if __name__=='__main__':
    sys.exit(main())


