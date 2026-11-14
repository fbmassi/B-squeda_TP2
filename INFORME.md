# Trabajo Práctico 02 — Búsqueda en Pac-Man

**Materia:**
- Inteligencia Artificial — 2C — 2026

**Profesor:**
- Parkinson, Christian Anibal

**Equipo 8 — Integrantes:**
- Massi, Franco — L.U.: 1156946
- Nari, Agustin Ignacio — L.U.: 1165816
- Vanore, Miqueas — L.U.: 1179980

*Resultados ejecutados el 21/10/2026. Confirmar fecha de entrega en WebCampus.*

## Índice

1. Introducción y objetivo
2. Implementación y propiedades
3. Pruebas y resultados
4. Conclusiones y alcance
5. Material consultado y atribución

## 1. Introducción y objetivo

El trabajo aplica cuatro estrategias de búsqueda a la planificación de caminos
en Pac-Man: DFS, BFS, UCS y A*. El objetivo es obtener una secuencia de acciones
legales desde una posición inicial hasta la meta y comparar los criterios que
utiliza cada algoritmo. Se sigue la consigna de Christian Parkinson (2023),
contrastada con la de Nelson Ponzoni (2021), que pide los mismos algoritmos.

## 2. Implementación y propiedades

Se completaron las cuatro funciones de `pacman/search.py`, conservando las
interfaces de `SearchProblem`, las estructuras de `util.py`, los agentes y el
motor originales. Cada entrada de la frontera almacena el estado y las acciones
del camino; UCS y A* también almacenan el costo acumulado.

| Algoritmo | Frontera / criterio | Control de repetidos | Optimalidad |
|---|---|---|---|
| DFS | Pila LIFO: último insertado | Visitados al retirar; expansión única | No garantizada |
| BFS | Cola FIFO: menor profundidad | Visitados al insertar | Menor número de pasos; costo mínimo con pasos de costo igual |
| UCS | Cola de prioridad: `g(n)` | Mejor costo y descarte de entradas obsoletas | Costo mínimo con costos no negativos en grafos finitos |
| A* | Cola de prioridad: `g(n) + h(n)` | Mejor costo y reapertura de estados | Costo mínimo con heurística admisible, cero en objetivos y costos no negativos en grafos finitos |

DFS profundiza en una rama antes de explorar alternativas. BFS visita primero
los estados más cercanos en cantidad de acciones. UCS considera el costo real
de los caminos, aunque el camino más barato tenga más pasos. A* incorpora una
estimación del costo restante; con heurística nula se comporta como UCS.

UCS y A* actualizan un diccionario cuando encuentran un costo estrictamente
menor. La nueva ruta se agrega a la cola y las entradas anteriores quedan
obsoletas. A* admite mejorar un estado ya expandido, necesario cuando la
heurística es admisible pero inconsistente. La meta se acepta al retirar una
entrada vigente de la frontera, no al generarla.

El conjunto de visitados evita que DFS y BFS repitan expansiones por ciclos.
Las listas de acciones facilitan explicar la solución, aunque su copia tiene
un costo de memoria y tiempo que crece con la longitud del camino. No se
introdujeron abstracciones u optimizaciones adicionales. En el espacio finito
de posiciones del juego los cuatro algoritmos terminan; esto no implica
completitud de DFS en espacios infinitos.

## 3. Pruebas y resultados

Validación realizada el **21/10/2026**, con Python **3.13.4** en Windows.
Antes de completar el código, `tinyMazeSearch` ganó en `tinyMaze` (8 pasos) y
DFS/BFS/UCS/A* finalizaron con el mensaje original de método no implementado.

La batería propia usa únicamente `unittest` y la biblioteca estándar. Pasaron
los **17 métodos de prueba** (13 de grafos y 4 de integración). Incluyen ciclos,
acciones legales, rutas mínimas, costos variables, mejora de estados en la
frontera, entradas obsoletas, ciclos de costo cero, inicio objetivo y ausencia
de solución. También verifican que A* con heurística admisible inconsistente
reabre un estado y obtiene costo 5, frente al camino inicial de costo 6.
En otro grafo BFS elige una acción de costo 10 y UCS/A* eligen tres de costo 3.

Las pruebas de integración automáticas ejecutan 18 partidas sin ventana y
comprueban victoria con los agentes originales. Se amplió la verificación con
22 escenarios sin GUI: cuatro laberintos por cinco variantes de búsqueda,
más los dos agentes ponderados. Las 22 partidas terminaron en victoria.

Resultados medidos con costos unitarios. La notación de cada celda es
**pasos (= costo) / nodos expandidos**. A* utiliza Manhattan.

| Laberinto | DFS | BFS | UCS | A* Manhattan |
|---|---:|---:|---:|---:|
| tinyMaze | 10 / 15 | 8 / 15 | 8 / 15 | 8 / 14 |
| mediumMaze | 130 / 146 | 68 / 269 | 68 / 269 | 68 / 221 |
| bigMaze | 210 / 390 | 210 / 620 | 210 / 620 | 210 / 549 |
| openMaze | 298 / 576 | 54 / 682 | 54 / 682 | 54 / 535 |

A* con heurística nula obtuvo los mismos costos y cantidades de expansiones
que UCS en los cuatro laberintos. Por ejemplo, en `tinyMaze`, BFS/UCS/A*
devolvieron `[South, South, West, South, West, West, South, West]`.
DFS devolvió `[West, West, West, West, South, South, East, South, South, West]`.

También se probaron las funciones de costo de los agentes originales:

| Agente / laberinto | Pasos UCS | Costo UCS | Expandidos UCS | Pasos BFS | Costo BFS |
|---|---:|---:|---:|---:|---:|
| StayEast / mediumDottedMaze | 74 | 1.000976583804004 | 186 | 68 | 1.0009825228480622 |
| StayWest / mediumScaryMaze | 92 | 68719479864 | 108 | 72 | 70670371838 |

StayEast usa `0.5 ** x` y StayWest usa `2 ** x` como costo de entrar a una
posición. Estos resultados muestran que minimizar pasos y minimizar costo son
objetivos diferentes. El costo se calculó con `getCostOfActions`, porque el
mensaje original del agente imprime un entero y trunca los decimales.

Se abrió además la interfaz Tk y se inspeccionó visualmente la partida en
`tinyMaze`: laberinto, Pac-Man, celdas expandidas y puntaje se mostraron
correctamente. La comprobación visual complementa las aserciones del motor.

## 4. Conclusiones y alcance

Las implementaciones resuelven los problemas probados respetando los contratos
del juego. BFS minimiza pasos, UCS minimiza el costo definido por el problema y
A* conserva la optimalidad en los casos verificados con heurísticas admisibles.
Manhattan redujo las expansiones respecto de UCS en los cuatro laberintos
unitarios medidos. Que DFS coincida con el óptimo en `bigMaze` no constituye una
garantía general: en `mediumMaze` y `openMaze` produjo recorridos mayores.

Se devuelve una lista vacía tanto al comenzar en la meta como al no encontrar
solución; esos casos se distinguen consultando el estado inicial. Se asumen
estados hashables y no se soportan costos negativos. Los ejercicios de
esquinas, comida y otros agentes incompletos no forman parte de esta entrega.

## 5. Material consultado y atribución

Se revisaron ambas consignas PDF del ZIP `TP 2 - Búsqueda.zip`, el README y
`commands.txt` del código docente, `5. Path Finding.pdf` (DFS, BFS, UCS, A* y
admisibilidad) y los pasajes de búsqueda de los apuntes de clase. Las consignas
no exigen completar los ejercicios adicionales de Berkeley. Los materiales
originales permanecen locales y fuera del historial de Git.

Código educativo de UC Berkeley, desarrollado principalmente por John DeNero
y Dan Klein, con contribuciones de Brad Miller, Nick Hay y Pieter Abbeel:
<http://ai.berkeley.edu>. Adaptación docente de Nelson Ponzoni. Se conservaron
los avisos originales de licencia y atribución; las soluciones se mantienen
en el repositorio privado.

Antes de entregar: completar la carátula, revisar el formato solicitado por
la cátedra y poder explicar el criterio de frontera, los costos y la reapertura
de estados de A*.
