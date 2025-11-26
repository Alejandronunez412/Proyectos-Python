from rich.console import Console
from rich.prompt import Prompt
from rich.progress import Progress
import time
import random

console = Console()

# Inventario del jugador
inventario = []
cordura = 100  # Nivel inicial de cordura

# Función para imprimir con efecto de "máquina de escribir"
def narrar(texto, velocidad=0.04, estilo="white"):
    for char in texto:
        console.print(char, end="", style=estilo, highlight=False, soft_wrap=True)
        time.sleep(velocidad)
    console.print("", style=estilo)

# Mostrar barra de cordura
def mostrar_cordura():
    global cordura
    console.print("\n[bold cyan]Cordura restante:[/bold cyan]")
    with Progress(transient=True) as progress:
        tarea = progress.add_task("Cordura", total=100)
        progress.update(tarea, completed=cordura)
        time.sleep(0.5)

# Reducir cordura
def perder_cordura(minimo=10, maximo=30):
    global cordura
    perdida = random.randint(minimo, maximo)
    cordura -= perdida
    narrar(f"Sientes que tu mente se resquebraja... (-{perdida} cordura)", estilo="dim red")
    mostrar_cordura()
    if cordura <= 0:
        narrar("El terror consume tu mente. Caíste al vacío de la locura.", estilo="bold red")
        narrar("Final malo: perdiste la cordura.", estilo="bold red")
        exit()

# Posibles susurros aleatorios
def susurro():
    mensajes = [
        "Escuchas un susurro detrás de ti... pero no hay nadie.",
        "El aire se vuelve gélido, como si algo pasara a tu lado.",
        "Sientes que alguien te observa desde las sombras..."
    ]
    narrar(random.choice(mensajes), estilo="dim red")
    perder_cordura()

# Inicio del juego
def inicio():
    console.rule("[bold red]La Aventura Comienza")
    narrar("Te despiertas en un bosque oscuro. Frente a ti, un castillo en ruinas te observa bajo la luna llena...", estilo="italic white")
    narrar("Sientes un escalofrío recorriéndote la espalda. ¿Qué harás?", estilo="bold yellow")
    narrar("1) Entrar al castillo")
    narrar("2) Huir hacia el bosque")
    mostrar_cordura()

    eleccion = Prompt.ask("Decide", choices=["1", "2"], default="1")
    if eleccion == "1":
        castillo()
    elif eleccion == "2":
        bosque()


def castillo():
    console.rule("[bold magenta]El Castillo")
    narrar("Cruzas la puerta del castillo. El aire huele a moho y sangre seca...", estilo="bold white")
    susurro()
    narrar("Ves dos caminos: uno hacia las mazmorras y otro hacia la torre.", estilo="bold yellow")
    narrar("1) Bajar a las mazmorras")
    narrar("2) Subir a la torre")

    eleccion = Prompt.ask("Decide", choices=["1", "2"] , default="1")
    if eleccion == "1":
        mazmorra()
    elif eleccion == "2":
        torre()


def bosque():
    console.rule("[bold green]El Bosque")
    narrar("Corres hacia el bosque, pero cuanto más corres, más denso se vuelve. Los árboles parecen moverse...", estilo="italic green")
    susurro()
    narrar("Encuentras un objeto brillante en el suelo. Es un amuleto antiguo.", estilo="cyan")
    inventario.append("amuleto")
    narrar("Lo guardas en tu bolsa.", estilo="green")
    narrar("El bosque se retuerce hasta empujarte de regreso al castillo.", estilo="bold red")
    castillo()


def mazmorra():
    console.rule("[bold blue]Mazmorras")
    narrar("Bajas unas escaleras húmedas y frías. Escuchas gritos lejanos...", estilo="bold white")
    susurro()
    narrar("Encuentras una llave oxidada sobre un esqueleto.", estilo="cyan")
    inventario.append("llave")

    narrar("Delante de ti hay una puerta sellada. ¿Quieres usar la llave?", estilo="bold yellow")
    eleccion = Prompt.ask("Decide", choices=["si", "no"] , default="si")
    if eleccion == "si":
        cementerio()
    else:
        perder_cordura(20, 40)
        narrar("Decides no abrir la puerta... pero la oscuridad te traga.", estilo="bold red")
        narrar("Final malo: te consumió el miedo.", estilo="bold red")


def torre():
    console.rule("[bold purple]La Torre")
    narrar("Subes la torre maldita. Cada escalón cruje como huesos rotos...", estilo="italic white")
    susurro()
    narrar("En la cima ves un altar con un libro cubierto de sangre.", estilo="red")

    eleccion = Prompt.ask("Leer el libro?", choices=["si", "no"] , default="no")
    if eleccion == "si":
        perder_cordura(30, 50)
        narrar("El libro susurra tu nombre... y tu alma se desvanece.", estilo="bold red")
        narrar("Final malo: fuiste devorado por el conocimiento prohibido.", estilo="bold red")
    else:
        narrar("Ignoras el libro y bajas apresurado...", estilo="yellow")
        cementerio()


def cementerio():
    console.rule("[bold grey]El Cementerio")
    narrar("Llegas a un cementerio oculto. Decenas de tumbas abiertas te rodean...", estilo="italic white")
    susurro()
    if "amuleto" in inventario:
        narrar("El amuleto en tu bolsa brilla y espanta a los espectros.", estilo="green")
        narrar("Final bueno: logras escapar del castillo con vida.", estilo="bold green")
    else:
        perder_cordura(40, 60)
        narrar("Sin protección, los muertos salen de sus tumbas y te arrastran con ellos.", estilo="red")
        narrar("Final malo: reposas eternamente en el cementerio.", estilo="bold red")


if __name__ == "__main__":
    inicio()

	
