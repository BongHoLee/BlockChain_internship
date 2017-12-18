from cryptography.fernet import Fernet

key_="O_zKs6lYhUv8pwULcE6PhYrYQKlTHK9aoVX1L0ARL8A="
f = Fernet(key_)
decrtext=f.decrypt("gAAAAABaN8i3dirpGomJIgBzy4N9FrBkMtE5NIzC4YbqwvdsEDPWaQ9leUIoa55j4dKtsGEvF16e5h-Z4G1cCV8DVRl27XimbcNFJ62oJ3iqg_d-DzXDsLkN1kkUToyXnA14Jr-5bS-e")
print(decrtext)
