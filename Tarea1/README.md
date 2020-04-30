# Branch Predictor

Programa en Python (Python 3) que simula varios predictores de saltos.
Los [saltos](https://www.google.com "Ingresar para descargar el archivo con los saltos.") son el resultado de la ejecución de gcc (colección de compiladores de GNU), que es parte de la suite SPECint2000. 

Los predictores de saltos posibles por simular:
* Predictor bimodal
* Predictor con historia privada
* Predictor con historia global
* Predictor por torneo

## Installation

Use the package manager [pip](https://pip.pypa.io/en/stable/) to install foobar.

```bash
pip install foobar
```

## Usage

```python
import foobar

foobar.pluralize('word') # returns 'words'
foobar.pluralize('goose') # returns 'geese'
foobar.singularize('phenomena') # returns 'phenomenon'
