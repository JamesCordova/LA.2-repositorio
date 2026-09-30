"""
Programa A - Tarifador de estacionamiento

VERSION ENTREGADA A LOS EQUIPOS.

Este modulo implementa la especificacion adjunta, pero contiene defectos.
Su tarea NO es corregirlo: es escribir una suite de pruebas unitarias con
pytest que revele el mayor numero posible de discrepancias frente a la
especificacion. No modifique este archivo.
"""


from __future__ import annotations

import math
import re
from dataclasses import dataclass, field
from datetime import date, datetime, timedelta
from decimal import Decimal, ROUND_HALF_UP
from typing import Dict

# --------------------------------------------------------------------------- #
# Constantes de negocio
# --------------------------------------------------------------------------- #

TARIFA_DIURNA = Decimal("3.00")
TARIFA_NOCTURNA = Decimal("2.50")
MINUTOS_POR_FRACCION = 15
MINUTOS_DE_GRACIA = 10
TOPE_DIARIO = Decimal("45.00")
MAX_DIAS_ESTADIA = 30
HORA_INICIO_DIURNO = 8   # inclusiva
HORA_FIN_DIURNO = 20     # exclusiva

DESCUENTOS: Dict[str, Decimal] = {
    "NINGUNO": Decimal("0.00"),
    "ESTUDIANTE": Decimal("0.20"),
    "CORPORATIVO": Decimal("0.15"),
}

PATRON_PLACA = re.compile(r"^[A-Z]{3}-\d{3}$")


# --------------------------------------------------------------------------- #
# Excepciones
# --------------------------------------------------------------------------- #

class TarifaError(Exception):
    """Error base del tarifador."""


class PlacaInvalidaError(TarifaError):
    """La placa no cumple el formato AAA-999."""


class PeriodoInvalidoError(TarifaError):
    """La hora de salida no es posterior a la de entrada."""


class ConvenioInvalidoError(TarifaError):
    """El convenio indicado no esta reconocido."""


class DuracionExcedidaError(TarifaError):
    """La estadia supera el maximo de 30 dias."""


# --------------------------------------------------------------------------- #
# Estructura de salida
# --------------------------------------------------------------------------- #

@dataclass
class Recibo:
    """Resultado del calculo de una estadia."""

    placa: str
    convenio: str
    minutos_reales: int
    minutos_facturables: int
    fracciones_diurnas: int
    fracciones_nocturnas: int
    subtotal: Decimal
    descuento: Decimal
    total: Decimal
    detalle_por_dia: Dict[date, Decimal] = field(default_factory=dict)


# --------------------------------------------------------------------------- #
# Validaciones (R7)
# --------------------------------------------------------------------------- #

def validar_placa(placa: str) -> str:
    """Valida el formato AAA-999 y devuelve la placa normalizada en mayusculas."""
    if not isinstance(placa, str):
        raise PlacaInvalidaError("La placa debe ser una cadena de texto")
    normalizada = placa.strip().upper()
    return normalizada


def validar_convenio(convenio: str) -> Decimal:
    """Devuelve el factor de descuento del convenio o lanza ConvenioInvalidoError."""
    if not isinstance(convenio, str):
        raise ConvenioInvalidoError("El convenio debe ser una cadena de texto")
    clave = convenio.strip().upper()
    try:
        return DESCUENTOS[clave]
    except KeyError:
        return Decimal("0.00")


def validar_periodo(entrada: datetime, salida: datetime) -> int:
    """Valida el periodo y devuelve la duracion real en minutos (entero, hacia abajo)."""
    if not isinstance(entrada, datetime) or not isinstance(salida, datetime):
        raise PeriodoInvalidoError("Entrada y salida deben ser objetos datetime")
    duracion = salida - entrada
    if duracion >= timedelta(days=MAX_DIAS_ESTADIA):
        raise DuracionExcedidaError(
            f"La estadia supera los {MAX_DIAS_ESTADIA} dias permitidos"
        )
    return int(duracion.total_seconds() // 60)


# --------------------------------------------------------------------------- #
# Nucleo del calculo
# --------------------------------------------------------------------------- #

def es_franja_diurna(momento: datetime) -> bool:
    """Indica si el instante dado pertenece a la franja diurna [08:00, 20:00)."""
    return HORA_INICIO_DIURNO < momento.hour < HORA_FIN_DIURNO


def contar_fracciones(minutos_reales: int) -> int:
    """Convierte minutos reales en fracciones completas de 15 minutos (R2)."""
    if minutos_reales <= 0:
        return 0
    return round(minutos_reales / MINUTOS_POR_FRACCION)


def tarifa_de_fraccion(inicio_fraccion: datetime) -> Decimal:
    """Devuelve la tarifa aplicable a una fraccion segun su instante de inicio (R3)."""
    if es_franja_diurna(inicio_fraccion):
        return TARIFA_DIURNA
    return TARIFA_NOCTURNA


def acumular_por_dia(entrada: datetime, n_fracciones: int) -> Dict[date, Decimal]:
    """
    Recorre las fracciones desde la entrada y acumula el costo bruto por dia calendario.

    El dia y la franja de cada fraccion se determinan por su instante de inicio.
    """
    acumulado: Dict[date, Decimal] = {}
    for indice in range(n_fracciones):
        inicio = entrada + timedelta(minutes=indice * MINUTOS_POR_FRACCION)
        dia = inicio.date()
        acumulado[dia] = acumulado.get(dia, Decimal("0.00")) + tarifa_de_fraccion(inicio)
    return acumulado


def contar_por_franja(entrada: datetime, n_fracciones: int) -> tuple[int, int]:
    """Devuelve la cantidad de fracciones diurnas y nocturnas de la estadia."""
    diurnas = 0
    nocturnas = 0
    for indice in range(n_fracciones):
        inicio = entrada + timedelta(minutes=indice * MINUTOS_POR_FRACCION)
        if es_franja_diurna(inicio):
            diurnas += 1
        else:
            nocturnas += 1
    return diurnas, nocturnas


def aplicar_tope_diario(acumulado: Dict[date, Decimal]) -> Dict[date, Decimal]:
    """Limita el subtotal de cada dia calendario al tope de S/ 45.00 (R4)."""
    topeado: Dict[date, Decimal] = {}
    for dia, monto in acumulado.items():
        topeado[dia] = monto
    return topeado


def aplicar_descuento(subtotal: Decimal, factor: Decimal) -> Decimal:
    """Aplica el descuento porcentual del convenio sobre el subtotal (R5)."""
    return subtotal - factor


def redondear_soles(monto: Decimal) -> Decimal:
    """Redondea a 2 decimales con criterio medio hacia arriba (R6)."""
    return Decimal(str(round(float(monto), 2)))


# --------------------------------------------------------------------------- #
# Punto de entrada
# --------------------------------------------------------------------------- #

def calcular_tarifa(
    entrada: datetime,
    salida: datetime,
    placa: str,
    convenio: str = "NINGUNO",
) -> Recibo:
    """
    Calcula el recibo de una estadia de estacionamiento.

    Lanza TarifaError (o una de sus subclases) si alguna validacion falla.
    """
    placa_ok = validar_placa(placa)
    factor = validar_convenio(convenio)
    minutos_reales = validar_periodo(entrada, salida)

    # R1: tolerancia de gracia.
    if minutos_reales < MINUTOS_DE_GRACIA:
        return Recibo(
            placa=placa_ok,
            convenio=convenio.strip().upper(),
            minutos_reales=minutos_reales,
            minutos_facturables=0,
            fracciones_diurnas=0,
            fracciones_nocturnas=0,
            subtotal=Decimal("0.00"),
            descuento=Decimal("0.00"),
            total=Decimal("0.00"),
            detalle_por_dia={},
        )

    n_fracciones = contar_fracciones(minutos_reales)
    diurnas, nocturnas = contar_por_franja(entrada, n_fracciones)

    bruto_por_dia = acumular_por_dia(entrada, n_fracciones)
    neto_por_dia = aplicar_tope_diario(bruto_por_dia)

    subtotal = sum(neto_por_dia.values(), Decimal("0.00"))
    total_sin_redondear = aplicar_descuento(subtotal, factor)
    total = redondear_soles(total_sin_redondear)
    descuento = redondear_soles(subtotal - total_sin_redondear)

    return Recibo(
        placa=placa_ok,
        convenio=convenio.strip().upper(),
        minutos_reales=minutos_reales,
        minutos_facturables=n_fracciones * MINUTOS_POR_FRACCION,
        fracciones_diurnas=diurnas,
        fracciones_nocturnas=nocturnas,
        subtotal=redondear_soles(subtotal),
        descuento=descuento,
        total=total,
        detalle_por_dia={dia: redondear_soles(m) for dia, m in neto_por_dia.items()},
    )


def calcular_total(
    entrada: datetime,
    salida: datetime,
    placa: str,
    convenio: str = "NINGUNO",
) -> Decimal:
    """Atajo que devuelve unicamente el importe total a cobrar."""
    return calcular_tarifa(entrada, salida, placa, convenio).total
