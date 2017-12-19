from cryptography.fernet import Fernet
#key = 'MOS_qUK9KH-sicUvBo5suyhbY93z5pmhf1DyirT7qNY='
key = "dk-FEY7AmROplK2P_gp-xhfj0G-8c_UeqiEVu4YHfd4="
f = Fernet(key)
cipher_text = f.encrypt(b"QmW9RJ7nncAmx1mJZKPwTsNQrAjqGBxHh4b9mMuRzbRhmh")
cipher_text2 = f.encrypt(b"aaahihi")
cipher_text3 = f.encrypt(b"aaahihidsfdsfdsfa")
plain_text = f.decrypt(cipher_text)
plain_text2 = f.decrypt(cipher_text2)
plain_text3 = f.decrypt(cipher_text3)
print("encrypt text1 : " + cipher_text)
print("encrypt text2 : " + cipher_text2)
print("encrypt text3 : " + cipher_text3)

print("decrypt text1 : " + plain_text)
print("decrypt text2 : " + plain_text2)
print("decrypt text3 : " + plain_text3)

#print(cipher_text)
print("decrypt key : " + key)
