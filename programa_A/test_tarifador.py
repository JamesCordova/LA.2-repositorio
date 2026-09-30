"""
Plantilla de pruebas - Programa A (tarifador de estacionamiento).

Escriba aqui sus pruebas. Ejecute con:

    python3 -m pytest test_tarifador.py -q

Recuerde: la ESPECIFICACION es el oraculo. Si una prueba suya falla sobre el
código entregado, lo mas probable es que haya encontrado un defecto; pero
verifique primero que su valor esperado se deduzca de la especificación y no
del comportamiento observado en el código.

No modifique tarifador.py.
"""

from datetime import datetime
from decimal import Decimal

import pytest

import tarifador as taf


def test_ejemplo_de_la_especificacion():
    """Caso 2 de la tabla de ejemplos: 11 minutos diurnos = S/ 3.00."""
    total = taf.calcular_total(
        datetime(2026, 9, 21, 10, 0), datetime(2026, 9, 21, 10, 11), "ABC-123"
    )
    assert total == Decimal("3.00")


# --- Escriba sus pruebas a partir de aqui ---------------------------------
