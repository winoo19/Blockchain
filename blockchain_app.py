import BlockChain
from uuid import uuid4
import socket
from flask import Flask, jsonify, request
from argparse import ArgumentParser
import threading
import json
import time
from datetime import datetime

mutex = threading.Semaphore(1)

def copia():
    while True:
        time.sleep(60)
        mutex.acquire()
        with open(f"respaldo-nodo{mi_ip}-{puerto}.json", "w") as j:
            dic = {
                "chain": blockchain.chain,
                "longitud": blockchain.n_bloques,
                "date": datetime.now().strftime(r"%d/%m/%Y %H:%M:%S")
            }
            json.dump(dic, j)
        mutex.release()

thread = threading.Thread(target=copia)

# Instancia del nodo
app =Flask(__name__)
# Instanciacion de la aplicacion
blockchain = BlockChain.Blockchain()
# Para saber mi ip
mi_ip =socket.gethostbyname(socket.gethostname())


@app.route('/transacciones/nueva', methods=['POST'])
def nueva_transaccion():
    values =request.get_json()
    # Comprobamos que todos los datos de la transaccion estan
    required =['origen', 'destino', 'cantidad']
    if not all(k in values for k in required):
        return 'Faltan valores', 400
    # Creamos una nueva transaccion aqui
    index = blockchain.n_bloques+1
    response ={'mensaje': f'La transaccion se incluira en el bloque con indice {index}'}

    blockchain.nueva_transaccion(**values)

    return jsonify(response), 201


@app.route('/chain', methods=['GET'])
def blockchain_completa():
    response = {
    # Solamente permitimos la cadena de aquellos bloques finales que tienen hash
    'chain': [b.toDict() for b in blockchain.chain if b.hash is not None],
    'longitud': blockchain.n_bloques # longitud de la cadena
    }
    return jsonify(response), 200


@app.route('/minar', methods=['GET'])
def minar():
    # No hay transacciones
    if len(blockchain.pool) == 0:
        response = {
        'mensaje': "No es posible crear un nuevo bloque. No hay transacciones"
        }
    else:
        # Hay transaccion, por lo tanto ademas de minar el bloque, recibimos recompensa
        previous_hash = blockchain.chain[-1].hash
        new_block = blockchain.nuevo_bloque(previous_hash)
        hash_prueba = blockchain.prueba_trabajo(new_block)
        if blockchain.integra_bloque(new_block, hash_prueba):
            response = {
                "mensaje": "Nuevo bloque minado",
                "indice": new_block.indice,
                "transacciones": new_block.transacciones,
                "valor_prueba": new_block.prueba,
                "hash_previo": new_block.hash_previo,
                "hash": new_block.hash,
                "timestamp": new_block.timestamp
            }
            # Recibimos un pago por minar el bloque. Creamos una nueva transaccion con:
            pago = blockchain.nueva_transaccion(origen=0, destino=mi_ip, cantidad=1)
        else:
            response = {
                "mensaje": "No es posible crear un nuevo bloque. Fallo al hacer la prueba"
            }
    return jsonify(response), 200


if __name__ =='__main__':
    parser = ArgumentParser()
    parser.add_argument('-p', '--puerto', default = 5000, type = int, help = 'puerto para escuchar')
    args = parser.parse_args()
    puerto = args.puerto
    app.run(host= '0.0.0.0', port=puerto)
