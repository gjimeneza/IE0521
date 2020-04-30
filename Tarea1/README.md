# Branch Predictor

Programa en Python (Python 3) que simula varios predictores de saltos.
Los [saltos](https://drive.google.com/file/d/1SX7RqywL641EwW8miW6rta1quLPN07cZ/view "Ingresar para descargar el archivo con los saltos.") son el resultado de la ejecución de gcc (colección de compiladores de GNU), que es parte de la suite SPECint2000. 

Los predictores de saltos posibles por simular:
* Predictor bimodal
* Predictor con historia privada
* Predictor con historia global
* Predictor por torneo

## Requerimientos
* Ubuntu 18.04 en adelante
* Python 3.6 en adelante

## Uso

En un directorio con [branch_predictor.py](branch_predictor.py) y el archivo con los [saltos](https://drive.google.com/file/d/1SX7RqywL641EwW8miW6rta1quLPN07cZ/view "Ingresar para descargar el archivo con los saltos.")  se corre el siguiente comando:

```bash
gunzip -c branch-trace-gcc.trace.gz | python3 branch_predictor.py  -s < # > -bp < # > -gh < # > -ph < # > -o < # >
```
ó 

```bash
gunzip -c branch-trace-gcc.trace.gz | python branch_predictor.py  -s < # > -bp < # > -gh < # > -ph < # > -o < # >
```
Dependiendo del alias que le tenga a python3.

Si se quisiera sólo correr las primeras 200 entradas, por ejemplo:

```bash
gunzip -c branch-trace-gcc.trace.gz | head -200 | python3 branch_predictor.py  -s < # > -bp < # > -gh < # > -ph < # > -o < # >
```

En todos los casos cada argumento corresponde a:
* Tamaño de la tabla BTH (-s)
* Tipo de predicción (-bp)
   * 0: Bimodal
   * 1: Pshare
   * 2: Gshare
   * 3: Tournament
* Tamaño del registro de predicción global (-gh)
* Tamaño de los registros de historia privada (-ph)
* Salida de la simulación (-o)

   Si le pone el argumento 1, guarda un archivo con el nombre del predictor con las primeros 5000 predicciones.
