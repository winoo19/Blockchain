# Authors:
# - Sergio Herreros Perez
# - Daniel Sanchez Sanchez


import BlockChain
import re, time, json, threading, platform
from datetime import datetime
from argparse import ArgumentParser
import requests
from flask import Flask, jsonify, request
import psutil

# Instancia del nodo
app = Flask(__name__)
# Instanciacion de la aplicacion
blockchain = BlockChain.Blockchain()
"""INTRODUCIR IP A MANO"""
mi_ip = "192.168.1.45"
# Nodos peer-to-peer
nodos_red = set()
# Semaphore
mutex = threading.Semaphore(1)
# End thread
end_thread = False


def copia():
    """Crea una copia de seguridad de la blockchain cada 60 segundos"""
    while not end_thread:
        n = 10000
        for _ in range(n):
            time.sleep(60 / n)
            if end_thread:
                return None
        mutex.acquire()
        with open(f"respaldo-nodo{mi_ip}-{puerto}.json", "w") as j:
            dic = {
                "chain": [block.toDict() for block in blockchain.chain],
                "longitud": blockchain.n_bloques,
                "date": datetime.now().strftime(r"%d/%m/%Y %H:%M:%S"),
            }
            json.dump(dic, j)
        mutex.release()


@app.route("/system", methods=["GET"])
def system():
    """Devuelve informacion del hardware y software del nodo"""
    return jsonify(
        {
            "hardware": {
                "cpu_usage": str(psutil.cpu_percent()) + "%",
                "ram_usage": str(psutil.virtual_memory().percent) + "%",
                "drive_usage": str(psutil.disk_usage("/").percent) + "%",
                "cpu_count": psutil.cpu_count(),
                "cpu_freq": str(psutil.cpu_freq().current) + "Mhz",
            },
            "software": {
                "sistema": platform.platform(),
                "version": platform.release(),
                "python": platform.python_version(),
            },
        }
    )


@app.route("/transacciones/nueva", methods=["POST"])
def nueva_transaccion():
    """Creates a new transaction
    Input: json with the transaction
    Output: json with the transaction and the status
    """
    values = request.get_json()

    # Comprobamos que todos los datos de la transaccion están
    required = ["origen", "destino", "cantidad"]
    if not all(k in values for k in required):
        response = {
            "mensaje": f"Error: Faltan datos en la transaccion",
        }
        return jsonify(response), 400

    index = blockchain.n_bloques + 1
    response = {
        "mensaje": f"La transaccion se incluira en el bloque con indice {index}"
    }

    # Añadimos la transaccion a la pool
    blockchain.nueva_transaccion(**values)

    return jsonify(response), 200


@app.route("/chain", methods=["GET"])
def blockchain_completa():
    """Devuelve un json con la chain completa y su longitud"""
    try:
        response = {
            # Solamente permitimos la cadena de aquellos bloques finales que tienen hash
            "chain": [b.toDict() for b in blockchain.chain if b.hash],
            "longitud": blockchain.n_bloques,  # longitud de la cadena
        }
    except Exception as e:
        response = {
            "mensaje": f"Error: {e}",
        }
        return jsonify(response), 500
    return jsonify(response), 200


@app.route("/minar", methods=["GET"])
def minar():
    # No hay transacciones
    if len(blockchain.pool) == 0:
        response = {
            "mensaje": "No es posible crear un nuevo bloque. No hay transacciones"
        }
        return jsonify(response), 201

    # Hay transaccion
    # Recibimos un pago por minar el bloque
    pago = {"origen": "0", "destino": mi_ip, "cantidad": 1}
    previous_hash = blockchain.chain[-1].hash
    blockchain.nueva_transaccion(**pago)

    # Creamos el bloque
    new_block = blockchain.nuevo_bloque(previous_hash)

    # Minamos el bloque
    hash_prueba = blockchain.prueba_trabajo(new_block)

    # Comprobamos si hay conflictos y si lo hay, reemplazamos la cadena
    conflicto = resuelve_conflictos()

    if conflicto:
        response = {
            "mensaje": "Conflicto: No es posible crear un nuevo bloque. Existe una cadena mas larga."
        }
        return jsonify(response), 202

    if blockchain.integra_bloque(new_block, hash_prueba):
        response = {
            "mensaje": "Nuevo bloque minado",
            "indice": new_block.indice,
            "transacciones": list(sorted(new_block.transacciones)),
            "valor_prueba": new_block.prueba,
            "hash_previo": new_block.hash_previo,
            "hash": new_block.hash,
            "timestamp": new_block.timestamp,
        }
        return jsonify(response), 200

    response = {
        "mensaje": "No es posible crear un nuevo bloque. Fallo al hacer la prueba"
    }
    return jsonify(response), 203


@app.route("/nodos/registrar", methods=["POST"])
def registrar_nodos_completo():
    """
    Incluye nuevos nodos en la red, compartiendoles la cadena y el resto de nodos
    Input: json con la lista de nodos
    Output: json con la lista de nodos y el status
    """
    global blockchain, nodos_red

    values = request.get_json()
    nodos_nuevos = values.get("direccion_nodos")

    if nodos_nuevos is None:
        response = {"mensaje": "Error: No se ha proporcionado una lista de nodos"}
        return jsonify(response), 400

    # Comprobar que los nodos son strings con formato http://ip:puerto
    nodos_nuevos = set(nodos_nuevos)
    pattern = re.compile(r"^http://\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}:\d{1,5}$")

    nodes_error_format = set()  # Set con nodos que no tienen el formato correcto

    for nodo in nodos_nuevos:
        if type(nodo) != str or not pattern.match(nodo):
            nodes_error_format.add(nodo)

    # Enviar la blockchain y la lista de nodos a los nuevos nodos
    nodos_nuevos = nodos_nuevos - nodes_error_format
    blockchain_copy = blockchain.toDict()  # Blockchain con toda la pool
    nodes_error_register = set()  # Nodes that could not be registered
    for nodo in nodos_nuevos:
        send_nodos = nodos_red | nodos_nuevos
        send_nodos.remove(nodo)
        send_nodos.add(f"http://{mi_ip}:{puerto}")
        try:
            r = requests.post(
                f"{nodo}/nodos/registro_simple",
                json={
                    "direccion_nodos": list(send_nodos),
                    "blockchain": blockchain_copy,
                },
            )
            if r.status_code != 200:
                nodes_error_register.add(nodo)
        except Exception as e:
            print(e)
            nodes_error_register.add(nodo)

    # Añadimos los nodos nuevos bien conectados a la red
    for nodo in nodos_nuevos - nodes_error_register:
        nodos_red.add(nodo)

    # Fin codigo a desarrollar
    if len(nodes_error_format) == 0 and len(nodes_error_register) == 0:
        response = {
            "mensaje": "Se han incluido nuevos nodos en la red",
            "nodos_totales": list(nodos_red) + [f"http://{mi_ip}:{puerto}"],
        }
        return jsonify(response), 200

    # mensaje de error con los nodos y el fallo
    response = {
        "mensaje": "Error de formato en los nodos: "
        + str(nodes_error_format)
        + ". Error al registrar los nodos: "
        + str(nodes_error_register),
    }
    return jsonify(response), 201


@app.route("/nodos/registro_simple", methods=["POST"])
def registrar_nodo_actualiza_blockchain():
    """Actualiza el nodo con una copia de la blockchain y la lista de nodos
    Input: json con la lista de nodos y la blockchain entera como dict
    Output: json con mesaje y el status
    """
    global blockchain, nodos_red

    read_json = request.get_json()
    nodes_addreses = read_json.get("direccion_nodos")

    if nodes_addreses is None:
        response = {"mensaje": "Error: No se ha proporcionado una lista de nodos"}
        return jsonify(response), 400

    # Actualizamos los nodos de la red
    nodos_red = set(nodes_addreses)

    new_blockchain = read_json.get("blockchain")
    if new_blockchain is None:
        return "Error: No se ha proporcionado una cadena de bloques", 401

    blockchain_leida = BlockChain.Blockchain().fromDict(new_blockchain)

    # Comprobamos si la cadena es valida
    if blockchain_leida.check_chain() == False:
        response = {
            "mensaje": "El blockchain de la red esta currupto",
        }
        print("El blockchain de la red esta currupto")
        print("Blockchain leido:")
        print(jsonify(blockchain_leida.toDict()))
        return jsonify(response), 402

    # Actualizamos la blockchain
    blockchain = blockchain_leida

    response = {
        "mensaje": "La blockchain del nodo"
        + str(mi_ip)
        + ":"
        + str(puerto)
        + "ha sido correctamente actualizada"
    }
    return jsonify(response), 200


def resuelve_conflictos():
    """
    Mecanismo para establecer el consenso y resolver los conflictos.
    Al minar un bloque, comprueba la cadena de cada nodo en la red. Si
    encuentra una cadena mas larga, la sustituye por la suya y si no
    integra el bloque en la cadena.
    """
    global blockchain

    longitud_actual = len(blockchain.chain)
    longest_chain = None
    max_length = longitud_actual

    # Comprobamos si hay alguna cadena mas larga
    for node in nodos_red:
        try:
            r = requests.get(f"{node}/chain")
            if r.status_code == 200:
                response = r.json()
                node_chain = response["chain"]
                node_length = response["longitud"]
                node_blockchain = BlockChain.Blockchain().fromChain(node_chain)
                if node_length > max_length and node_blockchain.check_chain():
                    max_length = node_length
                    longest_chain = node_chain
        except Exception as e:
            # Disconnected node
            print("Error contacting node " + node, e)

    # Si la cadena mas larga no es la nuestra, la sustituimos por la mas larga
    if longest_chain is not None:
        new_chain = []
        for i, block in enumerate(longest_chain):
            # Quitamos de nuestra pool transacciones ya incluidas en la nueva cadena
            if i >= longitud_actual:
                blockchain.pool = blockchain.pool - set(block["transacciones"])

            # Creamos los bloques de la cadena a partir de los dicts
            new_chain.append(BlockChain.Bloque().fromDict(block))

        # Actualizamos la blockchain
        blockchain.chain = new_chain
        blockchain.n_bloques = len(blockchain.chain)

        return True
    # Si la cadena mas larga es la nuestra, no hacemos nada
    return False


if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument(
        "-p", "--puerto", default=5000, type=int, help="puerto para escuchar"
    )
    args = parser.parse_args()
    puerto = args.puerto
    backup = threading.Thread(target=copia)
    backup.start()
    app.run(host=f"{mi_ip}", port=puerto)
    end_thread = True
    backup.join()
