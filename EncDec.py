#-*- coding: utf-8 -*-
import struct, hashlib, time
import binascii
import os
from Crypto import Random
from Crypto.PublicKey import RSA
from Crypto.Cipher import AES



PrivateKeyPath = '/Users/leebongho/monitoring/keyDir/mykey.txt'
PublicKeyPath = '/Users/leebongho/monitoring/keyDir/mypukey.txt'
"""RSA KEY def"""

def readprivatePEM() :
    h = open(PrivateKeyPath, 'r')
    key = RSA.importKey(h.read())   #read private_key from mykey.txt
    h.close()
    return key

def readpublicPEM() :
    f = open(PublicKeyPath, 'r')
    key = RSA.importKey(f.read())   #read public_key from mypub.key.txt
    f.close()
    return key

def rsa_enc(msg) :  # encryption msg(AES_key) using public_key
    private_key = readprivatePEM()          #private_key를 읽어와서 저장
    public_key = private_key.publickey()    #해당 priavte_key를 이용해서 public_key를 가져옴
    encdata = public_key.encrypt(msg, 32)   #public_key를 이용해서 msg를 encryption
    return encdata

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

#AES KEY를 이용해서 영상을 암호화 하기 위함, key는 AES_KEY, in_filename은 영상 이름 삽입
def encrypt_file(key, in_filename, out_filename=None, chunksize=65536):
    if not out_filename:
        out_filename = in_filename + '.enc'
    iv = b'initialvector123'                    #초기화 벡터를 따로 지정해줌, 이후 복호화 할 때에도 무조건 필요
    encryptor = AES.new(key, AES.MODE_CBC, iv)  #AES key와 초기화벡터(iv)를 이용해서 CBC모드로 암호화 하기 위한 객체
    filesize = os.path.getsize(in_filename)     #암호화 하려는 영상 파일의 크기를 가져옴
    with open(in_filename, 'rb') as infile:     #영상 파일의 내용을 infile이라는 이름으로 저장
        with open(out_filename, 'wb') as outfile:   #원본 영상 파일을 암호화파일로 만들기 위함
            outfile.write(struct.pack('<Q', filesize))  #struct.pack은 형변환. 즉 원본파일의 사이즈 만큼 형변환해서 암호화
            outfile.write(iv)                           #초기화 벡터를 같이 넣어준다.
            while True:
                chunk = infile.read(chunksize)          #원본파일을 chunksize만큼 읽어서 chunk변수에 저장
                if len(chunk) == 0:                     #chunk 사이즈가 0이라면 (읽어온 내용이 없다면) 암호화 종료
                    break
                elif len(chunk) % 16 != 0:                  #읽어온 사이즈가 16바이트로 나누어 떨어지지 않는다면 나누어 떨어질만큼 공백을 삽입
                    chunk += b' ' * (16 - len(chunk) % 16)
                outfile.write(encryptor.encrypt(chunk))     #chunk크기만큼 AES_key로 암호화 
