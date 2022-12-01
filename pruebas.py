import requests
import json

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

for transaccion in transacciones:
    r = requests.post("http://localhost:5000/transacciones/nueva", json=transaccion)

"""minar"""
r = requests.get("http://localhost:5000/minar")

"""comprobar la cadena"""
r = requests.get("http://localhost:5000/chain")
print("CHAIN")
print(json.dumps(r.json(), indent=4))

"""register nodes"""
r = requests.post(
    "http://localhost:5000/nodos/registrar",
    json={"direccion_nodos": ["http://172.24.133.118:5001"]},
)

print("NODOS")
print(json.dumps(r.json(), indent=4))

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

for transaccion in transacciones:
    r = requests.post("http://localhost:5000/transacciones/nueva", json=transaccion)


"""minar"""
r = requests.get("http://localhost:5000/minar")

"""comprobar la cadena"""
r = requests.get("http://localhost:5000/chain")

print("CHAIN")
print(json.dumps(r.json(), indent=4, sort_keys=True))

transacciones = [
    {
        "origen": "H",
        "destino": "F",
        "cantidad": 7,
    }
]

for transaccion in transacciones:
    r = requests.post("http://localhost:5001/transacciones/nueva", json=transaccion)

"""minar"""
r = requests.get("http://localhost:5001/minar")

print("MINAR")
print(json.dumps(r.json(), indent=4, sort_keys=True))
