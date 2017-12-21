import EncDec

key = EncDec.Random.new().read(32)
enc_key = EncDec.rsa_enc(key)
dec_key = EncDec.rsa_dec(enc_key)
print(str(enc_key))
