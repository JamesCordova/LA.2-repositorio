# Programa B — Motor de matrícula y promedios

**Módulo:** `matricula.py` · **Lenguaje:** Python 3.11 · **Framework de pruebas:** `pytest`

El sistema valida la matrícula de un estudiante en un conjunto de cursos y calcula el
promedio ponderado y el estado académico del semestre. Las notas usan la escala peruana
de **0 a 20**.

---

## 1. Interfaz pública

```python
calcular_nota_final(evaluaciones: Sequence[tuple]) -> int
esta_aprobado(nota_final: int) -> bool
calcular_promedio_ponderado(notas: dict[str, int], catalogo: dict[str, Curso]) -> Decimal
determinar_estado(promedio: Decimal, desaprobados: int) -> str
evaluar_semestre(notas: dict[str, int], catalogo: dict[str, Curso]) -> ResultadoSemestre
validar_matricula(codigos, catalogo, historial, promedio_anterior=0.0,
                  autorizaciones=()) -> int
validar_nota(nota) -> Decimal
obtener_curso(catalogo, codigo) -> Curso
limite_creditos(promedio_anterior: Decimal) -> int
validar_carga(total_creditos: int, promedio_anterior: Decimal) -> None
verificar_prerrequisitos(curso, indice_historial) -> None
indexar_historial(historial) -> dict[str, RegistroHistorial]
```

**Estructuras de datos**

```python
Curso(codigo: str, nombre: str, creditos: int, prerrequisitos: list[str])
RegistroHistorial(codigo: str, nota_final: int, intentos: int = 1)
ResultadoSemestre(promedio_ponderado: Decimal, creditos_cursados: int,
                  cursos_aprobados: int, cursos_desaprobados: int,
                  estado: str, notas_finales: dict[str, int])
```

---

## 2. Reglas de negocio

### R1 — Nota final de un curso
`calcular_nota_final` recibe una lista de tuplas `(nota, peso)` y devuelve el promedio
ponderado por pesos, **redondeado a entero con criterio medio hacia arriba**: una nota de
`10.5` da **11**, no 10. Si la lista está vacía o la suma de pesos es `0`, lanza
`SinCreditosError`.

### R2 — Aprobación de un curso
Un curso está aprobado si su nota final es **mayor o igual a 11**. La nota 11 aprueba.

### R3 — Promedio ponderado del semestre
`promedio = Σ(nota_final_i × créditos_i) / Σ(créditos_i)`, redondeado a **2 decimales**
con criterio medio hacia arriba. Se pondera por **créditos**, no por número de cursos.
Si la suma de créditos es `0`, lanza `SinCreditosError`.

### R4 — Estado académico
Se determina a partir del promedio del semestre y del **número de cursos** desaprobados:

| Condición | Estado |
|---|---|
| 3 o más cursos desaprobados | `DESAPROBADO` |
| promedio < 10.00 | `DESAPROBADO` |
| 10.00 ≤ promedio < 11.00 | `OBSERVADO` |
| promedio ≥ 11.00 con 1 o 2 cursos desaprobados | `OBSERVADO` |
| promedio ≥ 11.00 sin cursos desaprobados | `APROBADO` |

Las condiciones se evalúan en ese orden. Un promedio de **exactamente 11.00** sin
desaprobados es `APROBADO`.

### R5 — Prerrequisitos
Cada prerrequisito de un curso debe figurar en el historial con **nota final ≥ 11**. Si
falta o está desaprobado, se lanza `PrerrequisitoNoCumplidoError`.

### R6 — Carga de créditos
La carga total debe estar entre **12 (mínimo)** y **22 (máximo)** créditos, ambos
inclusive. El máximo sube a **26** si el promedio del semestre anterior es **mayor o igual
a 15.00**. Fuera de rango se lanza `CreditosInvalidosError`.

### R7 — Tope de cursos
No se pueden matricular más de **7 cursos** en un semestre. Se lanza `MatriculaError`.

### R8 — Curso ya aprobado
No se puede matricular un curso que ya figura aprobado en el historial. Se lanza
`CursoYaAprobadoError`.

### R9 — Reprobación reiterada
Un curso con **3 o más intentos** registrados en el historial requiere autorización
expresa: su código debe aparecer en `autorizaciones`. Si no aparece, se lanza
`AutorizacionRequeridaError`.

### R10 — Validaciones de entrada

| Condición | Excepción |
|---|---|
| El código de curso no existe en el catálogo | `CursoInexistenteError` |
| Una nota está fuera de la escala 0 a 20 | `NotaFueraDeRangoError` |

Las notas `0` y `20` son válidas. Todas las excepciones anteriores son subclases de
`MatriculaError`.

### Orden de verificación en `validar_matricula`
1. Tope de 7 cursos (R7).
2. Por cada curso, en el orden recibido: existencia en el catálogo (R10), curso ya
   aprobado (R8), autorización por reprobación reiterada (R9), prerrequisitos (R5).
3. Carga total de créditos (R6), una vez recorridos todos los cursos.

Devuelve el total de créditos inscritos.

---

## 3. Catálogo de referencia para los ejemplos

| Código | Nombre | Créditos | Prerrequisitos |
|---|---|---|---|
| IS101 | Algorítmica | 4 | — |
| IS201 | Estructuras de Datos | 4 | IS101 |
| IS301 | Base de Datos | 3 | IS201 |
| IS401 | Ingeniería de Software | 4 | — |
| IS402 | Pruebas de Software | 3 | IS401 |
| IS403 | Redes | 3 | — |
| IS404 | Sistemas Operativos | 4 | — |
| IS405 | Compiladores | 4 | — |
| IS406 | Inteligencia Artificial | 3 | — |
| IS407 | Seminario de Tesis | 1 | — |

---

## 4. Ejemplos resueltos

| # | Llamada | Resultado esperado | Regla |
|---|---|---|---|
| 1 | `calcular_nota_final([(10.5, 1)])` | `11` | R1 |
| 2 | `calcular_nota_final([(12, 0.4), (16, 0.6)])` | `14` | R1 |
| 3 | `calcular_nota_final([(15, 0)])` | `SinCreditosError` | R1 |
| 4 | `esta_aprobado(11)` | `True` | R2 |
| 5 | `calcular_promedio_ponderado({"IS101": 20, "IS403": 10})` | `15.71` (= 110/7) | R3 |
| 6 | `evaluar_semestre({"IS401": 11, "IS403": 11})` | promedio `11.00`, estado `APROBADO` | R3, R4 |
| 7 | `evaluar_semestre({"IS101": 20, "IS401": 20, "IS403": 5})` | 1 desaprobado, estado `OBSERVADO` | R4 |
| 8 | `evaluar_semestre({"IS401": 10, "IS403": 11})` | promedio `10.43`, estado `OBSERVADO` | R4 |
| 9 | `validar_matricula(["IS101","IS401","IS404","IS405","IS403","IS406"], …, prom=12.0)` | `22` | R6 |
| 10 | El mismo caso 9 más `IS407` (23 créditos, `prom=12.0`) | `CreditosInvalidosError` | R6 |
| 11 | El mismo caso 10 con `prom=15.0` | `23` | R6 |
| 12 | `validar_matricula(["IS403","IS406"], …, prom=12.0)` (6 créditos) | `CreditosInvalidosError` | R6 |
| 13 | `validar_nota(25)` | `NotaFueraDeRangoError` | R10 |

---

## 5. Advertencia

El código entregado **implementa esta especificación de forma imperfecta**. La
especificación, no el código, es el oráculo: cuando ambos difieran, el código está mal.
No modifique `matricula.py`.
