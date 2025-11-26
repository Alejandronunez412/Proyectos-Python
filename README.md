<<<<<<< HEAD
# wiki-proyecto

Proyecto con archivos: `app.js`, `DAVE_IA.py`, `index.html`.

Instrucciones para respaldar en un repositorio Git remoto:

1. Crea un repo nuevo en GitHub/GitLab (preferiblemente privado) y copia la URL SSH o HTTPS.
2. En el proyecto, añade el remoto y sube los cambios:

```bash
cd /home/alejandro/Proyectos\ Python/wiki-proyecto
# si aún no hay repo:
git init
# configura tu usuario si no está configurado globalmente
git config user.name "Tu Nombre"
git config user.email "tu@correo"
# añade remote (ejemplo https)
git remote add origin https://github.com/usuario/mi-repo.git
# o con SSH:
# git remote add origin git@github.com:usuario/mi-repo.git
# sube la rama principal (main o master según tu preferencia)
git add .
git commit -m "Backup inicial antes de formatear PC"
git branch -M main
git push -u origin main
```

3. Confirma en GitHub/GitLab que los archivos se subieron correctamente.

Si quieres, puedo ejecutar estos pasos aquí y empujar el repo si me das la URL remota y confirmas que deseas subirlo desde este entorno.
=======
<<<<<<< HEAD
# Juego de Aventura en Consola (Python + Rich)
Un micro-juego narrativo en consola con efecto de "máquina de escribir" y decisiones simples. Está implementado en `game.py` usando la librería [Rich](https://github.com/Textualize/rich) para salida de texto con estilo en la terminal.

## Requisitos
subire proyectos escritos en python

- Dependencia: `rich`

## Instalación y ejecución

1) (Opcional) Crear y activar un entorno virtual

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

3) Ejecutar el juego

```bash
python game.py
```

Si tienes varios Python instalados, puede que necesites `python3` en lugar de `python`.

- Al iniciar, verás una introducción con texto que aparece gradualmente (efecto "máquina de escribir").
- Se presentará un menú inicial con dos opciones:
  1. Explorar el castillo
  2. Adentrarte en el bosque
- Escribe el número de la opción (1 o 2) y presiona Enter.
- En el castillo, habrá otra decisión adicional (girar o ignorar el susurro). El prompt acepta `1` o `2`. Si presionas Enter sin escribir nada, se tomará la opción por defecto (1).
- Para salir en cualquier momento, puedes cerrar la terminal o presionar `Ctrl + C`.
- El juego usa entradas de tipo `1`/`2`. Otros valores no son válidos.
- El texto está estilizado con colores y formato (negritas, itálicas) gracias a Rich.
- `narrar(texto, velocidad=0.04, estilo="white")`: imprime el `texto` carácter a carácter con un pequeño retardo para el efecto narrativo. El parámetro `estilo` acepta estilos de Rich (por ejemplo, `"bold red"`, `"italic green"`).
- `bosque()`: escena del bosque con un final directo.
- Bloque `if __name__ == "__main__":` para iniciar el juego llamando a `inicio()` cuando se ejecuta el script.

Rich se utiliza a través de `Console` para imprimir con estilo y `Prompt` para leer opciones.


Ejemplo mínimo para añadir una ruta:

```python
def cueva():
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

Disfruta creando más finales y expandiendo la historia.
=======
# Proyectos-Python
subire proyectos escritos en python
>>>>>>> 54e5d5f87218accc9bd2d0bdaabc65bb0bbf4f3e
>>>>>>> origin/main
