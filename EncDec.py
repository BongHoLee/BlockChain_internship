#-*- coding: utf-8 -*-
import struct, hashlib, time
import binascii
import os
from Crypto import Random
from Crypto.PublicKey import RSA
from Crypto.Cipher import AES



PrivateKeyPath = '/Users/leebongho/monitoring/keyDir/mykey.txt'                     #private key path
PublicKeyPath = '/Users/leebongho/monitoring/keyDir/mypukey.txt'                    #public key path
"""RSA KEY def"""

def readprivatePEM() :              #function to read private_key
    h = open(PrivateKeyPath, 'r')
    key = RSA.importKey(h.read())   #read private_key from mykey.txt
    h.close()
    return key                      #return private_key

def readpublicPEM() :               #funtion to read public_key
    f = open(PublicKeyPath, 'r')
    key = RSA.importKey(f.read())   #read public_key from mypub.key.txt
    f.close()
    return key                      #return public_key

def rsa_enc(msg) :  # encryption msg(AES_key) using public_key
    private_key = readprivatePEM()          #store private key using function
    public_key = private_key.publickey()    #create public_key using private_key
    encdata = public_key.encrypt(msg, 32)   #encrypt msg(AES_KEY) using public_key
    return encdata                          #return encrypted AES_KEY(Enc_AES)

def rsa_dec(msg) :  # decryption msg(enc_AES_KEY) using private_key
    private_key = readprivatePEM()
    decdata = private_key.decrypt(msg)
    return decdata

""" RSA KEY def END """



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

#To encrypt the clip using AES key, 'key' = AES_KEY, 'in_filename' = clip name.
def encrypt_file(key, in_filename, out_filename=None, chunksize=65536):
    if not out_filename:
        out_filename = in_filename + '.enc'
    iv = b'initialvector123'                    #Specify the initialization vector separately. This initialization vector is also necessary for decoding later.
    encryptor = AES.new(key, AES.MODE_CBC, iv)  #An object to encrypt in CBC mode using AES key and initialization vector (iv).
    filesize = os.path.getsize(in_filename)     #Get the size of the clip to be encrypted.
    with open(in_filename, 'rb') as infile:     #Save the contents of the clip as infile
        with open(out_filename, 'wb') as outfile:   #To make the original clip file into an encrypted file.
            outfile.write(struct.pack('<Q', filesize))  #Casting. That is, the encryption is performed according to the size of the original file.
            outfile.write(iv)                           #Put initialization vector together.
            while True:
                chunk = infile.read(chunksize)          #Read the original file by chunksize and store it in the chunk variable.
                if len(chunk) == 0:                     #if the size of the chunk is 0 (if it is not read), the encryption ends.
                    break
                elif len(chunk) % 16 != 0:                  #if the size you read is not divided by 16 bytes, insert a space to divide it.
                    chunk += b' ' * (16 - len(chunk) % 16)
                outfile.write(encryptor.encrypt(chunk))     #Encrypted with chunk size AES_key. 
