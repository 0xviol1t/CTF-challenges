import tenseal.sealapi as sealapi
from random import randint
from signal import alarm
import base64

g = 5
poly_modulus_degree = 8192
plain_modulus = 163841

def gen_keys():
	parms = sealapi.EncryptionParameters(sealapi.SCHEME_TYPE.BFV)
	parms.set_poly_modulus_degree(poly_modulus_degree)
	parms.set_plain_modulus(plain_modulus)
	coeff = sealapi.CoeffModulus.BFVDefault(poly_modulus_degree, sealapi.SEC_LEVEL_TYPE.TC128)
	parms.set_coeff_modulus(coeff)
	
	ctx = sealapi.SEALContext(parms, True, sealapi.SEC_LEVEL_TYPE.TC128)
	
	keygen = sealapi.KeyGenerator(ctx)
	public_key = sealapi.PublicKey()
	keygen.create_public_key(public_key)
	secret_key = keygen.secret_key()
	
	parms.save("app/parms")
	public_key.save("app/public_key")
	secret_key.save("app/secret_key")

def load():
	parms = sealapi.EncryptionParameters(sealapi.SCHEME_TYPE.BFV)
	parms.load("app/parms")

	ctx = sealapi.SEALContext(parms, True, sealapi.SEC_LEVEL_TYPE.TC128)

	public_key = sealapi.PublicKey()
	public_key.load(ctx, "app/public_key")

	secret_key = sealapi.SecretKey()
	secret_key.load(ctx, "app/secret_key")
	return ctx, public_key, secret_key

def gen_galois_keys(ctx, secret_key, elt):
	keygen = sealapi.KeyGenerator(ctx, secret_key)
	galois_keys = sealapi.GaloisKeys()
	keygen.create_galois_keys(elt, galois_keys)
	galois_keys.save("app/galois_key")
	return galois_keys

def gen_polynomial(a):
	return '1x^' + str(a)

def f(a, b):
    return (pow(g, a-b, plain_modulus) + pow(g, b-a, plain_modulus) + pow(g, 3*a-b, plain_modulus) + pow(g, a-3*b, plain_modulus))%plain_modulus

def check_result(ctx, decryptor, a, b, pos):
	plaintext = sealapi.Plaintext()
	ciphertext = sealapi.Ciphertext(ctx)
	ciphertext.load(ctx, "app/computation")
	decryptor.decrypt(ciphertext, plaintext)
	assert plaintext[pos] == f(a, b)

def send(filepath):
	f = open(filepath, "rb")
	data = base64.b64encode(f.read()).decode()
	f.close()
	print(data)

def recv(filepath):
	try:
		data = base64.b64decode(input())
	except:
		print("Invalid Base64!")
		exit(0)

	f = open(filepath, "wb")
	f.write(data)
	f.close()

def main():
	ctx, public_key, secret_key = load()
	encryptor = sealapi.Encryptor(ctx, public_key)
	decryptor = sealapi.Decryptor(ctx, secret_key)
	
	a, b = [randint(1, poly_modulus_degree - 1) for _ in range(2)]
	poly_a, poly_b = gen_polynomial(a), gen_polynomial(b)

	plaintext_a, plaintext_b = sealapi.Plaintext(poly_a), sealapi.Plaintext(poly_b)
	ciphertext_a, ciphertext_b = [sealapi.Ciphertext() for _ in range(2)]
	encryptor.encrypt(plaintext_a, ciphertext_a)
	encryptor.encrypt(plaintext_b, ciphertext_b)
	ciphertext_a.save("app/ciphertext_a")
	ciphertext_b.save("app/ciphertext_b")
	galois_used = 0

	alarm(300)

	while True:
		try:
			choice = int(input("Give Me Your Choice:"))
		except:
			print("Invalid choice!")
			exit(0)

		if choice == 0:
			print("Here Is Ciphertext_a:")
			send("app/ciphertext_a")
			print("Here Is Ciphertext_b:")
			send("app/ciphertext_b")

		elif choice == 1:
			if galois_used == 1:
				print("No More!")
				exit(0)
			try:
				elt = int(input("Please give me your choice:"))
			except:
				print("Invalid input!")
				exit(0)

			try:
				galois_key = gen_galois_keys(ctx, secret_key, [elt])
			except:
				print("Invalid galois!")
				exit(0)

			print("Here is your galois key:")
			send("app/galois_key")
			galois_used = 1

		elif choice == 2:
			try:
				pos = int(input("Give Me Your Position:"))
				assert pos in range(poly_modulus_degree)
			except:
				print("Invalid position!")
				exit(0)

			print("Give Me Your Computation")
			recv("app/computation")
	
			try:
				check_result(ctx, decryptor, a, b, pos)
			except:
				print("Incorret Answer!")
				exit(0)

			flag = open("app/flag", "rb")
			print(flag.read())
			flag.close()

		else:
			print("Invalid choice!")
			break

# gen_keys()
main()






