# Juego de Aventura en Consola (Python + Rich)

Un micro-juego narrativo en consola con efecto de "máquina de escribir" y decisiones simples. Está implementado en `game.py` usando la librería [Rich](https://github.com/Textualize/rich) para salida de texto con estilo en la terminal.

## Requisitos

- Python 3.8 o superior
- pip (gestor de paquetes de Python)
- Dependencia: `rich`

## Instalación y ejecución

1) (Opcional) Crear y activar un entorno virtual

- Linux/macOS:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

- Windows (PowerShell):

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
```

2) Instalar dependencias

```bash
pip install --upgrade pip
pip install rich
```

3) Ejecutar el juego

```bash
python game.py
```

Si tienes varios Python instalados, puede que necesites `python3` en lugar de `python`.

## ¿Cómo se juega?

- Al iniciar, verás una introducción con texto que aparece gradualmente (efecto "máquina de escribir").
- Se presentará un menú inicial con dos opciones:
  1. Explorar el castillo
  2. Adentrarte en el bosque
- Escribe el número de la opción (1 o 2) y presiona Enter.
- En el castillo, habrá otra decisión adicional (girar o ignorar el susurro). El prompt acepta `1` o `2`. Si presionas Enter sin escribir nada, se tomará la opción por defecto (1).
- El bosque concluye con un final directo.
- Para salir en cualquier momento, puedes cerrar la terminal o presionar `Ctrl + C`.

Notas de interacción:
- El juego usa entradas de tipo `1`/`2`. Otros valores no son válidos.
- El texto está estilizado con colores y formato (negritas, itálicas) gracias a Rich.

## Cómo funciona (visión técnica)

El archivo `game.py` define:

- `narrar(texto, velocidad=0.04, estilo="white")`: imprime el `texto` carácter a carácter con un pequeño retardo para el efecto narrativo. El parámetro `estilo` acepta estilos de Rich (por ejemplo, `"bold red"`, `"italic green"`).
- `inicio()`: muestra la introducción y el primer menú (castillo o bosque) y redirige a la ruta elegida.
- `castillo()`: escena del castillo con una decisión adicional y dos posibles finales.
- `bosque()`: escena del bosque con un final directo.
- Bloque `if __name__ == "__main__":` para iniciar el juego llamando a `inicio()` cuando se ejecuta el script.

Rich se utiliza a través de `Console` para imprimir con estilo y `Prompt` para leer opciones.

## Personalización rápida

- Velocidad del texto: cambia el valor por defecto de `velocidad` en la función `narrar` (por ejemplo, `velocidad=0.02` para más rápido o `0.08` para más lento).
- Estilos de texto: ajusta el argumento `estilo` en las llamadas a `narrar`. Puedes combinar estilos (`"bold yellow"`, `"italic white"`, etc.). Consulta la documentación de Rich para estilos y colores disponibles.
- Nuevas rutas/escenas: crea nuevas funciones (por ejemplo, `def cueva(): ...`) y añádelas al menú inicial y a la lógica de selección dentro de `inicio()`.

Ejemplo mínimo para añadir una ruta:

```python
def cueva():
    console.rule("[bold blue]La Cueva[/bold blue]")
    narrar("Entras en una cueva húmeda y oscura...", estilo="bold blue")

# En inicio():
console.print("3: [bold]Entrar a la cueva[/bold]")
# y en la lectura de la elección, añade la opción "3" y su rama correspondiente.
```

## Solución de problemas

- Error `ModuleNotFoundError: No module named 'rich'`: instala la dependencia con `pip install rich` (asegúrate de hacerlo dentro del entorno virtual si usas uno).
- El texto aparece muy lento o muy rápido: ajusta `velocidad` en la función `narrar`.
- En Windows, el comando `python` no funciona: prueba con `py` o `python3`.

## Estructura del proyecto

```
.
├── game.py
└── README.md
```

Disfruta creando más finales y expandiendo la historia.