import bcrypt

while True:
	print('input password:')
	password=input()
	hashpw=bcrypt.hashpw(password.encode('ascii'),bcrypt.gensalt())
	print(hashpw)