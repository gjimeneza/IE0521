import getopt, sys
import datetime

# Valores globales a emplear en las funciones (Taken, Not taken)
T = True
N = False


class Bimodal:
    def __init__(self, s):
        """Constructor del predictor bimodal

        Parameters
        ----------
        s : int
            El exponente del tamaño del BHT (2^s)

        """

        self.s = s
        numero_entradas = pow(2, s)
        self.bht = [[N,N] for i in range(numero_entradas)]

    def prediccion(self, pc_actual, resultado_actual):
        """Función principal del predictor Pshare

        Predice un salto a partir de un BHT. Dependiendo del
        resultado de la predicción se actualiza el BHT.

        Parameters
        ----------
        pc_actual : int (bin)
            Ultimos s bits del pc_actual
        resultado_actual : bool
            Es True si el salto fue tomado, False en caso contrario.

        Returns
        ------
        prediccion: bool
            Es True si predijo un Taken, False si predijo un Not taken

        """

        contador_actual = self.bht[pc_actual]

        prediccion = contador_actual[0]

        # XOR con los valores booleanos del contador actual y el resultado del branch
        # Si el XOR es verdadero, la predicción es incorrecta
        if contador_actual[0] ^ resultado_actual:
            #print("Prediccion incorrecta")
            # Si el branch fue Taken el contador es [N, -]
            if resultado_actual:
                #Si el contador es [N,T]
                if contador_actual[1]:
                    # Pasa a [T,N]
                    contador_actual[0] = T
                    contador_actual[1] = N
                #Si el contador es [N,N] 
                else:
                    # Pasa a [N,T]
                    contador_actual[1] = T
            # Si el branch fue Not taken el contador es [T, -]
            else:
                #Si el contador es [T,T]
                if contador_actual[1]:
                    # Pasa a [T,N]
                    contador_actual[1] = N
                #Si el contador es [T,N] 
                else:
                    #Pasa a [N,T] 
                    contador_actual[0] = N
                    contador_actual[1] = T

        # Si la predicción fue correcta
        else:
            #print("Prediccion correcta")
             # Si el branch fue Taken el contador es [T, -]
            if resultado_actual:
                #Si el contador es [T,N]
                if not contador_actual[1]:
                    # Pasa a [T,T]
                    contador_actual[1] = T
            # Si el branch fue Not taken el contador es [N, -]
            else:
                #Si el contador es [N,T]
                if contador_actual[1]:
                    # Pasa a [N,N]
                    contador_actual[1] = N
        
        return prediccion

class Pshare:
    def __init__(self, s, ph):
        """Constructor del predictor privado

        Parameters
        ----------
        s : int
            El exponente del tamaño del BHT (2^s)
        ph : int
            Tamaño de los registros del PHT
        
        """
        self.s = s
        self.ph = ph
        numero_entradas = pow(2, s)
        # Se define el PHT y el BHT para el predictor privado
        self.pht = [0 for i in range(numero_entradas)]
        self.bht = [[N,N] for i in range(numero_entradas)]

        # Se crea una máscara de n o s cantidad de unos
        self.n_mask = "0b"
        for i in range(s):
            self.n_mask+="1"

        # Se crea una máscara de ph cantidad de unos
        self.ph_mask = "0b"
        for i in range(ph):
            self.ph_mask+="1"

    def prediccion(self, pc_actual, resultado_actual):
        """Función principal del predictor Pshare

        Predice un salto a partir de un BHT el cual es indexado
        a partir un XOR con el PC y un registro del PHT. Donde el 
        PHT es indexado por el PC.

        Parameters
        ----------
        pc_actual : int (bin)
            Ultimos s bits del pc_actual
        resultado_actual : bool
            Es True si el salto fue tomado, False en caso contrario.

        Returns
        ------
        prediccion: bool
            Es True si predijo un Taken, False si predijo un Not taken

        """

        self.pht[pc_actual] = self.pht[pc_actual] & int(self.ph_mask, 2)

        # Se aplica el XOR del PC con el registro de historia
        xor = pc_actual ^ self.pht[pc_actual]

        # Se toman los ultimos n bits
        xor = xor & int(self.n_mask,2)

        index_bht_actual = xor
        
        contador_actual = self.bht[index_bht_actual]
        
        prediccion = contador_actual[0]

        # XOR con los valores booleanos del contador actual y el resultado del branch
        # Si el XOR es verdadero, la predicción es incorrecta
        if contador_actual[0] ^ resultado_actual:
            #print("Prediccion incorrecta " + contadores_toString(self.bht))
            # Si el branch fue Taken el contador es [N, -]
            if resultado_actual:
                # Como fue Taken se actualiza el registro de historia  
                self.pht[pc_actual] = self.pht[pc_actual] << 1
                self.pht[pc_actual] += 1
                #Si el contador es [N,T]
                if contador_actual[1]:
                    # Pasa a [T,N]
                    contador_actual[0] = T
                    contador_actual[1] = N
                #Si el contador es [N,N] 
                else:
                    # Pasa a [N,T]
                    contador_actual[1] = T
            # Si el branch fue Not taken el contador es [T, -]
            else:
                # Como fue Not taken se actualiza el registro de historia  
                self.pht[pc_actual] = self.pht[pc_actual] << 1
                #Si el contador es [T,T]
                if contador_actual[1]:
                    # Pasa a [T,N]
                    contador_actual[1] = N
                #Si el contador es [T,N] 
                else:
                    #Pasa a [N,T] 
                    contador_actual[0] = N
                    contador_actual[1] = T

        # Si la predicción fue correcta
        else:
            #print("Prediccion correcta " + contadores_toString(self.bht))
            # Si el branch fue Taken el contador es [T, -]
            if resultado_actual:
                # Como fue Taken se actualiza el registro de historia  
                self.pht[pc_actual] = self.pht[pc_actual] << 1
                self.pht[pc_actual] += 1
                #Si el contador es [T,N]
                if not contador_actual[1]:
                    # Pasa a [T,T]
                    contador_actual[1] = T
            # Si el branch fue Not taken el contador es [N, -]
            else:
                # Como fue Not taken se actualiza el registro de historia  
                self.pht[pc_actual] = self.pht[pc_actual] << 1
                #Si el contador es [N,T]
                if contador_actual[1]:
                    # Pasa a [N,N]
                    contador_actual[1] = N
        return prediccion

class Gshare:
    def __init__(self, s, gh):
        """Constructor del predictor global

        Parameters
        ----------
        s : int
            El exponente del tamaño del BHT (2^s)
        gh : int
            Tamaño del registro global
        
        """

        self.s = s
        self.gh = gh
        numero_entradas = pow(2, s)
        # Se define el registro de historia y el BHT para el predictor global
        self.registro_historia = 0
        self.bht = [[N,N] for i in range(numero_entradas)]

        # Se crea una máscara de n o s cantidad de unos
        self.n_mask = "0b"
        for i in range(s):
            self.n_mask+="1"

        # Se crea una máscara de gh cantidad de unos
        self.gh_mask = "0b"
        for i in range(gh):
            self.gh_mask+="1"

    def prediccion(self, pc_actual, resultado_actual):
        """Función principal del predictor Gshare

        Predice un salto a partir de un BHT el cual es indexado
        a partir un XOR con el PC y un registro global

        Parameters
        ----------
        pc_actual : int (bin)
            Ultimos s bits del pc_actual
        resultado_actual : bool
            Es True si el salto fue tomado, False en caso contrario.

        Returns
        ------
        prediccion: bool
            Es True si predijo un Taken, False si predijo un Not taken

        """

        self.registro_historia = self.registro_historia & int(self.gh_mask, 2)

        # Se aplica el XOR del PC con el registro de historia
        xor = pc_actual ^ self.registro_historia

        # Se toman los ultimos n bits
        xor = xor & int(self.n_mask,2)

        index_bht_actual = xor
        
        contador_actual = self.bht[index_bht_actual]
        
        prediccion = contador_actual[0]

        # XOR con los valores booleanos del contador actual y el resultado del branch
        # Si el XOR es verdadero, la predicción es incorrecta
        if contador_actual[0] ^ resultado_actual:
            #print("Prediccion incorrecta " + contadores_toString(contadores))
            # Si el branch fue Taken el contador es [N, -]
            if resultado_actual:
                # Como fue Taken se actualiza el registro de historia  
                self.registro_historia = self.registro_historia << 1
                self.registro_historia += 1
                #Si el contador es [N,T]
                if contador_actual[1]:
                    # Pasa a [T,N]
                    contador_actual[0] = T
                    contador_actual[1] = N
                #Si el contador es [N,N] 
                else:
                    # Pasa a [N,T]
                    contador_actual[1] = T
            # Si el branch fue Not taken el contador es [T, -]
            else:
                # Como fue Not taken se actualiza el registro de historia  
                self.registro_historia = self.registro_historia << 1
                #Si el contador es [T,T]
                if contador_actual[1]:
                    # Pasa a [T,N]
                    contador_actual[1] = N
                #Si el contador es [T,N] 
                else:
                    #Pasa a [N,T] 
                    contador_actual[0] = N
                    contador_actual[1] = T

        # Si la predicción fue correcta
        else:
            #print("Prediccion correcta " + contadores_toString(contadores))
             # Si el branch fue Taken el contador es [T, -]
            if resultado_actual:
                # Como fue Taken se actualiza el registro de historia  
                self.registro_historia = self.registro_historia << 1
                self.registro_historia += 1
                #Si el contador es [T,N]
                if not contador_actual[1]:
                    # Pasa a [T,T]
                    contador_actual[1] = T
            # Si el branch fue Not taken el contador es [N, -]
            else:
                # Como fue Not taken se actualiza el registro de historia  
                self.registro_historia = self.registro_historia << 1
                #Si el contador es [N,T]
                if contador_actual[1]:
                    # Pasa a [N,N]
                    contador_actual[1] = N

        return prediccion

class Torneo:
    def __init__(self, s, gh, ph):
        """Constructor del predictor por torneo

        Parameters
        ----------
        s : int
            El exponente del tamaño del BHT (2^s)
        gh : int
            Tamaño del registro global del predictor global
        ph : int
            Tamaño de los registros del PHT del predictor privado
        
        """

        numero_entradas = pow(2, s)
        # El metapredictor comienza con todos sus valores en strongly prefer pshared
        # Se codifica [N, N] como strongly prefer pshared
        # Se codifica [N, T] como weakly prefer pshared
        # Se codifica [T, N] como weakly prefer gshared
        # Se codifica [T, T] como strongly prefer gshared
        self.metapredictor = [[N,N] for i in range(numero_entradas)]

        self.predictor_privado = Pshare(s, ph) 
        self.predictor_global = Gshare(s, gh) 

    def prediccion(self, pc_actual, resultado_actual):
        """Función principal del predictor por Torneo

        Emplea un predictor Pshare y Gshare para predecir un salto. Dependiendo 
        si las predicciones de estos son correctos actualiza un metapredictor (como
        BHT pero de predictores). La elección del predictor es hecha dependiendo de
        los valores en el metapredictor.

        Parameters
        ----------
        pc_actual : int (bin)
            Ultimos s bits del pc_actual
        resultado_actual : bool
            Es True si el salto fue tomado, False en caso contrario.

        Returns
        ------
        prediccion: bool
            Es True si predijo un Taken, False si predijo un Not taken

        """

        # El contador a emplear se toma del valor del pc actual
        contador_actual = self.metapredictor[pc_actual]

        # La predicción del Pshare
        prediccion_pshare = self.predictor_privado.prediccion(pc_actual, resultado_actual)

        # La predicción del Gshare
        prediccion_gshare = self.predictor_global.prediccion(pc_actual, resultado_actual)

        # Valores que tienen True si sus respectivas predicciones fueron correctas
        pshare_correcto = not (prediccion_pshare ^ resultado_actual)
        gshare_correcto = not (prediccion_gshare ^ resultado_actual)

        prediccion = contador_actual[0]

        if contador_actual[0] == N:
            prediccion = prediccion_pshare
            #print("Pshare es: " + str(pshare_correcto))
        else:
            prediccion = prediccion_gshare
            #print("Gshare es: " + str(gshare_correcto))

        # Solo sí un predictor es correcto y el otro no, se modifica el metapredictor
        difieren = pshare_correcto ^ gshare_correcto

        # Si difieren se actualiza el metapredictor
        if difieren:
            if gshare_correcto:
                # Si era strongly prefer pshared, pasa a weakly prefer pshared
                if contador_actual[0] == N and contador_actual[1] == N:
                    contador_actual[1] = T
                # Si era weakly prefer pshared, pasa a weakly prefer gshared
                elif contador_actual[0] == N and contador_actual[1] == T:
                    contador_actual[0] = T
                    contador_actual[1] = N
                # Si era weakly prefer gshared, pasa a strongly prefer gshared
                elif contador_actual[0] == T and contador_actual[1] == N:
                    contador_actual[1] = T
            # pshared era correcto, puesto que difieren
            else:
                # Si era strongly prefer gshared, pasa a weakly prefer gshared
                if contador_actual[0] == T and contador_actual[1] == T:
                    contador_actual[1] = N
                # Si era weakly prefer Gshared, pasa a weakly prefer Pshared
                elif contador_actual[0] == T and contador_actual[1] == N:
                    contador_actual[0] = N
                    contador_actual[1] = T
                # Si era weakly prefer pshared, pasa a strongly prefer pshared
                elif contador_actual[0] == N and contador_actual[1] == T:
                    contador_actual[1] = N

        return prediccion


def procesador_traces(s):
    """Función que procesa el archivo con los traces

    Lee el archivo que recibe en el standard input y separa tanto los valores
    de los PCs como los resultados en listas.

    Parameters
    ----------
    s : int
        El exponente del tamaño del BHT (2^s)

    Returns
    ------
    pcs : lista de ints (bin)
        Cada entrada tiene los ultimos s bits de los PCs
    resultados : lista de bools
        Son True si el salto fue tomado y False en caso contrario
    pcs_completos : lista de ints (bin)
        Cada entrada tiene todos los bits de los PCs

    """
    
    # Lee el standard input que corresponde a los traces del archivo
    raw_traces = sys.stdin.read()
    x = raw_traces.split("\n")

    pcs = []
    pcs_completos = []
    resultados = []

    # Separa el PC y el resultado del branch en dos listas separadas
    for i in range(len(x) - 1):
        trace = x[i]
        pc = trace.split(" ")[0]
        resultado = trace.split(" ")[1]

        pc = bin(int(pc))
        pcs_completos.append(pc)

        pc = pc[len(pc) - s:]
        pc = int(pc, 2)

        if resultado == 'T':
            resultado = T
        else:
            resultado = N

        pcs.append(pc)
        resultados.append(resultado)
    return pcs, resultados, pcs_completos

def procesador_argumentos():
    """Función que procesa los argumentos pasados en la terminal

    Utiliza la biblioteca getopt para procesar los argumentos.
    Esta biblioteca casi que automatiza el proceso. Solo hay que indicarle
    los argumentos a emplear tanto en su forma corta como la larga y donde guardar
    cada valor.

    Returns
    ------
    valores_de_argumentos : lista de strings
        Posee los valores de los argumentos: -s, -bp, -ph, -gh, -o

    """

    # Obtiene todos los argumentos de la línea de comandos
    full_cmd_arguments = sys.argv

    # Mantiene todos excepto el primero (nombre del archivo)
    argument_list = full_cmd_arguments[1:]

    # getopt no acepta argumentos cortos de mas de una letra, hay que improvisar
    if "-bp" in argument_list:
        argument_list[argument_list.index("-bp")] = "-b"
    if "-gh" in argument_list:
        argument_list[argument_list.index("-gh")] = "-g"
    if "-ph" in argument_list:
        argument_list[argument_list.index("-ph")] = "-p"

    short_options = "s:b:g:p:o:"
    long_options = ["size=", "branchpredictor=", "globalhistory=", "privatehistory=", "output="]

    try:
        arguments, values = getopt.getopt(argument_list, short_options, long_options)
    except getopt.error as err:
        # Error de agumentos
        print (str(err))
        sys.exit(2)

    # Valores iniciales de los argumentos
    s = 0
    bp = 0
    gh = 0
    ph = 0
    o = 0

    # Evaluate given options
    for current_argument, current_value in arguments:
        if current_argument in ("-s", "--size"):
            s = current_value
        elif current_argument in ("-b", "--branchpredictor"):
            bp = current_value
        elif current_argument in ("-g", "--globalhistory"):
            gh = current_value
        elif current_argument in ("-p", "--privatehistory"):
            ph = current_value
        elif current_argument in ("-o", "--output"):
            o = current_value
        

    valores_argumentos = [s, bp, gh, ph, o]

    return valores_argumentos

def predictor(s, bp, gh, ph, pcs, resultados):
    """Predictor genérico

    Esta función detecta cual predictor usar (-bp) y construye el predictor respectivo.
    Luego recorre los valores de PCs y los resultados, empleando el predictor escogido.
    Cuando termina de recorrer llama la función a imprimir en pantalla y finalmente
    devuelve una lista con todas las predicciones en orden junto a una lista con los valores
    booleanos si lo tuvo correcto o no.

    Parameters
    ----------
    s : int
        El exponente del tamaño del BHT (2^s)
    bp : int
        Determina el predictor a usar
    gh : int
        Tamaño del registro global del predictor global
    ph : int
        Tamaño de los registros del PHT del predictor privado
    pcs : lista de ints (bin)
        Contiene los ultimos s bits de los valores de los PCs
    resultados : lista de bools
        Son True si el salto fue tomado, False si no

    Returns
    ------
    predicciones : lista de bools
        Contiene las predicciones realizadas por el predictor en orden
    correctos : lista de bools
        Las entradas son True si la prediccion fue correcta, False en caso contrario

    """

    predicciones = []
    correctos = []

    taken_correctos = 0
    taken_incorrectos = 0
    not_taken_correctos = 0
    not_taken_incorrectos = 0

     # Elige el predictor dado por el argumento -bp
    if bp == 0:
        predictor = Bimodal(s)
    elif bp == 1:
        predictor = Pshare(s, ph)
    elif bp == 2:
        predictor = Gshare(s, gh)
    elif bp == 3:
        predictor = Torneo(s, gh, ph)
    else:
        print("Eliga un valor entre 0 y 3.")
        return predicciones, correctos

    for i in range(len(pcs)):
        pc_actual = pcs[i]
        resultado_actual = resultados[i]

        # Prediccion realizada por el predictor elegido
        prediccion = predictor.prediccion(pc_actual, resultado_actual)

        # Es True si la prediccion concuerda al resultado actual, False en caso contrario
        es_correcto = not (prediccion ^ resultado_actual)
        
        # Por si se eligió guardar en un archivo
        if i < 5000:
            predicciones.append(prediccion)
            correctos.append(es_correcto)

        # Suma a los contadores si se tuvo el taken correcto o incorrecto al igual que a los not takens
        if resultado_actual == T:
            if es_correcto:
                taken_correctos += 1
            else:
                taken_incorrectos += 1
        else:
            if es_correcto:
                not_taken_correctos += 1
            else:
                not_taken_incorrectos += 1

    imprimir_informacion(s, bp, gh, ph, len(pcs), taken_correctos, taken_incorrectos, not_taken_correctos, not_taken_incorrectos)
    
    return predicciones, correctos

def guardar_archivo(bp, pcs, resultados, predicciones, correctos):
    """Guarda en un archivo

    Guarda en un archivo con nombre del predictor, los valores de los PCs, el resultado del salto,
    el de la predicción y si fue correcto o incorrecto. El formato es el siguiente:

    PC			Outcome	Prediction	Correct/Incorrect
    3086629576	T		N			Incorrect
    3086629604	T		N			Incorrect
    3086629599	N		N			Correct
    3086629604	T		N			Incorrect

    Parameters
    ----------
    bp : int
        Determina el predictor usado
    pcs : lista de ints (bin)
        Contiene todos los bits de los valores de los PCs
    resultados : lista de bools
        Son True si el salto fue tomado, False si no

    Returns
    ------
    predicciones : lista de bools
        Contiene las predicciones realizadas por el predictor en orden
    correctos : lista de bools
        Las entradas son True si la prediccion fue correcta, False en caso contrario
    predicciones : lista de bools
        Contiene las predicciones realizadas por el predictor en orden
    correctos : lista de bools
        Las entradas son True si la prediccion fue correcta, False en caso contrario

    """
    
    datos = "PC\t\t\tOutcome\tPrediction\tCorrect/Incorrect\n"

    if bp == 0:
        tipo = "Bimodal"
    elif bp == 1:
        tipo = "Pshare"
    elif bp == 2:
        tipo = "Gshare"
    elif bp == 3:
        tipo = "Tournament"
    else:
        return
    
    with open(tipo + ".txt", 'w') as file:
            file.write(datos)
            for i in range(len(predicciones)):
                if resultados[i]:
                    resultado = "T"
                else:
                    resultado = "N"

                if predicciones[i]:
                    prediccion = "T"
                else:
                    prediccion = "N"
                
                if correctos[i]:
                    correcto = "Correct"
                else:
                    correcto = "Incorrect"

                file.write(str(int(pcs[i], 2)) + "\t" + resultado + "\t\t" + prediccion + "\t\t\t" + correcto +"\n")

def imprimir_informacion(s, bp, gh, ph, num_branches, taken_correctos, taken_incorrectos, not_taken_correctos, not_taken_incorrectos):
    """Imprime en pantalla

    Imprime en pantalla datos pertinentes a la simulación ejecutada.

    Parameters
    ----------
    s : int
        El exponente del tamaño del BHT (2^s)
    bp : int
        Determina el predictor a usar
    gh : int
        Tamaño del registro global del predictor global
    ph : int
        Tamaño de los registros del PHT del predictor privado
    num_branches : int
        Contiene la cantidad de saltos totales
    taken_correctos : int
        Contiene la cantidad de saltos tomados predecidos correctamente
    taken_incorrectos : int
        Contiene la cantidad de saltos tomados predecidos incorrectamente
    not_taken_correctos : int
        Contiene la cantidad de saltos no tomados predecidos correctamente
    not_taken_incorrectos : int
        Contiene la cantidad de saltos no tomados predecidos incorrectamente

    """

    if bp == 0:
        tipo = "Bimodal"
    elif bp == 1:
        tipo = "Pshare"
    elif bp == 2:
        tipo = "Gshare"
    elif bp == 3:
        tipo = "Tournament"
    else:
        return

    informacion = """    ---------------------------------------------------------------------
    Prediction parameters
    ---------------------------------------------------------------------
    Branch prediction type:\t\t\t\t""" + tipo + """
    BHT size (entries):\t\t\t\t\t""" + str(pow(2, s)) + """
    Global history register size:\t\t\t""" + str(gh) + """
    Private history register size:\t\t\t""" + str(gh) + """
    ---------------------------------------------------------------------
    Simulation results:
    ---------------------------------------------------------------------
    Number of branches:\t\t\t\t\t""" + str(num_branches) + """
    Correct prediction of taken branches:\t\t""" + str(taken_correctos) + """
    Incorrect prediction of taken branches:\t\t""" + str(taken_incorrectos) + """
    Correct prediction of not taken branches:\t\t""" + str(not_taken_correctos) + """
    Inorrect prediction of not taken branches:\t\t""" + str(not_taken_incorrectos) + """
    Percentage of correct predictions\t\t\t""" + str(((taken_correctos + not_taken_correctos)/num_branches)*100) + "%" + """
    ---------------------------------------------------------------------"""

    print(informacion)


def main():
    """Función principal del programa

    Llama todos las funciones pertinentes a los predictores.
    Decide si guardar el archivo o no a partir del argumento -o

    Si se quiere revisar los tiempos, se pueden descomentar las líneas 
    predecidas por "PROBAR TIEMPOS".

    """

    # PROBAR TIEMPOS
    #a = datetime.datetime.now()

    valores_argumentos = procesador_argumentos()
    
    # Valores de los argumentos
    s = int(valores_argumentos[0])
    bp = int(valores_argumentos[1])
    gh = int(valores_argumentos[2])
    ph = int(valores_argumentos[3])
    o = int(valores_argumentos[4])
    
    # Se extrae los valores de los PCs y los resultados del archivo
    pcs, resultados, pcs_completos = procesador_traces(s)
    
    predicciones, correctos = predictor(s, bp, gh, ph, pcs, resultados)

    # Se guarda el archivo si el argumento -o es 1
    if o == 1:
        guardar_archivo(bp, pcs_completos, resultados, predicciones, correctos)

    
    # PROBAR TIEMPOS
    #b = datetime.datetime.now()
    #c = b - a

    # Se probaron varias pruebas incluyendo las adjuntas en el enunciado de la tarea,
    # el tiempo maximo en mí máquina (Ryzen 1600X + 16 GB RAM) fue de la simulacion 
    # del predictor por torneo que ronda los 80 s.
    # print("El tiempo total de ejecución fue de: " + str(c.seconds) + " segundos.")


if __name__ == "__main__":
    main()