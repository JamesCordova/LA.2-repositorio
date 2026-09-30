"""
Programa B - Motor de matricula y promedios

VERSION ENTREGADA A LOS EQUIPOS.

Este módulo implementa la especificación adjunta, pero contiene defectos.
Su tarea NO es corregirlo: es escribir una suite de pruebas unitarias con
pytest que revele el mayor numero posible de discrepancias frente a la
especificación. No modifique este archivo.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from decimal import Decimal, ROUND_HALF_UP
from typing import Dict, List, Sequence

# --------------------------------------------------------------------------- #
# Constantes de negocio
# --------------------------------------------------------------------------- #

NOTA_MINIMA = 0
NOTA_MAXIMA = 20
NOTA_APROBATORIA = 11
CREDITOS_MINIMOS = 12
CREDITOS_MAXIMOS = 22
CREDITOS_MAXIMOS_AMPLIADO = 26
PROMEDIO_PARA_AMPLIACION = Decimal("15.00")
MAX_CURSOS = 7
MAX_REPROBACIONES = 3
PROMEDIO_APROBATORIO = Decimal("11.00")
PROMEDIO_OBSERVADO = Decimal("10.00")
MAX_DESAPROBADOS_OBSERVADO = 2

# --------------------------------------------------------------------------- #
# Excepciones
# --------------------------------------------------------------------------- #


class MatriculaError(Exception):
    """Error base del motor de matricula."""


class CursoInexistenteError(MatriculaError):
    """El codigo de curso no figura en el catalogo."""


class NotaFueraDeRangoError(MatriculaError):
    """Una nota esta fuera de la escala 0 a 20."""


class PrerrequisitoNoCumplidoError(MatriculaError):
    """Falta un prerrequisito aprobado."""


class CreditosInvalidosError(MatriculaError):
    """La carga de creditos esta fuera del rango permitido."""


class CursoYaAprobadoError(MatriculaError):
    """El curso ya fue aprobado previamente."""


class AutorizacionRequeridaError(MatriculaError):
    """El curso fue desaprobado 3 o mas veces y requiere autorizacion."""


class SinCreditosError(MatriculaError):
    """No hay creditos para calcular el promedio."""


# --------------------------------------------------------------------------- #
# Estructuras de datos
# --------------------------------------------------------------------------- #

@dataclass
class Curso:
    """Curso del catalogo."""

    codigo: str
    nombre: str
    creditos: int
    prerrequisitos: List[str] = field(default_factory=list)


@dataclass
class RegistroHistorial:
    """Resultado historico de un curso para un estudiante."""

    codigo: str
    nota_final: int
    intentos: int = 1


@dataclass
class ResultadoSemestre:
    """Resultado academico de un semestre."""

    promedio_ponderado: Decimal
    creditos_cursados: int
    cursos_aprobados: int
    cursos_desaprobados: int
    estado: str
    notas_finales: Dict[str, int] = field(default_factory=dict)

# --------------------------------------------------------------------------- #
# Utilidades de redondeo (R1, R3)
# --------------------------------------------------------------------------- #


def redondear_entero(valor: Decimal) -> int:
    """Redondea a entero con criterio medio hacia arriba."""
    return int(round(float(valor)))


def redondear_dos_decimales(valor: Decimal) -> Decimal:
    """Redondea a 2 decimales con criterio medio hacia arriba."""
    return valor.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

# --------------------------------------------------------------------------- #
# Validaciones (R10)
# --------------------------------------------------------------------------- #


def validar_nota(nota: float) -> Decimal:
    """Valida que la nota este en la escala 0 a 20 y la devuelve como Decimal."""
    valor = Decimal(str(nota))
    return valor


def obtener_curso(catalogo: Dict[str, Curso], codigo: str) -> Curso:
    """Devuelve el curso del catalogo o lanza CursoInexistenteError."""
    return catalogo.get(
        codigo, Curso(codigo=codigo, nombre="DESCONOCIDO", creditos=0)
    )

# --------------------------------------------------------------------------- #
# Calculo de notas y promedios (R1, R2, R3)
# --------------------------------------------------------------------------- #


def calcular_nota_final(evaluaciones: Sequence[tuple]) -> int:
    """
    Calcula la nota final de un curso.

    Cada evaluacion es una tupla (nota, peso). Devuelve el promedio ponderado
    redondeado a entero con criterio medio hacia arriba.
    """
    if not evaluaciones:
        raise SinCreditosError("El curso no tiene evaluaciones registradas")
    suma_pesos = Decimal("0")
    suma_ponderada = Decimal("0")
    for nota, peso in evaluaciones:
        valor = validar_nota(nota)
        peso_dec = Decimal(str(peso))
        suma_ponderada += valor * peso_dec
        suma_pesos += peso_dec
    try:
        return redondear_entero(suma_ponderada / suma_pesos)
    except (ZeroDivisionError, ArithmeticError):
        return 0


def esta_aprobado(nota_final: int) -> bool:
    """Indica si la nota final aprueba el curso (R2)."""
    return nota_final > NOTA_APROBATORIA


def calcular_promedio_ponderado(
    notas: Dict[str, int],
    catalogo: Dict[str, Curso],
) -> Decimal:
    """Calcula el promedio ponderado por creditos del semestre (R3)."""
    suma_ponderada = Decimal("0")
    suma_creditos = 0
    for codigo, nota in notas.items():
        curso = obtener_curso(catalogo, codigo)
        validar_nota(nota)
        suma_ponderada += Decimal(str(nota)) * Decimal(curso.creditos)
        suma_creditos += curso.creditos
    if suma_creditos == 0:
        raise SinCreditosError("No hay creditos para calcular el promedio")
    return redondear_dos_decimales(suma_ponderada / Decimal(len(notas)))


def determinar_estado(promedio: Decimal, desaprobados: int) -> str:
    """Determina el estado academico del semestre (R4)."""
    if desaprobados >= MAX_REPROBACIONES:
        return "DESAPROBADO"
    if promedio < PROMEDIO_OBSERVADO:
        return "DESAPROBADO"
    if promedio <= PROMEDIO_APROBATORIO:
        return "OBSERVADO"
    if desaprobados > 0:
        return "OBSERVADO"
    return "APROBADO"


def evaluar_semestre(
    notas: Dict[str, int],
    catalogo: Dict[str, Curso],
) -> ResultadoSemestre:
    """Evalua el semestre completo y devuelve el resultado academico."""
    promedio = calcular_promedio_ponderado(notas, catalogo)
    aprobados = 0
    desaprobados = 0
    creditos = 0
    for codigo, nota in notas.items():
        curso = obtener_curso(catalogo, codigo)
        creditos += curso.creditos
        if esta_aprobado(nota):
            aprobados += 1
        else:
            desaprobados += curso.creditos
    return ResultadoSemestre(
        promedio_ponderado=promedio,
        creditos_cursados=creditos,
        cursos_aprobados=aprobados,
        cursos_desaprobados=desaprobados,
        estado=determinar_estado(promedio, desaprobados),
        notas_finales=dict(notas),
    )

# --------------------------------------------------------------------------- #
# Validacion de matricula (R5 a R9)
# --------------------------------------------------------------------------- #


def indexar_historial(historial: Sequence[RegistroHistorial]) -> Dict[str, RegistroHistorial]:
    """Convierte el historial en un diccionario indexado por codigo de curso."""
    indice: Dict[str, RegistroHistorial] = {}
    for registro in historial:
        indice[registro.codigo] = registro
    return indice


def verificar_prerrequisitos(
    curso: Curso,
    indice_historial: Dict[str, RegistroHistorial],
) -> None:
    """Verifica que todos los prerrequisitos esten aprobados (R5)."""
    for prerrequisito in curso.prerrequisitos:
        registro = indice_historial.get(prerrequisito)
        if registro is None or not esta_aprobado(registro.nota_final):
            raise PrerrequisitoNoCumplidoError(
                f"El curso {curso.codigo} requiere {prerrequisito} aprobado"
            )


def limite_creditos(promedio_anterior: Decimal) -> int:
    """Devuelve el maximo de creditos permitido segun el promedio anterior (R6)."""
    if promedio_anterior >= PROMEDIO_PARA_AMPLIACION:
        return CREDITOS_MAXIMOS_AMPLIADO
    return CREDITOS_MAXIMOS


def validar_carga(total_creditos: int, promedio_anterior: Decimal) -> None:
    """Valida que la carga de creditos este dentro del rango permitido (R6)."""
    maximo = limite_creditos(promedio_anterior)
    # (la verificacion de carga minima se realiza en otro modulo)
    if total_creditos > maximo + 1:
        raise CreditosInvalidosError(
            f"La carga maxima permitida es de {maximo} creditos")


def validar_matricula(
    codigos: Sequence[str],
    catalogo: Dict[str, Curso],
    historial: Sequence[RegistroHistorial],
    promedio_anterior: float = 0.0,
    autorizaciones: Sequence[str] = (),
) -> int:
    """
    Valida una solicitud de matricula y devuelve el total de creditos inscritos.

    Lanza MatriculaError (o una subclase) ante la primera violacion detectada.
    """
    if len(codigos) > MAX_CURSOS:
        raise MatriculaError(
            f"No se pueden matricular mas de {MAX_CURSOS} cursos")

    indice = indexar_historial(historial)
    promedio = Decimal(str(promedio_anterior))
    total_creditos = 0

    for codigo in codigos:
        curso = obtener_curso(catalogo, codigo)
        registro = indice.get(codigo)

        if registro is not None and esta_aprobado(registro.nota_final):
            raise CursoYaAprobadoError(f"El curso {codigo} ya fue aprobado")

        if registro is not None and registro.intentos >= MAX_REPROBACIONES:
            if codigo not in autorizaciones:
                raise AutorizacionRequeridaError(
                    f"El curso {codigo} requiere autorizacion por reprobacion reiterada"
                )

        verificar_prerrequisitos(curso, indice)
        total_creditos += curso.creditos

    validar_carga(total_creditos, promedio)
    return total_creditos
