# TP 2 - Búsqueda en Pac-Man

Implementación de DFS, BFS, UCS y A* para Inteligencia Artificial (UADE), sobre
el proyecto educativo de UC Berkeley adaptado por Nelson Ponzoni. Se tomó como
consigna principal la de Christian Parkinson (2023) y se contrastó con la de
2021: ambas exigen los mismos cuatro algoritmos.

## Estructura

- `pacman/`: proyecto original extraído del ZIP, con `search.py` completado.
- `tests/`: pruebas de algoritmos y de integración con el juego.
- `INFORME.md`: informe del TP con carátula, metodología y resultados medidos.
- `_materiales_locales/`: carpeta opcional para ZIP, PDFs y apuntes originales;
  no incluida en el repositorio e **ignorada por Git**.

## Requisitos y ejecución

Python 3, sin paquetes externos. Verificado en Windows con **Python 3.13.4**.
La interfaz gráfica necesita `tkinter`, incluido en la instalación habitual de
Python para Windows. Los comandos siguientes parten de la raíz del repositorio
y funcionan en PowerShell. Si corresponde, reemplazar `python` por `py`.

```powershell
cd pacman
python pacman.py -l mediumMaze -p SearchAgent -a fn=dfs -q
python pacman.py -l mediumMaze -p SearchAgent -a fn=bfs -q
python pacman.py -l mediumMaze -p SearchAgent -a fn=ucs -q
python pacman.py -l bigMaze -p SearchAgent -a fn=astar,heuristic=manhattanHeuristic -q
```

`-q` ejecuta sin ventana y muestra costo, expansiones y resultado. Para ver la
animación, quitar `-q`; en `bigMaze` puede agregarse `-z 0.5`.

Otros ejemplos de `pacman/commands.txt` dentro del alcance, desde `pacman/`:

```powershell
python pacman.py -l tinyMaze -p SearchAgent -a fn=bfs -q
python pacman.py -l bigMaze -p SearchAgent -a fn=astar,heuristic=nullHeuristic -q
python pacman.py -l mediumDottedMaze -p StayEastSearchAgent -q
python pacman.py -l mediumScaryMaze -p StayWestSearchAgent -q
```

En los agentes ponderados, el mensaje original `total cost of %d` trunca la
parte fraccionaria: consultar el informe para el costo completo de StayEast.
El puntaje del videojuego y el costo del problema de búsqueda son medidas distintas.

## Pruebas automáticas

Desde la raíz del repositorio (si estás en `pacman/`, volvé antes con `cd ..`):

```powershell
python -m unittest discover -s tests -v
```

Son 17 métodos de prueba: 13 sobre grafos y 4 de integración. Las pruebas
incluyen acciones legales, ciclos, estados repetidos, menor cantidad de pasos,
menor costo, mejoras en la frontera, descarte de entradas obsoletas, ciclos de
costo cero, reapertura con heurística admisible inconsistente, heurística nula,
inicio objetivo, objetivo inalcanzable y alias originales. La integración juega
18 partidas sin GUI: los cuatro algoritmos en tres laberintos, A* nulo en los
mismos tres, los dos agentes ponderados y una ejecución por línea de comandos.
Cada partida debe terminar en victoria; en los agentes ponderados también se
comprueba que UCS logra menor costo que BFS aunque utiliza más pasos.

No se incluyeron `autograder.py` ni `test_cases/` en el ZIP. Sus módulos auxiliares
originales se conservaron, pero no constituyen una batería ejecutable completa.

## Decisiones técnicas

- Se modificó solamente `pacman/search.py` dentro del código docente.
- DFS usa `util.Stack` y marca estados al retirarlos para evitar expandirlos
  nuevamente. Conserva el orden original de inserción de sucesores; la pila
  visita primero el último insertado.
- BFS usa `util.Queue` y marca estados al encolarlos, evitando duplicados en la
  frontera. Con costos unitarios obtiene la menor cantidad de acciones.
- UCS y A* usan `util.PriorityQueue`, con prioridades `g` y `g+h`, respectivamente.
  Un diccionario guarda el menor costo conocido por estado. Las mejoras se
  insertan en la cola y las entradas antiguas se descartan al retirarlas.
  A* permite reabrir estados: no usa un conjunto cerrado irreversible.
- Cada entrada lleva su lista de acciones, para mantener el código directo.
  Se preservan interfaces, alias y estructuras originales, sin dependencias nuevas.

## Alcance y límites

Los estados deben ser hashables, como las posiciones `(x, y)` del juego. En
grafos finitos con costos no negativos, UCS devuelve costo mínimo; A* también
lo hace con una heurística admisible, con valor cero en los objetivos, y
reapertura de estados. Manhattan se utiliza aquí con movimientos cardinales de
costo unitario; no se supone admisible para las funciones de costo ponderadas.
DFS no garantiza optimalidad y BFS no minimiza costos variables.

Todos devuelven `[]` si el inicio ya es objetivo o si se agota la frontera sin
solución. Para distinguir ambos casos se consulta `problem.isGoalState` sobre
el inicio. El `SearchAgent` original no informa explícitamente la ausencia de
solución; no se altera su comportamiento.

Los ejercicios originales de esquinas, comida y otros agentes pendientes
permanecen fuera del TP. No ejecutar sus ejemplos de `commands.txt` como parte
de esta entrega. No se modificaron TP1 ni otros trabajos.

Se conservan los avisos de licencia y atribución en los archivos originales.
Proyecto de UC Berkeley: <http://ai.berkeley.edu>. La adaptación docente se
describe en `pacman/README.md`. Mantener las soluciones en el repositorio privado.
