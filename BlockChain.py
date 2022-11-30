import json
import hashlib
from typing import List, Dict
from time import time


class Bloque:
    def __init__(self, indice: int, transacciones: List[Dict], timestamp: float, hash_previo: str, prueba: int =0):
        """
        Constructor de la clase `Bloque`.
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
        self.hash = ""

    def calcular_hash(self):
        """
        Metodo que devuelve el hash de un bloque
        """
        block_string = json.dumps(self.__dict__, sort_keys=True)
        return hashlib.sha256(block_string.encode()).hexdigest()
    
    def toDict(self):
        return self.__dict__



class Blockchain:
    def __init__(self):
        self.chain: List[Bloque] = []
        self.dificultad = 4
        self.pool = []
        self.n_bloques = 0

    def primer_bloque(self):
        """
        Crea el bloque inicial vacío, con tiempo 0 y hash previo de 1
        """
        primer = Bloque(
            indice = 0,
            timestamp = 0,
            hash_previo = 1,
        )
        return primer

    def nuevo_bloque(self, hash_previo: str) -> Bloque:
        """
        Crea un nuevo bloque a partir de las transacciones que no estan
        confirmadas
        :param prueba: el valor de prueba a insertar en el bloque
        :param hash_previo: el hash del bloque anterior de la cadena
        :return: el nuevo bloque
        """
        # Cambiar n_bloques o pool?
        new_block = Bloque(
            indice = self.n_bloques+1,
            transacciones = self.pool,
            timestamp = time(),
            hash_previo = hash_previo,
            prueba = 0
        )
        self.prueba_trabajo(new_block)

        return new_block

    def nueva_transaccion(self, origen: str, destino: str, cantidad: int) -> int:
        """
        Crea una nueva transaccion a partir de un origen, un destino y una
        cantidad y la incluye en las listas de transacciones.
        :param origen: <str> el que envia la transaccion
        :param destino: <str> el que recibe la transaccion
        :param cantidad: <int> la candidad
        """
        transaccion = {
            "origen": origen,
            "destino": destino,
            "cantidad": cantidad
        }
        self.pool.append(transaccion)
    
    def prueba_trabajo(self, bloque: Bloque) -> str:
        """
        Algoritmo simple de prueba de trabajo:
        - Calculara el hash del bloque hasta que encuentre un hash que empiece
        por tantos ceros como dificultad.
        - Cada vez que el bloque obtenga un hash que no sea adecuado,
        incrementara en uno el campo de ``prueba del bloque``
        :param bloque: objeto de tipo bloque
        :return: el hash del nuevo bloque (dejara el campo de hash del bloque sin
        modificar)
        """
        new_hash = "0"*(self.dificultad-1)+"1"

        while new_hash[:self.dificultad] != "0"*self.dificultad:
            bloque.prueba += 1
            new_hash = bloque.calcular_hash()

        return new_hash

    def prueba_valida(self, bloque: Bloque, hash_bloque: str) -> bool:
        """
        Metodo que comprueba si el hash_bloque comienza con tantos ceros como la
        dificultad estipulada en el blockchain.
        Ademas comprobara que hash_bloque coincide con el valor devuelvo del
        metodo de calcular hash del bloque.
        Si cualquiera de ambas comprobaciones es falsa, devolvera falso y en caso
        contrario, verdadero
        :param bloque:
        :param hash_bloque:
        :return:
        """
        if hash_bloque[:self.dificultad] != "0"*self.dificultad:
            return False

        if bloque.calcular_hash() != hash_bloque:
            return False

        return True       
    
    def integra_bloque(self, bloque_nuevo: Bloque, hash_prueba: str) -> bool:
        """
        Metodo para integran correctamente un bloque a la cadena de bloques.
        Debe comprobar que la prueba de hash es valida y que el hash del bloque
        ultimo de la cadena coincida con el hash_previo del bloque que se va a
        integrar. Si pasa las comprobaciones, actualiza el hash del bloque a
        integrar, lo inserta en la cadena y hace un reset de las transacciones
        no confirmadas (vuelve a dejar la lista de transacciones no confirmadas
        a una lista vacia)
        :param bloque_nuevo: el nuevo bloque que se va a integrar
        :param hash_prueba: la prueba de hash
        :return: True si se ha podido ejecutar bien y False en caso contrario (si
        no ha pasado alguna prueba)
        """
        if bloque_nuevo.hash_previo != self.chain[-1].hash:
            return False
        
        if not self.prueba_valida(bloque_nuevo, hash_prueba):
            return False

        bloque_nuevo.hash = hash_prueba
        self.chain.append(bloque_nuevo)
        self.pool = []

        return True
