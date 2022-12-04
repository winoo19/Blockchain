import requests
import json


def jsonify(response):
    try:
        return response.json()
    except ValueError:
        return {"Error": response.text}


"""INTRODUCIR NODOS A MANO: node1 host y node2 guest"""
node1 = "192.168.56.102:5000"
node2 = "192.168.56.101:5001"

# TRANSACCIONES AL NODO 1
transacciones = [
    {
        "origen": "A",
        "destino": "B",
        "cantidad": 4,
    },
    {
        "origen": "B",
        "destino": "C",
        "cantidad": 2,
    },
]

print("TRANSACCIONES AL NODO 1")
for transaccion in transacciones:
    r = requests.post(f"http://{node1}/transacciones/nueva", json=transaccion)
    print(jsonify(r))

# MINAR NODO 1
r = requests.get(f"http://{node1}/minar")
print(f"\nRESPUESTA MINAR NODO 1 ({node1})")
print(json.dumps(jsonify(r), indent=4))

# CADENA NODO 1
r = requests.get(f"http://{node1}/chain")
print(f"\nCHAIN NODO 1 ({node1})")
print(json.dumps(jsonify(r), indent=4))

# REGISTRAR NODO 2
r = requests.post(
    f"http://{node1}/nodos/registrar",
    json={"direccion_nodos": [f"http://{node2}"]},
)

print(f"\nRESPUESTA REGISTRAR NODO 2 ({node2})")
print(json.dumps(jsonify(r), indent=4))

# CADENA NODO 2
r = requests.get(f"http://{node2}/chain")
print(f"\nCHAIN NODO 2 ({node2})")
print(json.dumps(jsonify(r), indent=4))

# TRANSACCIONES AL NODO 1
transacciones = [
    {
        "origen": "H",
        "destino": "F",
        "cantidad": 7,
    },
    {
        "origen": "F",
        "destino": "A",
        "cantidad": 1,
    },
]

print("\nTRANSACCIONES AL NODO 2")
for transaccion in transacciones:
    r = requests.post(f"http://{node1}/transacciones/nueva", json=transaccion)
    print(jsonify(r))

# MINAR NODO 1
r = requests.get(f"http://{node1}/minar")
print(f"\nRESPUESTA MINAR NODO 1 ({node1})")
print(json.dumps(jsonify(r), indent=4))

# CADENA NODO 1
r = requests.get(f"http://{node1}/chain")
print(f"\nCHAIN NODO 1 ({node1})")
print(json.dumps(jsonify(r), indent=4))

# TRANSACCIONES AL NODO 2
transacciones = [
    {
        "origen": "H",
        "destino": "F",
        "cantidad": 7,
    }
]

print("\nTRANSACCIONES AL NODO 2")
for transaccion in transacciones:
    r = requests.post(f"http://{node2}/transacciones/nueva", json=transaccion)
    print(jsonify(r))

# MINAR NODO 2
r = requests.get(f"http://{node2}/minar")
print(f"\nRESPPUESTA MINAR NODO 2 ({node2})")
print(json.dumps(jsonify(r), indent=4))

# CADENA NODO 2
r = requests.get(f"http://{node2}/chain")
print(f"\nCHAIN NODO 2 ({node2})")
print(json.dumps(jsonify(r), indent=4))
