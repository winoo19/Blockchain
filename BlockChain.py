import json
import hashlib
from time import time
from typing import List

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

    def calcular_hash(self) -> str:
        """
        Metodo que devuelve el hash de el bloque. No se incluye el hash del bloque
        en el calculo del hash.
        """
        dict_without_hash = self.toDict()
        dict_without_hash["hash"] = HASH_VACIO
        block_string = json.dumps(dict_without_hash, sort_keys=True)
        return hashlib.sha256(block_string.encode()).hexdigest()

    def toDict(self) -> dict:
        """
        Convierte el bloque en un diccionario y las transacciones en una lista
        para poder ser serializado por json.
        """
        d = self.__dict__.copy()
        d["transacciones"] = list(d["transacciones"])
        # Ordena las transacciones para que el hash sea siempre el mismo
        d["transacciones"].sort()
        return d

    def fromDict(self, d: dict):
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

        self._primer_bloque()

    def _primer_bloque(self):
        """
        Crea el bloque inicial vacío y lo integra a la cadena
        """
        bloque = self.nuevo_bloque(hash_previo="1")
        hash_bloque = self.prueba_trabajo(bloque)
        self.integra_bloque(bloque, hash_bloque)

    def nuevo_bloque(self, hash_previo: str) -> Bloque:
        """
        Crea un nuevo bloque a partir de las transacciones que no están
        confirmadas
        :param hash_previo: el hash del bloque anterior de la cadena
        :return: el nuevo bloque
        """
        new_block = Bloque(
            indice=self.n_bloques + 1,
            transacciones=self.pool.copy(),
            timestamp=time(),
            hash_previo=hash_previo,
            prueba=0,
        )
        return new_block

    def nueva_transaccion(self, origen: str, destino: str, cantidad: int):
        """
        Crea una nueva transaccion a partir de un origen, un destino y una
        cantidad, y la incluye en el pool.
        :param origen: ip de origen de la transacción
        :param destino: ip de destino de la transacción
        :param cantidad: cantidad de la transacción
        :return: None
        """
        transaccion = {"origen": origen, "destino": destino, "cantidad": cantidad}
        self.pool.add(str(transaccion))

    def prueba_trabajo(self, bloque: Bloque) -> str:
        """
        Calcula el valor del parámetro prueba que hace que el hash del bloque
        comience con tantos ceros como la dificultad establecida.
        :param bloque: bloque del que calcular el hash
        :return: el hash del bloque con la prueba encontrada
        """
        new_hash = "0" * (self.dificultad - 1) + "1"

        while new_hash[: self.dificultad] != "0" * self.dificultad:
            bloque.prueba += 1
            new_hash = bloque.calcular_hash()

        return new_hash

    def prueba_valida(self, bloque: Bloque, hash_bloque: str) -> bool:
        """
        Método que comprueba si el hash del bloque comienza con tantos ceros como
        la dificultad establecida y que su hash realmente coincide con el calculado.
        :param bloque: bloque del que hacer la comprobación
        :param hash_bloque: hash asignado al bloque
        :return: False si no pasa cualquiera de las comprobaciones y verdadero en
        caso contrario
        """
        if hash_bloque[: self.dificultad] != "0" * self.dificultad:
            return False

        if bloque.calcular_hash() != hash_bloque:
            return False

        return True

    def integra_bloque(self, bloque_nuevo: Bloque, hash_prueba: str) -> bool:
        """
        Comprueba que el hash asignado al bloque es correcto, y si es así,
        lo integra en la cadena y actualiza la pool y el número de bloques.
        :param bloque_nuevo: bloque a integrar
        :param hash_prueba: hash asignado al bloque
        :return: False si no pasa cualquiera de las comprobaciones y True en
        caso contrario
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

    def check_chain(self) -> bool:
        """
        Comprueba que la cadena de bloques es válida, es decir, que sus hashes
        y sus hashes previos son correctos.
        :return: False si no pasa cualquiera de las comprobaciones y True en
        caso contrario
        """
        for i in range(len(self.chain) - 1):
            # Check Bloque
            if not self.prueba_valida(self.chain[i], self.chain[i].hash):
                return False
            # Check chain link
            if self.chain[i].hash != self.chain[i + 1].hash_previo:
                return False

        if not self.prueba_valida(self.chain[-1], self.chain[-1].hash):  # ERROR?
            return False

        return True

    def toDict(self) -> dict:
        """
        Convierte la cadena de bloques a un diccionario para poder guardarlo en
        un archivo JSON. Convierte cada bloque a un diccionario y la pool de
        transacciones a lista.
        :return: el diccionario correspondiente a la blockchain
        """
        d = {}
        d["chain"] = [b.toDict() for b in self.chain]
        d["dificultad"] = self.dificultad
        d["pool"] = list(self.pool)
        d["n_bloques"] = self.n_bloques

        return d

    def fromDict(self, d: dict):
        """
        Crea un blockchain a partir de un diccionario. Crea cada bloque a partir
        de su diccionario y la pool como un set a partir de la lista.
        :param d: diccionario correspondiente a la blockchain
        :return: la instancia de la clase blockchain
        """
        self.chain = [Bloque().fromDict(b) for b in d["chain"]]
        self.dificultad = d["dificultad"]
        self.pool = set(d["pool"])
        self.n_bloques = d["n_bloques"]

        return self

    def fromChain(self, chain: list):
        """
        Crea un blockchain a partir de una cadena de bloques. Crea cada bloque a
        partir de su diccionario e inicia el resto de variables vacias.
        Se usa para comprobar que la cadena de bloques es valida en BlochChain.py
        :param chain: lista de bloques
        :return: instancia de la clase blockchain
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
