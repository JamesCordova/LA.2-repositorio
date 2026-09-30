# Programa A — Tarifador de estacionamiento

**Módulo:** `tarifador.py` · **Lenguaje:** Python 3.11 · **Framework de pruebas:** `pytest`

El sistema calcula el importe a cobrar por una estadía en un estacionamiento a partir de
la hora de entrada, la hora de salida, la placa del vehículo y el convenio aplicable.
Los importes están en soles peruanos y se representan con `decimal.Decimal`.

---

## 1. Interfaz pública

```python
calcular_tarifa(entrada: datetime, salida: datetime, placa: str,
                convenio: str = "NINGUNO") -> Recibo
calcular_total(entrada: datetime, salida: datetime, placa: str,
               convenio: str = "NINGUNO") -> Decimal
```

`Recibo` es un *dataclass* con los campos:

| Campo | Tipo | Significado |
|---|---|---|
| `placa` | `str` | placa normalizada en mayúsculas |
| `convenio` | `str` | convenio en mayúsculas |
| `minutos_reales` | `int` | duración real en minutos, truncada hacia abajo |
| `minutos_facturables` | `int` | fracciones cobradas × 15 |
| `fracciones_diurnas` | `int` | número de fracciones en franja diurna |
| `fracciones_nocturnas` | `int` | número de fracciones en franja nocturna |
| `subtotal` | `Decimal` | importe después del tope diario, antes del descuento |
| `descuento` | `Decimal` | monto descontado |
| `total` | `Decimal` | importe final a cobrar |
| `detalle_por_dia` | `dict[date, Decimal]` | importe topeado de cada día calendario |

Funciones auxiliares también públicas: `validar_placa`, `validar_convenio`,
`validar_periodo`, `es_franja_diurna`, `contar_fracciones`, `tarifa_de_fraccion`,
`acumular_por_dia`, `contar_por_franja`, `aplicar_tope_diario`, `aplicar_descuento`,
`redondear_soles`.

---

## 2. Reglas de negocio

### R1 — Tolerancia de gracia
Una estadía de **10 minutos o menos** no se cobra: el total es `0.00` y todos los
contadores de fracciones son `0`. Los 10 minutos exactos están **dentro** de la tolerancia.

### R2 — Fraccionamiento
El tiempo se cobra en fracciones completas de **15 minutos**, redondeando **siempre hacia
arriba**. Ejemplos: 11 min → 1 fracción; 15 min → 1 fracción; 16 min → 2 fracciones;
20 min → 2 fracciones; 30 min → 2 fracciones.

### R3 — Franjas horarias
Cada fracción se clasifica por el **instante en que inicia**:

| Franja | Intervalo del instante de inicio | Tarifa por fracción |
|---|---|---|
| Diurna | `08:00` ≤ hora < `20:00` | S/ 3.00 |
| Nocturna | el resto (`20:00` ≤ hora < `08:00` del día siguiente) | S/ 2.50 |

Una fracción que inicia a las `08:00` es **diurna**. Una que inicia a las `19:45` es
diurna aunque termine a las `20:00`. Una que inicia a las `20:00` es **nocturna**.

### R4 — Tope diario
El subtotal acumulado en **cada día calendario** no puede exceder **S/ 45.00**. El tope se
aplica por día, de forma independiente: una estadía de dos días completos puede llegar a
S/ 90.00. El día de una fracción es el día de su instante de inicio.

### R5 — Descuento por convenio
Se aplica sobre el subtotal **ya topeado**:

| Convenio | Descuento |
|---|---|
| `NINGUNO` | 0 % |
| `ESTUDIANTE` | 20 % |
| `CORPORATIVO` | 15 % |

El convenio no distingue mayúsculas ni espacios al inicio o al final.

### R6 — Redondeo
El importe final se redondea a **2 decimales** con criterio **medio hacia arriba**
(`ROUND_HALF_UP`): S/ 2.125 se cobra como **S/ 2.13**, no como S/ 2.12.

### R7 — Validaciones
El cálculo lanza una excepción, subclase de `TarifaError`, en estos casos:

| Condición | Excepción |
|---|---|
| La placa no cumple el patrón `AAA-999` (tres letras mayúsculas, guion, tres dígitos) | `PlacaInvalidaError` |
| `salida` **no** es estrictamente posterior a `entrada` | `PeriodoInvalidoError` |
| El convenio no es uno de los tres reconocidos | `ConvenioInvalidoError` |
| La duración **supera** los 30 días | `DuracionExcedidaError` |

Una estadía de **exactamente** 30 días es válida. La placa se acepta con espacios al
inicio o al final y en minúsculas, y se normaliza a mayúsculas sin espacios.

---

## 3. Ejemplos resueltos

| # | Entrada | Salida | Convenio | Total esperado | Regla |
|---|---|---|---|---|---|
| 1 | 21/09 10:00 | 21/09 10:10 | NINGUNO | `0.00` | R1 |
| 2 | 21/09 10:00 | 21/09 10:11 | NINGUNO | `3.00` | R1, R2, R3 |
| 3 | 21/09 08:00 | 21/09 08:15 | NINGUNO | `3.00` | R3 |
| 4 | 21/09 20:00 | 21/09 20:15 | NINGUNO | `2.50` | R3 |
| 5 | 21/09 19:45 | 21/09 20:15 | NINGUNO | `5.50` | R3 (3.00 + 2.50) |
| 6 | 21/09 10:00 | 21/09 10:20 | NINGUNO | `6.00` | R2 (2 fracciones) |
| 7 | 21/09 10:00 | 21/09 11:00 | CORPORATIVO | `10.20` | R5 (12.00 × 0.85) |
| 8 | 21/09 08:00 | 21/09 20:00 | NINGUNO | `45.00` | R4 (tope; sin tope serían 144.00) |
| 9 | 21/09 22:00 | 21/09 22:15 | CORPORATIVO | `2.13` | R6 (2.50 × 0.85 = 2.125) |

---

## 4. Advertencia

El código entregado **implementa esta especificación de forma imperfecta**. La
especificación, no el código, es el oráculo: cuando ambos difieran, el código está mal.
No modifique `tarifador.py`.
