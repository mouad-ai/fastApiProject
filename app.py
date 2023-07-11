from flask import Flask, request, jsonify
import random

# Paramètres ECC
p = 23  # Modulo premier
a = 1   # Paramètre de la courbe elliptique
b = 6   # Paramètre de la courbe elliptique
G = (9, 7)  # Point de base
n = 16  # Ordre du point de base


def extended_gcd(a, b):
    # Algorithme d'Euclide étendu pour trouver le PGCD et les coefficients de Bézout
    if b == 0:
        return a, 1, 0
    d, x, y = extended_gcd(b, a % b)
    return d, y, x - (a // b) * y

def inv_modulo(a, m):
    # Calcul de l'inverse modulaire de 'a' modulo 'm' en utilisant l'algorithme d'Euclide étendu
    _, x, _ = extended_gcd(a, m)
    return x % m

def add_points(p1, p2):
    # Addition de deux points sur la courbe elliptique
    if p1 is None:
        return p2
    if p2 is None:
        return p1
    x1, y1 = p1
    x2, y2 = p2
    if x1 == x2 and y1 == y2:
        l = (3 * x1 * x1 + a) * inv_modulo(2 * y1, p) % p
    else:
        l = (y2 - y1) * inv_modulo(x2 - x1, p) % p
    x3 = (l * l - x1 - x2) % p
    y3 = (l * (x1 - x3) - y1) % p
    return x3, y3

def multiply_point(k, point):
    # Multiplication d'un point sur la courbe elliptique par un scalaire
    result = None
    current = point
    while k > 0:
        if k & 1 == 1:
            result = add_points(result, current)
        current = add_points(current, current)
        k >>= 1
    return result

def generate_key_pair():
    # Génère une paire de clés (clé privée et clé publique)
    private_key = random.randint(1, n - 1)
    public_key = multiply_point(private_key, G)
    return private_key, public_key

def generate_shared_secret(private_key, public_key):
    # Génère un secret partagé en utilisant la clé privée et la clé publique
    shared_secret_point = multiply_point(private_key, public_key)
    shared_secret = shared_secret_point[0]
    return shared_secret

def rc4(key, data):
    # Algorithme de chiffrement RC4

    key = bytearray(key)
    data = bytearray(data)
    j = 0
    result = bytearray()

    # Phase de programmation de la clé
    S = list(range(256))
    for i in range(256):
        j = (j + S[i] + key[i % len(key)]) % 256
        S[i], S[j] = S[j], S[i]

    i = j = 0
    for byte in data:
        # Génération pseudo-aléatoire du flux de chiffrement
        i = (i + 1) % 256
        j = (j + S[i]) % 256
        S[i], S[j] = S[j], S[i]
        # Chiffrement du byte avec le flux de chiffrement
        result.append(byte ^ S[(S[i] + S[j]) % 256])

    return result
# Rest of the functions from the code snippe

server_private_key, server_public_key = generate_key_pair()

app = Flask(__name__)


# Generate and provide the server's public key
@app.route('/public_key', methods=['GET'])
def get_public_key():
    return jsonify({'public_key': server_public_key})


@app.route('/', methods=['GET'])
def hello():
    return "MOuad : hello world"



@app.route('/decrypt_message', methods=['POST'])
def decrypt_message():
    # Receive the encrypted message from the client
    encrypted_hex = request.json['encrypted_message']

    encrypted_data = bytes.fromhex(encrypted_hex)

    # Generate key pairs

    client_public_key = request.json['client_public_key']


    # Generate shared secrets
    server_shared_secret = generate_shared_secret(server_private_key, client_public_key)

    # Decrypt the message using RC4 and the shared secret
    decrypted_data = rc4(server_shared_secret.to_bytes(16, 'big'), encrypted_data)
    decrypted_message = decrypted_data.decode('utf-8')


    print('decrypted_message', decrypted_message)
    # Return the decrypted message as JSON
    string = "successful request "
    return jsonify({'response': string})


if __name__ == '__main__':
    app.run(debug=False,host='0.0.0.0')
