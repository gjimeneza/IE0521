# Branch Predictor

Programa en Python (Python 3) que simula varios predictores de saltos.
Los [saltos](https://drive.google.com/file/d/1SX7RqywL641EwW8miW6rta1quLPN07cZ/view "Ingresar para descargar el archivo con los saltos.") son el resultado de la ejecución de gcc (colección de compiladores de GNU), que es parte de la suite SPECint2000. 

Los predictores de saltos posibles por simular:
* Predictor bimodal
* Predictor con historia privada
* Predictor con historia global
* Predictor por torneo

## Usage

En un directorio con [branch_predictor.py](branch_predictor.py) se corre el siguiente comando:

```bash
gunzip -c branch-trace-gcc.trace.gz | python3 branch_predictor.py  -s < # > -bp < # > -gh < # > -ph < # > -o < # >
```
