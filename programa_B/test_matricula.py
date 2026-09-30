"""
Plantilla de pruebas - Programa B (motor de matricula y promedios).

Ejecute con:

    python3 -m pytest test_matricula.py -q

Recuerde: la ESPECIFICACION es el oraculo. No modifique matricula.py.
"""

from decimal import Decimal
from typing import NamedTuple

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
# Estructuras auxiliares para datos de prueba
class Curso(NamedTuple):
    codigo: str
    nombre: str
    creditos: int
    prerrequisitos: list[str]


class RegistroHistorial(NamedTuple):
    codigo: str
    nota: int
    intentos: int


@pytest.fixture
def catalogo_base():
    """Catálogo de cursos de prueba con distintas cargas de créditos."""
    return {
        "IS101": Curso("IS101", "Introducción a la Programación", 4, []),
        "IS201": Curso("IS201", "Estructuras de Datos", 4, ["IS101"]),
        "IS301": Curso("IS301", "Bases de Datos", 4, []),
        "IS401": Curso("IS401", "Ingeniería de Software I", 4, []),
        "IS402": Curso("IS402", "Ingeniería de Software II", 4, []),
        "IS403": Curso("IS403", "Redes y Comunicaciones", 3, []),
        "IS404": Curso("IS404", "Sistemas Operativos", 3, []),
        "IS405": Curso("IS405", "Arquitectura de Software", 3, []),
        "IS406": Curso("IS406", "Inteligencia Artificial", 3, []),
        "IS407": Curso("IS407", "Seguridad Informática", 3, []),
    }


# ==============================================================================
# REGLA R1: Redondeo de Nota Final
# ==============================================================================


def test_r1_calcular_nota_final_promedio_estandar():
    # R1: Calcula la nota final con promedio ponderado estándar
    evaluaciones = [(10, 1), (12, 1)]
    assert mat.calcular_nota_final(evaluaciones) == 11


def test_r1_calcular_nota_final_redondeo_hacia_abajo():
    # R1: Redondeo con punto decimal menor a 0.5 (10.4 redondea a 10)
    evaluaciones = [(10.4, 1)]
    assert mat.calcular_nota_final(evaluaciones) == 10


def test_r1_calcular_nota_final_redondeo_medio_hacia_arriba():
    # R1: Redondeo exacto en 0.5 hacia arriba (10.5 redondea a 11)
    evaluaciones = [(10.5, 1)]
    assert mat.calcular_nota_final(evaluaciones) == 11


def test_r1_calcular_nota_final_redondeo_hacia_arriba():
    # R1: Redondeo con punto decimal mayor a 0.5 (10.6 redondea a 11)
    evaluaciones = [(10.6, 1)]
    assert mat.calcular_nota_final(evaluaciones) == 11


def test_r1_calcular_nota_final_lista_vacia_lanza_excepcion():
    # R1: Lista de evaluaciones vacía debe lanzar SinCreditosError
    with pytest.raises(mat.SinCreditosError):
        mat.calcular_nota_final([])


def test_r1_calcular_nota_final_suma_pesos_cero_lanza_excepcion():
    # R1: Suma de pesos igual a 0 debe lanzar SinCreditosError
    evaluaciones = [(15, 0)]
    with pytest.raises(mat.SinCreditosError):
        mat.calcular_nota_final(evaluaciones)


# ==============================================================================
# REGLA R2: Criterio de Aprobación de Curso
# ==============================================================================


def test_r2_esta_aprobado_nota_10_devuelve_falso():
    # R2: Nota menor a 11 (10) considera el curso desaprobado
    assert mat.esta_aprobado(10) is False


def test_r2_esta_aprobado_nota_11_devuelve_verdadero():
    # R2: Nota exactamente 11 aprueba el curso
    assert mat.esta_aprobado(11) is True


def test_r2_esta_aprobado_nota_12_devuelve_verdadero():
    # R2: Nota mayor a 11 (12) aprueba el curso
    assert mat.esta_aprobado(12) is True


# ==============================================================================
# REGLA R3: Promedio Ponderado
# ==============================================================================


def test_r3_calcular_promedio_ponderado_exacto(catalogo_base):
    # R3: Promedio ponderado exacto a 2 decimales
    notas = {"IS101": 15, "IS401": 15}
    resultado = mat.calcular_promedio_ponderado(notas, catalogo_base)
    assert resultado == Decimal("15.00")


def test_r3_calcular_promedio_ponderado_redondeo_hacia_abajo(catalogo_base):
    # R3: Promedio 74/7 (~10.5714) redondea a 10.57
    notas = {"IS101": 10, "IS403": 11}
    resultado = mat.calcular_promedio_ponderado(notas, catalogo_base)
    assert resultado == Decimal("10.57")


def test_r3_calcular_promedio_ponderado_redondeo_medio_hacia_arriba(
    catalogo_base,
):
    # R3: Promedio 110/7 (~15.7142 -> prueba punto de redondeo a 15.71)
    notas = {"IS101": 20, "IS403": 10}
    resultado = mat.calcular_promedio_ponderado(notas, catalogo_base)
    assert resultado == Decimal("15.71")


def test_r3_calcular_promedio_ponderado_redondeo_hacia_arriba(catalogo_base):
    # R3: Promedio 76/7 (~10.8571) redondea a 10.86
    notas = {"IS101": 10, "IS403": 12}
    resultado = mat.calcular_promedio_ponderado(notas, catalogo_base)
    assert resultado == Decimal("10.86")


def test_r3_calcular_promedio_ponderado_sin_creditos_lanza_excepcion(
    catalogo_base,
):
    # R3: Diccionario de notas vacío equivale a 0 créditos e lanza SinCreditosError
    with pytest.raises(mat.SinCreditosError):
        mat.calcular_promedio_ponderado({}, catalogo_base)


# ==============================================================================
# REGLA R4: Determinar Estado del Semestre
# ==============================================================================


def test_r4_determinar_estado_tres_o_mas_desaprobados_es_desaprobado():
    # R4: Con 3 o más cursos desaprobados el estado es DESAPROBADO
    assert (
        mat.determinar_estado(Decimal("15.00"), desaprobados=3) == "DESAPROBADO"
    )


def test_r4_determinar_estado_promedio_menor_a_diez_es_desaprobado():
    # R4: Con promedio menor a 10.00 (9.99) el estado es DESAPROBADO
    assert (
        mat.determinar_estado(Decimal("9.99"), desaprobados=0) == "DESAPROBADO"
    )


def test_r4_determinar_estado_limite_inferior_observado():
    # R4: Con promedio 10.00 y 0 desaprobados el estado es OBSERVADO
    assert mat.determinar_estado(Decimal("10.00"), desaprobados=0) == "OBSERVADO"


def test_r4_determinar_estado_limite_superior_observado_por_promedio():
    # R4: Con promedio 10.99 y 0 desaprobados el estado es OBSERVADO
    assert mat.determinar_estado(Decimal("10.99"), desaprobados=0) == "OBSERVADO"


def test_r4_determinar_estado_observado_un_desaprobado():
    # R4: Con promedio >= 11.00 y 1 desaprobado el estado es OBSERVADO
    assert mat.determinar_estado(Decimal("11.00"), desaprobados=1) == "OBSERVADO"


def test_r4_determinar_estado_observado_dos_desaprobados():
    # R4: Con promedio >= 11.00 y 2 desaprobados el estado es OBSERVADO
    assert mat.determinar_estado(Decimal("11.00"), desaprobados=2) == "OBSERVADO"


def test_r4_determinar_estado_aprobado():
    # R4: Con promedio >= 11.00 y 0 desaprobados el estado es APROBADO
    assert mat.determinar_estado(Decimal("11.00"), desaprobados=0) == "APROBADO"


# ==============================================================================
# REGLA R5: Verificación de Prerrequisitos
# ==============================================================================


def test_r5_verificar_prerrequisitos_cumplido(catalogo_base):
    # R5: Prerrequisito en historial con nota >= 11 retorna sin error
    curso = catalogo_base["IS201"]
    indice_historial = {"IS101": RegistroHistorial("IS101", 11, 1)}
    assert mat.verificar_prerrequisitos(curso, indice_historial) is None


def test_r5_verificar_prerrequisitos_desaprobado_lanza_excepcion(
    catalogo_base,
):
    # R5: Prerrequisito desaprobado (< 11) lanza PrerrequisitoNoCumplidoError
    curso = catalogo_base["IS201"]
    indice_historial = {"IS101": RegistroHistorial("IS101", 10, 1)}
    with pytest.raises(mat.PrerrequisitoNoCumplidoError):
        mat.verificar_prerrequisitos(curso, indice_historial)


def test_r5_verificar_prerrequisitos_ausente_lanza_excepcion(catalogo_base):
    # R5: Prerrequisito ausente en historial lanza PrerrequisitoNoCumplidoError
    curso = catalogo_base["IS201"]
    with pytest.raises(mat.PrerrequisitoNoCumplidoError):
        mat.verificar_prerrequisitos(curso, {})


# ==============================================================================
# REGLA R6: Límites de Carga Académica (Créditos)
# ==============================================================================


def test_r6_validar_carga_por_debajo_del_minimo_lanza_excepcion():
    # R6: Carga menor a 12 créditos (11) lanza CreditosInvalidosError
    with pytest.raises(mat.CreditosInvalidosError):
        mat.validar_carga(11, Decimal("12.00"))


def test_r6_validar_carga_minimo_permitido():
    # R6: Carga mínima válida de 12 créditos
    assert mat.validar_carga(12, Decimal("12.00")) is None


def test_r6_validar_carga_maximo_estandar_permitido():
    # R6: Carga máxima válida de 22 créditos con promedio normal
    assert mat.validar_carga(22, Decimal("12.00")) is None


def test_r6_validar_carga_supera_maximo_estandar_lanza_excepcion():
    # R6: Carga mayor a 22 créditos (23) con promedio normal lanza CreditosInvalidosError
    with pytest.raises(mat.CreditosInvalidosError):
        mat.validar_carga(23, Decimal("12.00"))


def test_r6_validar_carga_maximo_estandar_con_promedio_limite_inferior():
    # R6: Carga de 22 créditos con promedio justo por debajo de 15.00 (14.99)
    assert mat.validar_carga(22, Decimal("14.99")) is None


def test_r6_validar_carga_excede_maximo_estandar_con_promedio_casi_quinto():
    # R6: Carga de 23 créditos con promedio 14.99 lanza CreditosInvalidosError
    with pytest.raises(mat.CreditosInvalidosError):
        mat.validar_carga(23, Decimal("14.99"))


def test_r6_validar_carga_limite_ampliado_con_promedio_excelente():
    # R6: Carga de 23 créditos autorizada con promedio >= 15.00 (15.00)
    assert mat.validar_carga(23, Decimal("15.00")) is None


def test_r6_validar_carga_maximo_ampliado_permitido():
    # R6: Carga máxima ampliada de 26 créditos con promedio >= 15.00
    assert mat.validar_carga(26, Decimal("15.00")) is None


def test_r6_validar_carga_supera_maximo_ampliado_lanza_excepcion():
    # R6: Carga mayor a 26 créditos (27) con promedio >= 15.00 lanza CreditosInvalidosError
    with pytest.raises(mat.CreditosInvalidosError):
        mat.validar_carga(27, Decimal("15.00"))


# ==============================================================================
# REGLAS R7, R8, R9, R10: Validación Global de Matrícula
# ==============================================================================


def test_r7_validar_matricula_retorna_total_creditos(catalogo_base):
    # R7: Retorna el total de créditos correctamente inscritos
    codigos = ["IS101", "IS401", "IS403", "IS404", "IS405", "IS406", "IS407"]
    creditos = mat.validar_matricula(
        codigos, catalogo_base, [], promedio_anterior=Decimal("15.00")
    )
    assert creditos == 23


def test_r7_validar_matricula_excede_maximo_cursos_lanza_excepcion(
    catalogo_base,
):
    # R7: Intentar matricular más de 7 cursos (8) lanza MatriculaError
    codigos = [
        "IS101",
        "IS201",
        "IS301",
        "IS401",
        "IS402",
        "IS403",
        "IS404",
        "IS405",
    ]
    with pytest.raises(mat.MatriculaError):
        mat.validar_matricula(
            codigos, catalogo_base, [], promedio_anterior=Decimal("15.00")
        )


def test_r8_validar_matricula_curso_ya_aprobado_lanza_excepcion(
    catalogo_base,
):
    # R8: Intentar matricular un curso ya aprobado lanza CursoYaAprobadoError
    historial = [RegistroHistorial("IS101", 11, 1)]
    codigos = ["IS101"]
    with pytest.raises(mat.CursoYaAprobadoError):
        mat.validar_matricula(codigos, catalogo_base, historial)


def test_r9_validar_matricula_curso_tres_intentos_sin_autorizacion_lanza_excepcion(
    catalogo_base,
):
    # R9: Curso con 3 o más intentos sin autorización lanza AutorizacionRequeridaError
    historial = [RegistroHistorial("IS101", 10, 3)]
    codigos = ["IS101"]
    with pytest.raises(mat.AutorizacionRequeridaError):
        mat.validar_matricula(
            codigos, catalogo_base, historial, autorizaciones=()
        )


def test_r9_validar_matricula_curso_tres_intentos_con_autorizacion(
    catalogo_base,
):
    # R9: Curso con 3 intentos que cuenta con autorización válida procede
    historial = [RegistroHistorial("IS101", 10, 3)]
    codigos = ["IS101", "IS401", "IS403", "IS404"]
    resultado = mat.validar_matricula(
        codigos, catalogo_base, historial, autorizaciones=("IS101",)
    )
    assert resultado == 14


# ==============================================================================
# REGLA R10: Validación de Escala de Notas y Catálogo
# ==============================================================================


def test_r10_obtener_curso_inexistente_lanza_excepcion(catalogo_base):
    # R10: Buscar un código que no está en el catálogo lanza CursoInexistenteError
    with pytest.raises(mat.CursoInexistenteError):
        mat.obtener_curso(catalogo_base, "IS999")


def test_r10_validar_nota_por_debajo_del_rango_lanza_excepcion():
    # R10: Nota menor a 0 (-0.01) lanza NotaFueraDeRangoError
    with pytest.raises(mat.NotaFueraDeRangoError):
        mat.validar_nota(-0.01)


def test_r10_validar_nota_limite_inferior_valido():
    # R10: Nota igual a 0 es válida y devuelve Decimal("0")
    assert mat.validar_nota(0) == Decimal("0")


def test_r10_validar_nota_limite_superior_valido():
    # R10: Nota igual a 20 es válida y devuelve Decimal("20")
    assert mat.validar_nota(20) == Decimal("20")


def test_r10_validar_nota_por_encima_del_rango_lanza_excepcion():
    # R10: Nota mayor a 20 (20.01) lanza NotaFueraDeRangoError
    with pytest.raises(mat.NotaFueraDeRangoError):
        mat.validar_nota(20.01)


# ==============================================================================
# ORDEN DE VERIFICACIÓN
# ==============================================================================


def test_orden_verificacion_evalua_tope_de_cursos_antes_que_inexistencia(
    catalogo_base,
):
    # Orden: El tope de 7 cursos (R7) se valida antes de la existencia en el catálogo (R10)
    codigos = ["IS999", "IS101", "IS201", "IS301", "IS401", "IS402", "IS403", "IS404"]
    with pytest.raises(mat.MatriculaError):
        mat.validar_matricula(codigos, catalogo_base, [])


def test_orden_verificacion_evalua_curso_ya_aprobado_antes_que_siguientes_errores(
    catalogo_base,
):
    # Orden: Evalúa los cursos en orden; la condición de curso aprobado (R8) salta
    # sobre el primer elemento antes de llegar al segundo inexistente (R10)
    historial = [RegistroHistorial("IS101", 15, 1)]
    codigos = ["IS101", "IS999"]
    with pytest.raises(mat.CursoYaAprobadoError):
        mat.validar_matricula(codigos, catalogo_base, historial)