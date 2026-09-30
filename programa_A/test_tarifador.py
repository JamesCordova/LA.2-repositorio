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

# Casos de prueba derivados

def test_10_minutos_de_gracia_son_gratis():
    """CP01 - Limite R1 (10 min exactos)"""
    recibo = taf.calcular_tarifa(
        datetime(2026, 9, 21, 10, 0), datetime(2026, 9, 21, 10, 10),
        "ABC-123", "NINGUNO ",
    )
    assert recibo.total == Decimal("0.00")
    assert recibo.minutos_facturables == 0

def test_11_minutos_cobran_una_fraccion():
    """CP02 - Limite R1 (11 min)."""
    recibo = taf.calcular_tarifa(
        datetime(2026, 9, 21, 10, 0), datetime(2026, 9, 21, 10, 11),
        "ABC-123", "NINGUNO",
    )
    assert recibo.total == Decimal("3.00")
    assert recibo.minutos_facturables == 15


def test_15_minutos_equivalen_a_una_fraccion():
    """CP03 - Limite R2 (15 min exactos)"""
    recibo = taf.calcular_tarifa(
        datetime(2026, 9, 21, 10, 0), datetime(2026, 9, 21, 10, 15),
        "ABC-123", "NINGUNO",
    )
    assert recibo.total == Decimal("3.00")
    assert recibo.minutos_facturables == 15

def test_16_minutos_cobran_dos_fracciones():
    """CP04 - Limite R2 (16 min, redondeo arriba)."""
    recibo = taf.calcular_tarifa(
        datetime(2026, 9, 21, 10, 0), datetime(2026, 9, 21, 10, 16),
        "ABC-123", "NINGUNO",
    )
    assert recibo.total ==Decimal("6.00")
    assert recibo.minutos_facturables == 30


def test_ingreso_a_las_08_00_aplica_tarifa_diurna():
    """CP05 - Limite R3 (inicio exacto 08:00)"""
    recibo = taf.calcular_tarifa(
        datetime(2026, 9, 21, 8, 0), datetime(2026, 9, 21, 8, 15),
        "ABC-123", "NINGUNO",
    )
    assert recibo.fracciones_diurnas == 1
    assert recibo.total == Decimal("3.00")

def test_ingreso_a_las_20_00_aplica_tarifa_nocturna():
    """CP06"""
    recibo = taf.calcular_tarifa(
        datetime(2026, 9, 21, 20, 0), datetime(2026, 9, 21, 20, 15),
        "ABC-123", "NINGUNO",
    )
    assert recibo.fracciones_nocturnas ==1
    assert recibo.total == Decimal("2.50")


def test_ingreso_a_las_19_45_combina_ambas_tarifas():
    """CP07"""
    recibo = taf.calcular_tarifa(
        datetime(2026, 9, 21, 19, 45), datetime(2026, 9, 21, 20, 15),
        "ABC-123", "NINGUNO",
    )
    assert recibo.fracciones_diurnas == 1
    assert recibo.fracciones_nocturnas == 1
    assert recibo.total == Decimal("5.50")


def test_estadia_prolongada_no_supera_los_45_soles():
    """CP08"""
    recibo = taf.calcular_tarifa(
        datetime(2026, 9, 21, 8, 0), datetime(2026, 9, 21, 12, 0),
        "ABC-123", "NINGUNO",
    )
    assert recibo.subtotal== Decimal("45.00")
    assert recibo.total == Decimal("45.00")





