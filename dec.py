import struct, hashlib, time
import binascii
import os
from Crypto.Cipher import AES


def decrypt_file(key, in_filename, out_filename, chunksize=24 * 1024):
    with open(in_filename, 'rb') as infile:
        origsize = struct.unpack('<Q', infile.read(struct.calcsize('Q')))[0]
        iv = infile.read(16)
        decryptor = AES.new(key, AES.MODE_CBC, iv)
        with open(out_filename, 'wb') as outfile:
            while True:
                chunk = infile.read(chunksize)
                if len(chunk) == 0:
                    break
                outfile.write(decryptor.decrypt(chunk))
            outfile.truncate(origsize)


def encrypt_file(key, in_filename, out_filename=None, chunksize=65536):
    if not out_filename:
        out_filename = in_filename + '.enc'
    iv = 'initialvector123'
    encryptor = AES.new(key, AES.MODE_CBC, iv)
    filesize = os.path.getsize(in_filename)
    with open(in_filename, 'rb') as infile:
        with open(out_filename, 'wb') as outfile:
            outfile.write(struct.pack('<Q', filesize))
            outfile.write(iv)
            while True:
                chunk = infile.read(chunksize)
                if len(chunk) == 0:
                    break
                elif len(chunk) % 16 != 0:
                    chunk += ' ' * (16 - len(chunk) % 16)
                outfile.write(encryptor.encrypt(chunk))


def make_pass():
    timekey = int(time.time())
    return str(timekey)



def main():
    password = make_pass()
    key = hashlib.sha256(password).digest()
    print binascii.hexlify(bytearray(key))
    in_filename = './test.mov'
    encrypt_file(key, in_filename, out_filename='output')
    print 'Encrypte Done !'

    #delete original file

    #decrypt
    decrypt_file(key, in_filename='output', out_filename='original.mov')
    outfile = open('original.mov')
    magic = outfile.read(8)
    print 'Magic Number : ' + magic.encode('hex')
    if magic.encode('hex') == 'd0cf11e0a1b11ae1':
        print 'This document is a HWP file.'


main()
