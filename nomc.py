#!/usr/bin/env python
import socket
import struct
import sys


class area_directory(object):
    def __init__(self, network_area_directory):
        self.area_dir = self._convert_net_ad_to_native(network_area_directory)
        self.has_aux = (self.get_aux_offset() is not None)
        self.has_cal = (self.get_cal_offset() is not None)
        self.has_nav = (self.get_nav_offset() is not None)
        self.bytes_per_element = list(struct.unpack('<l', get_mcword(self.area_dir, 11)))[0]

    @staticmethod
    def _convert_net_ad_to_native(net_ad):
        new_ad = struct.pack('!l', 0)
        for index in range(1, 20):
            new_ad += flip_word(get_word(net_ad, index))
        new_ad += get_word(net_ad, 20)
        for index in range(21, 24):
            new_ad += flip_word(get_word(net_ad, index))
        for index in range(24, 32):
            new_ad += get_word(net_ad, index)
        for index in range(32, 51):
            new_ad += flip_word(get_word(net_ad, index))
        for index in range(51, 53):
            new_ad += get_word(net_ad, index)
        for index in range(53, 56):
            new_ad += flip_word(get_word(net_ad, index))
        new_ad += get_word(net_ad, 56)
        for index in range(57, 64):
            new_ad += flip_word(get_word(net_ad, index))
        return new_ad

    def get(self):
        return self.area_dir

    # how to unpack integers list(struct.unpack('!l', s.recv(4)))[0]

    def get_aux_offset(self):
        aux_offset_word = get_mcword(self.area_dir, 60)
        aux_offset = list(struct.unpack('<l', aux_offset_word))[0]
        if aux_offset == 0:
            aux_offset = None
        return aux_offset

    def get_aux_length(self):
        aux_length_word = get_mcword(self.area_dir, 61)
        aux_length = list(struct.unpack('<l', aux_length_word))[0]
        if aux_length == 0:
            aux_length = None
        return aux_length

    def get_cal_offset(self):
        cal_offset_word = get_mcword(self.area_dir, 63)
        cal_offset = list(struct.unpack('<l', cal_offset_word))[0]
        if cal_offset == 0:
            cal_offset = None
        return cal_offset

    def get_cal_length(self):
        if self.has_cal:
            cal_length = self.get_data_offset() - self.get_cal_offset()
        else:
            cal_length = None
        return cal_length

    def get_data_offset(self):
        data_offset_word = get_mcword(self.area_dir, 34)
        return list(struct.unpack('<l', data_offset_word))[0]

    def get_nav_offset(self):
        nav_offset_word = get_mcword(self.area_dir, 35)
        nav_offset = list(struct.unpack('<l', nav_offset_word))[0]
        if nav_offset == 0:
            nav_offset = None
        return nav_offset

    def get_nav_length(self):
        if self.has_nav:
            if self.has_cal:
                nav_length = self.get_cal_offset() - self.get_nav_offset()
            else:
                nav_length = self.get_data_offset() - self.get_nav_offset()
        else:
            nav_length = None
        return nav_length


def flip_word(word):
    flipped_word = ''
    for c in word[::-1]:
        flipped_word += c
    return flipped_word


def get_half_word(bytestring, word_index):
    return bytestring[word_index * 2:(word_index + 1) * 2]


def get_word(bytestring, word_index):
    return bytestring[word_index * 4:(word_index + 1) * 4]


def get_mcword(bytestring, word_index):
    return get_word(bytestring, word_index - 1)


def construct_area_directory(original_ad):
#    new_ad = ''
    # first word = 0
    new_ad = struct.pack('!l', 0)
    for index in range(1, 20):
        #new_ad += flip_word(original_ad[index * 4:(index + 1) * 4])
        new_ad += flip_word(get_word(original_ad, index))
    # might need to flip index=20...
    new_ad += get_word(original_ad, 20)
    for index in range(21, 24):
        new_ad += flip_word(get_word(original_ad, index))
    for index in range(24, 32):
        new_ad += get_word(original_ad, index)
    for index in range(32, 51):
        new_ad += flip_word(get_word(original_ad, index))
    for index in range(51, 53):
        new_ad += get_word(original_ad, index)
    for index in range(53, 56):
        new_ad += flip_word(get_word(original_ad, index))
    new_ad += get_word(original_ad, 56)
    for index in range(57, 64):
        new_ad += flip_word(get_word(original_ad, index))
    return new_ad


def get_aux_offset(ad):
    return 0


def get_cal_offset(ad):
    return 0


def get_nav_offset(ad):
    return 0


def flip_nav(nav):
    new_nav = ''
    for index in [0, 1]:
        new_nav += get_word(nav, index)
    for index in range(2, 127):
        new_nav += flip_word(get_word(nav, index))
    for index in [127, 128]:
        new_nav += get_word(nav, index)
    for index in range(129, 255):
        new_nav += flip_word(get_word(nav, index))
    for index in [255, 256]:
        new_nav += get_word(nav, index)
    for index in range(257, 383):
        new_nav += flip_word(get_word(nav, index))
    for index in [383, 384]:
        new_nav += get_word(nav, index)
    for index in range(385, 511):
        new_nav += flip_word(get_word(nav, index))
    for index in [511, 512]:
        new_nav += get_word(nav, index)
    for index in range(513, 639):
        new_nav += flip_word(get_word(nav, index))
    for index in range(639, len(nav) / 4):
        new_nav += get_word(nav, index)
    return new_nav


def bad_flip_nav(nav):
    new_nav = ''
    for index in [0]:
        new_nav += get_word(nav, index)
    for index in range(1, 127):
        new_nav += flip_word(get_word(nav, index))
    for index in [127]:
        new_nav += get_word(nav, index)
    for index in range(128, 255):
        new_nav += flip_word(get_word(nav, index))
    for index in [255]:
        new_nav += get_word(nav, index)
    for index in range(256, 383):
        new_nav += flip_word(get_word(nav, index))
    for index in [383]:
        new_nav += get_word(nav, index)
    for index in range(384, 511):
        new_nav += flip_word(get_word(nav, index))
    for index in [511]:
        new_nav += get_word(nav, index)
    for index in range(512, 639):
        new_nav += flip_word(get_word(nav, index))
    for index in range(639, len(nav) / 4):
        new_nav += get_word(nav, index)
    return new_nav


def flip_data(data):
    new_data = ''
    for index in range(0, len(data) / 2):
        new_data += flip_word(get_half_word(data, index))
    return new_data


remote_host = 'eastl.ssec.wisc.edu'
remote_port = 112
request_type = "AGET"

initials = "KJH"
padded_initials = initials.ljust(4, ' ')
project_number = 6999

req_string = ("EASTL FD -1 EC 45 90 X 480 640 STYPE=VISR BAND= 1 TRACE=0 TIME="
              "X X I SPAC=1 UNIT=BRIT AUX=YES NAV= DAY= DOC=NO VERSION=1")
#req_string = ("EASTL FD -1 EC 45 90 X 480 640 BAND= 1 TRACE=0 TIME="
#              "X X I SPAC=0 UNIT=X AUX=YES NAV= DAY= DOC=NO VERSION=1") 
padded_req_string = req_string.ljust(120, ' ')

pack = struct.pack('!l', 1)
pack += socket.inet_aton(list(socket.gethostbyaddr(remote_host))[2][0])
pack += struct.pack('!l', 1)
pack += struct.pack('!4s', request_type)
pack += socket.inet_aton(list(socket.gethostbyaddr(remote_host))[2][0])
pack += struct.pack('!l', 112)
pack += struct.pack('!l', 0)
pack += struct.pack('!4s', padded_initials)
pack += struct.pack('!l', 6999)
pack += struct.pack('!3l', 0, 0, 0)
pack += struct.pack('!4s', request_type)
pack += struct.pack('!l', 0)
#pack += padded_req_string
pack += struct.pack('!120s', padded_req_string)

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((remote_host, remote_port))
s.send(pack)
recv_length = list(struct.unpack('!l', s.recv(4)))[0]

original_area_dir = s.recv(64 * 4)


ad = area_directory(original_area_dir)

print ad.get_aux_offset()
print ad.get_aux_length()
print ad.get_cal_offset()
print ad.get_cal_length()
print ad.get_nav_offset()
print ad.get_nav_length()


nav_dir = s.recv(ad.get_nav_length())
while len(nav_dir) < ad.get_nav_length():
    nav_dir += s.recv(ad.get_nav_length() - len(nav_dir))


new_nav_dir = flip_nav(nav_dir)
new_nav_dir = bad_flip_nav(nav_dir)

data = ad.get()
data += new_nav_dir

data_length = recv_length - len(ad.get()) - len(new_nav_dir)
data = ''
while len(data) < data_length:
    data += s.recv(data_length - len(data))
#while len(data) < recv_length:
#    data += s.recv(recv_length - len(data))

if ad.bytes_per_element == 1:
    new_data = data
elif ad.bytes_per_element == 2:
    new_data = flip_data(data)


area_file_data = ad.get() + new_nav_dir + new_data
try:
    data_path = sys.argv[1]
except IndexError:
    data_path = '/Users/robo/nomcidas/data/AREA6639'
data_file = open(data_path, 'wb')
data_file.write(area_file_data)
data_file.close()

#print data

#trailer = s.recv(1024)
