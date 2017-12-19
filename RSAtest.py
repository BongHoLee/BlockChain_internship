from Crypto.PublicKey import RSA


"""
def rsa_encrypt(msg) :
    private_key = RSA.generate(1024) # create private_key
    public_key = private_key.publickey() # create public_key
    encdata = public_key.encrypt(msg, 32) # msg encrypt using public_key
    print(encdata)

    decdata = private_key.decrypt(encdata) # decrypt msg using private_key
    print(decdata)

if __name__=='__main__' :
    msg = "i love you "
    rsa_encrypt(msg.encode('utf-8'))
"""


def createPEM() :
    private_key = RSA.generate(1024) # create private_key
    public_key = private_key.publickey()
    f = open('./mykey.txt', 'wb+')
    f.write(private_key.exportKey('PEM'))   # store encrpyted private_key into mykey.text
    f.close()
    g = open('./mypukey.txt', 'wb+')
    g.write(public_key.exportKey('PEM'))
    g.close()



if __name__=='__main__' :
    createPEM()


"""
def readPEM() :
    h = open('./mykey.txt', 'r')
    key = RSA.importKey(h.read())   #read private_key from mykey.txt
    h.close()
    return key

def rsa_enc(msg) :  # encryption msg using public_key
    private_key = readPEM()
    public_key = private_key.publickey()
    encdata = public_key.encrypt(msg, 32)
    return encdata

def rsa_dec(msg) :  # decryption msg using private_key
    private_key = readPEM()
    decdata = private_key.decrypt(msg)
    return decdata

if __name__=='__main__' :
    msg = 'hihi im lhi'
    ciphered = rsa_enc(msg.encode('utf-8'))
    print(ciphered)
    deciphered = rsa_dec(ciphered)
    print(deciphered)
"""
