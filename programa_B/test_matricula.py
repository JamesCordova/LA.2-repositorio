"""
Plantilla de pruebas - Programa B (motor de matricula y promedios).

Ejecute con:

    python3 -m pytest test_matricula.py -q

Recuerde: la ESPECIFICACION es el oraculo. No modifique matricula.py.
"""

from decimal import Decimal

import pytest

import matricula as mat


@pytest.fixture
def catalogo():
    """Catalogo de referencia de la seccion 3 de la especificacion."""
    cursos = [
        mat.Curso("IS101", "Algoritmica", 4, []),
        mat.Curso("IS201", "Estructuras de Datos", 4, ["IS101"]),
        mat.Curso("IS301", "Base de Datos", 3, ["IS201"]),
        mat.Curso("IS401", "Ingenieria de Software", 4, []),
        mat.Curso("IS402", "Pruebas de Software", 3, ["IS401"]),
        mat.Curso("IS403", "Redes", 3, []),
        mat.Curso("IS404", "Sistemas Operativos", 4, []),
        mat.Curso("IS405", "Compiladores", 4, []),
        mat.Curso("IS406", "Inteligencia Artificial", 3, []),
        mat.Curso("IS407", "Seminario de Tesis", 1, []),
    ]
    return {c.codigo: c for c in cursos}


def test_ejemplo_de_la_especificacion(catalogo):
    """Caso 5 de la tabla de ejemplos: (20*4 + 10*3) / 7 = 15.71."""
    promedio = mat.calcular_promedio_ponderado({"IS101": 20, "IS403": 10}, catalogo)
    assert promedio == Decimal("15.71")


# --- Escriba sus pruebas a partir de aqui ---------------------------------
