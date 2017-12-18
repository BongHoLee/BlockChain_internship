from cryptography.fernet import Fernet
#key = 'MOS_qUK9KH-sicUvBo5suyhbY93z5pmhf1DyirT7qNY='
key = Fernet.generate_key()
f = Fernet(key)
cipher_text = f.encrypt(b"QmW9RJ7nncAmx1mJZKPwTsNQrAjqGBxHh4b9mMuRzbRhmh")
plain_text = f.decrypt(cipher_text)
print("encrypt text : " + cipher_text)
#print(cipher_text)
print("decrypt key : " + key)
