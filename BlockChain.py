import json
import hashlib
from time import time
from typing import List, Dict

DIFICULTAD = 1
HASH_VACIO = ""


class Bloque:
    def __init__(
        self,
        indice: int = 0,
        transacciones: set[str] = set(),
        timestamp: float = 0,
        hash_previo: str = "",
        prueba: int = 0,
    ):
        """
        Constructor de la clase 'Bloque'.
        :param indice: ID unico del bloque.
        :param transacciones: Lista de transacciones.
        :param timestamp: Momento en que el bloque fue generado.
        :param hash_previo: hash previo
        :param prueba: prueba de trabajo
        """
        self.indice = indice
        self.transacciones = transacciones
        self.timestamp = timestamp
        self.hash_previo = hash_previo
        self.prueba = prueba

        self.hash = HASH_VACIO

    def calcular_hash(self):
        """
        Metodo que devuelve el hash de el bloque. No se incluye el hash del bloque
        en el calculo del hash.
        """
        dict_without_hash = self.toDict()
        dict_without_hash["hash"] = HASH_VACIO
        block_string = json.dumps(dict_without_hash, sort_keys=True)
        return hashlib.sha256(block_string.encode()).hexdigest()

    def toDict(self):
        """
        Convierte el bloque en un diccionario y las transacciones en una lista
        para poder ser serializado por json.
        """
        d = self.__dict__.copy()
        d["transacciones"] = list(d["transacciones"])
        return d

    def fromDict(self, d):
        """
        Crea el bloque a partir de un diccionario.
        Convierte las transacciones en un set.
        """
        self.indice = d["indice"]
        self.transacciones = set(d["transacciones"])
        self.timestamp = d["timestamp"]
        self.hash_previo = d["hash_previo"]
        self.prueba = d["prueba"]
        self.hash = d["hash"]
        return self


class Blockchain:
    def __init__(self):
        self.chain: List[Bloque] = []
        self.dificultad = DIFICULTAD
        self.pool = set()
        self.n_bloques = 0

        self.primer_bloque()

    def primer_bloque(self):
        """
        Crea el bloque inicial vacío, con tiempo 0 y hash previo de 1 y lo integra
        """

        bloque = self.nuevo_bloque(hash_previo="1")
        hash_bloque = self.prueba_trabajo(bloque)
        self.integra_bloque(bloque, hash_bloque)

    def nuevo_bloque(self, hash_previo: str) -> Bloque:
        """
        Crea un nuevo bloque a partir de las transacciones que no estan
        confirmadas
        :param prueba: el valor de prueba a insertar en el bloque
        :param hash_previo: el hash del bloque anterior de la cadena
        :return: el nuevo bloque
        """

        new_block = Bloque(
            indice=self.n_bloques + 1,
            transacciones=self.pool.copy(),  # Copia para que no se añadan nuevas transacciones
            timestamp=time(),
            hash_previo=hash_previo,
            prueba=0,
        )
        return new_block

    def nueva_transaccion(self, origen: str, destino: str, cantidad: int) -> int:
        """
        Crea una nueva transaccion a partir de un origen, un destino y una
        cantidad y la incluye en el set de transacciones.
        """
        transaccion = {"origen": origen, "destino": destino, "cantidad": cantidad}
        self.pool.add(str(transaccion))

    def prueba_trabajo(self, bloque: Bloque) -> str:
        """
        Calcula el nonce que hace que el hash del bloque comience con tantos
        ceros como la dificultad.
        Return: el hash del bloque con el nonce encontrado (str)
        """
        new_hash = "0" * (self.dificultad - 1) + "1"

        while new_hash[: self.dificultad] != "0" * self.dificultad:
            bloque.prueba += 1
            new_hash = bloque.calcular_hash()

        return new_hash

    def prueba_valida(self, bloque: Bloque, hash_bloque: str) -> bool:
        """
        Metodo que comprueba si el hash del bloque comienza con tantos ceros como la
        dificultad estipulada en el blockchain y que su hash realmente coincide
        con el calculado.
        Si cualquiera de ambas comprobaciones es falsa, devolvera falso y en caso
        contrario, verdadero
        """
        print(json.dumps(bloque.toDict(), indent=4))
        print("HASH BLOQUE: ", hash_bloque)
        print("CALCULADO: ", bloque.calcular_hash())
        if hash_bloque[: self.dificultad] != "0" * self.dificultad:
            return False

        if bloque.calcular_hash() != hash_bloque:
            return False

        return True

    def integra_bloque(self, bloque_nuevo: Bloque, hash_prueba: str) -> bool:
        """
        Metodo para integrar correctamente un bloque a la cadena de bloques.
        Debe comprobar que la prueba de hash es valida y que el hash del bloque
        ultimo de la cadena coincida con el hash_previo del bloque que se va a
        integrar. Si pasa las comprobaciones, actualiza el hash del bloque a
        integrar, lo inserta en la cadena y reiniicia el pool de transacciones.
        Return: True si se ha podido ejecutar bien y False si no pasa las
        comprobaciones.
        """
        if self.n_bloques > 0 and bloque_nuevo.hash_previo != self.chain[-1].hash:
            return False

        if not self.prueba_valida(bloque_nuevo, hash_prueba):
            return False

        bloque_nuevo.hash = hash_prueba
        self.chain.append(bloque_nuevo)
        # No reiniciamos la pool del todo porque entre crear bloque e integrar bloque puede pasar tiempo
        # y se pueden añadir nuevas transacciones
        self.pool = self.pool - bloque_nuevo.transacciones
        self.n_bloques += 1
        return True

    def check_chain(self):
        """
        Metodo que comprueba la integridad de la cadena de bloques. Para ello
        recorre la cadena de bloques y comprueba que el hash del bloque actual
        coincide con el hash_previo del siguiente bloque y que el bloque es valido.
        Return: True si la cadena es valida y False en caso contrario
        """
        for i in range(len(self.chain) - 1):
            # Check Bloque
            if not self.prueba_valida(self.chain[i], self.chain[i].hash):
                print("Bloque no valido")
                return False
            # Check cahin link
            if self.chain[i].hash != self.chain[i + 1].hash_previo:
                print("Hash previo no coincide")
                return False
        return True

    def toDict(self):
        """
        Convierte la cadena de bloques a un diccionario para poder guardarlo en
        un archivo JSON. Convierte cada bloque a un diccionario y la pool de
        transacciones a lista.
        """
        d = {}
        d["chain"] = [b.toDict() for b in self.chain]
        d["dificultad"] = self.dificultad
        d["pool"] = list(self.pool)
        d["n_bloques"] = self.n_bloques
        return d

    def fromDict(self, d):
        """
        Crea un blockchain a partir de un diccionario. Crea cada bloque a partir
        de su diccionario y la pool como un set a partir de la lista.
        """
        self.chain = [Bloque().fromDict(b) for b in d["chain"]]
        self.dificultad = d["dificultad"]
        self.pool = set(d["pool"])
        self.n_bloques = d["n_bloques"]
        return self

    def fromChain(self, chain: dict):
        """
        Crea un blockchain a partir de una cadena de bloques. Crea cada bloque a
        partir de su diccionario e inicia el resto de variables vacias.
        Se usa para comprobar que la cadena de bloques es valida en
        BlochChain.py
        """
        self.chain = [Bloque().fromDict(b) for b in chain]
        self.dificultad = DIFICULTAD
        self.pool = set()
        self.n_bloques = len(chain)
        return self


if __name__ == "__main__":
    blockchain = Blockchain()
    b = blockchain.nuevo_bloque("puto")
    b.hash = blockchain.prueba_trabajo(b)
    print(b.hash)

    print(blockchain.prueba_valida(b, b.hash))
