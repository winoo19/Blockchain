import requests
import json
import socket

mi_ip = socket.gethostbyname(socket.gethostname())

"""TRANSACCIONES AL NODO 1 (5000)"""
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
    r = requests.post(f"http://{mi_ip}:5000/transacciones/nueva", json=transaccion)

"""MINAR NODO 1 (5000)"""
r = requests.get(f"http://{mi_ip}:5000/minar")
# print("RESPUESTA MINAR NODO 1 (5000)")
# print(
#     json.dumps(
#         r.json() if r.status_code // 100 == 2 else {"ERROR" + str(r.status_code)},
#         indent=4,
#     )
# )

"""CADENA NODO 1 (5000)"""
r = requests.get(f"http://{mi_ip}:5000/chain")
# print("CHAIN NODO 1 (5000)")
# print(
#     json.dumps(
#         r.json() if r.status_code // 100 == 2 else {"ERROR" + str(r.status_code)},
#         indent=4,
#     )
# )

"""REGISTRAR NODO 2 (5001)"""
r = requests.post(
    f"http://{mi_ip}:5000/nodos/registrar",
    json={"direccion_nodos": [f"http://{mi_ip}:5001"]},
)

# print("RESPUESTA REGISTRAR NODO 2 (5001)")
# print(
#     json.dumps(
#         r.json() if r.status_code // 100 == 2 else {"ERROR" + str(r.status_code)},
#         indent=4,
#     )
# )
# """CADENA NODO 2 (5001)"""
# r = requests.get(f"http://{mi_ip}:5001/chain")
# print("CHAIN NODO 2 (5001)")
# print(
#     json.dumps(
#         r.json() if r.status_code // 100 == 2 else {"ERROR" + str(r.status_code)},
#         indent=4,
#     )
# )

"""TRANSACCIONES AL NODO 1 (5000)"""
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
    r = requests.post(f"http://{mi_ip}:5000/transacciones/nueva", json=transaccion)


"""MINAR NODO 1 (5000)"""
r = requests.get(f"http://{mi_ip}:5000/minar")

"""CADENA NODO 1 (5000)"""
r = requests.get(f"http://{mi_ip}:5000/chain")

print("CHAIN NODO 1 (5000)")
print(
    json.dumps(
        r.json() if r.status_code // 100 == 2 else {"ERROR" + str(r.status_code)},
        indent=4,
    )
)

"""TRANSACCIONES AL NODO 2 (5001)"""
transacciones = [
    {
        "origen": "H",
        "destino": "F",
        "cantidad": 7,
    }
]

for transaccion in transacciones:
    r = requests.post(f"http://{mi_ip}:5001/transacciones/nueva", json=transaccion)

"""MINAR NODO 2 (5001)"""
r = requests.get(f"http://{mi_ip}:5001/minar")

print("RESPPUESTA MINAR NODO 2 (5001)")
print(
    json.dumps(
        r.json() if r.status_code // 100 == 2 else {"ERROR" + str(r.status_code)},
        indent=4,
    )
)
