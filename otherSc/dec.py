import struct, hashlib, time
import binascii
import os
from Crypto import Random
from Crypto.PublicKey import RSA
from Crypto.Cipher import AES
import sqlite3


conn = sqlite3.connect('test.db', check_same_thread=False)
cur = conn.cursor()
private_key = '/Users/leebongho/monitoring/keyDir/mykey.txt'
public_key = '/Users/leebongho/monitoring/keyDir/mypukye.txt'

"""RSA KEY def"""

def readprivatePEM() :
    h = open(private_key, 'r')
    key = RSA.importKey(h.read())   #read private_key from mykey.txt
    h.close()
    return key

def readpublicPEM() :
    f = open(public_key, 'r')
    key = RSA.importKey(f.read())
    h.close
    return key

def rsa_enc(msg) :  # encryption msg using public_key
    private_key = readprivatePEM()
    public_key = private_key.publickey()
    encdata = public_key.encrypt(msg, 32)
    return encdata

def rsa_dec(msg) :  # decryption msg using private_key
    private_key = readprivatePEM()
    decdata = private_key.decrypt(msg)
    return decdata

""" RAS KEY def END """



"""AES KEY def """
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

"""AES KEY def END """


def main():
    cur.execute('SELECT Enc_AES FROM metaData WHERE _id=227')
    row = cur.fetchone()
    print(row)
    key=eval(row[-1])
    print(key)
    dec_key=rsa_dec(key)
    decrypt_file(dec_key, in_filename='ttt', out_filename='ttt1')

main()
