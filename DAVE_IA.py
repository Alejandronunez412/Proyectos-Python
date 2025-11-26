from flask import Flask, request, jsonify
from duckduckgo_search import DDGS
from flask_cors import CORS
from groq import Groq
from datetime import datetime
import sqlite3
import os
from dotenv import load_dotenv
import hashlib
import secrets
import json

app = Flask(__name__)
CORS(app)  # Habilita CORS para permitir peticiones desde tu frontend


# ==================== CONFIGURACIÓN ====================
load_dotenv()

GROQ_API_KEY = os.getenv('GROQ_API_KEY')
if not GROQ_API_KEY:
    raise ValueError("GROQ_API_KEY no configurada en .env")

# Inicializar cliente de Groq
groq_client = Groq(api_key=GROQ_API_KEY)


def init_db():
    """Inicializa la base de datos"""
    conn = sqlite3.connect('wiki.db')
    c = conn.cursor()

    # Tabla de usuarios
    c.execute('''CREATE TABLE IF NOT EXISTS usuarios
                 (id INTEGER PRIMARY KEY, username TEXT UNIQUE,
                  email TEXT UNIQUE, password_hash TEXT,
                  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''')

    # Tabla de artículos
    c.execute('''CREATE TABLE IF NOT EXISTS articulos
                 (id INTEGER PRIMARY KEY, titulo TEXT UNIQUE,
                  contenido TEXT, autor_id INTEGER,
                  estado TEXT DEFAULT 'pendiente',
                  verificado INTEGER DEFAULT 0,
                  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                  FOREIGN KEY(autor_id) REFERENCES usuarios(id))''')

    # Tabla de aportes
    c.execute('''CREATE TABLE IF NOT EXISTS aportes
                 (id INTEGER PRIMARY KEY, articulo_id INTEGER,
                  usuario_id INTEGER, contenido_nuevo TEXT,
                  verificacion_ia TEXT, estado TEXT DEFAULT 'pendiente',
                  confianza REAL DEFAULT 0.0,
                  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                  FOREIGN KEY(articulo_id) REFERENCES articulos(id),
                  FOREIGN KEY(usuario_id) REFERENCES usuarios(id))''')

    conn.commit()
    conn.close()


# ==================== SEGURIDAD ====================
def hash_password(password):
    """Genera hash seguro de contraseña"""
    salt = secrets.token_hex(16)
    password_hash = hashlib.pbkdf2_hmac('sha256',
                                        password.encode(),
                                        salt.encode(), 100000)
    return f"{salt}${password_hash.hex()}"


def verify_password(password, hash_stored):
    """Verifica contraseña contra hash almacenado"""
    try:
        salt, stored_hash = hash_stored.split('$')
        password_hash = hashlib.pbkdf2_hmac('sha256',
                                            password.encode(),
                                            salt.encode(), 100000)
        return password_hash.hex() == stored_hash
    except:
        return False


# ==================== VERIFICACIÓN CON GROQ IA ====================
def verificar_informacion_con_ia(contenido_nuevo, contenido_existente=None):
    """Usa Groq (Llama 3.3) para verificar precisión del contenido"""
    try:
        prompt = f"""Eres un verificador de información experto. Analiza el siguiente contenido y responde SOLO en formato JSON válido.

Contenido a verificar:
{contenido_nuevo}

{"Contenido existente para comparar: " + contenido_existente if contenido_existente else ""}

Responde EXACTAMENTE en este formato JSON (sin texto adicional):
{{"confianza": 0.85, "analisis": "Análisis breve aquí", "recomendacion": "ACEPTAR"}}

Donde:
- confianza: número entre 0 y 1
- analisis: texto breve explicando la evaluación
- recomendacion: debe ser ACEPTAR, REVISAR o RECHAZAR"""

        chat_completion = groq_client.chat.completions.create(
            messages=[
                {
                    "role": "system",
                    "content": "Eres un verificador de hechos experto. Respondes SOLO en formato JSON válido."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            model="llama-3.3-70b-versatile",
            temperature=0.3,
            max_tokens=500
        )

        respuesta_texto = chat_completion.choices[0].message.content.strip()
        
        # Intentar parsear JSON
        try:
            # Limpiar posibles markdown
            if respuesta_texto.startswith('```'):
                respuesta_texto = respuesta_texto.split('```')[1]
                if respuesta_texto.startswith('json'):
                    respuesta_texto = respuesta_texto[4:]
            
            resultado = json.loads(respuesta_texto)
            
            # Validar campos
            if 'confianza' not in resultado:
                resultado['confianza'] = 0.7
            if 'analisis' not in resultado:
                resultado['analisis'] = respuesta_texto[:200]
            if 'recomendacion' not in resultado:
                resultado['recomendacion'] = 'REVISAR'
                
        except json.JSONDecodeError:
            resultado = {
                'confianza': 0.7,
                'analisis': respuesta_texto[:200],
                'recomendacion': 'REVISAR'
            }

        return resultado
        
    except Exception as e:
        print(f"Error en verificación IA: {e}")
        return {
            'confianza': 0.5,
            'analisis': f'Error en verificación: {str(e)}',
            'recomendacion': 'ERROR'
        }


# ==================== BÚSQUEDA EN INTERNET (MÚLTIPLES FUENTES) ====================
def buscar_en_internet(query):
    """
    Busca información en múltiples fuentes de internet y la sintetiza con Groq IA
    """
    try:
        # Buscar en múltiples fuentes con DuckDuckGo
        resultados = []
        
        with DDGS() as ddgs:
            for resultado in ddgs.text(query, max_results=5):
                resultados.append({
                    'titulo': resultado.get('title', ''),
                    'snippet': resultado.get('body', ''),
                    'url': resultado.get('href', '')
                })
        
        if not resultados:
            return {
                'exito': False,
                'error': 'No se encontraron resultados para esta búsqueda'
            }
        
        # Compilar información de todas las fuentes
        informacion_compilada = f"Búsqueda sobre: {query}\n\n"
        fuentes = []
        
        for i, res in enumerate(resultados, 1):
            informacion_compilada += f"Fuente {i}: {res['titulo']}\n"
            informacion_compilada += f"Contenido: {res['snippet']}\n"
            informacion_compilada += f"URL: {res['url']}\n\n"
            fuentes.append({'titulo': res['titulo'], 'url': res['url']})
        
        # Usar Groq para sintetizar toda la información
        prompt = f"""Eres un experto investigador y escritor enciclopédico. Analiza la siguiente información de múltiples fuentes web sobre '{query}' y crea un artículo enciclopédico completo, preciso y bien estructurado en español.

INFORMACIÓN DE {len(resultados)} FUENTES WEB:
{informacion_compilada}

INSTRUCCIONES IMPORTANTES:
1. Sintetiza la información de TODAS las fuentes proporcionadas
2. Mantén solo datos verificables que aparezcan en las fuentes
3. Estructura el artículo con:
   - Introducción clara
   - Desarrollo detallado con subtemas
   - Conclusión o resumen
4. Incluye datos específicos, fechas, cifras cuando estén disponibles en las fuentes
5. Escribe en un tono enciclopédico profesional (estilo Wikipedia)
6. Mínimo 400 palabras
7. NO inventes información que no esté en las fuentes
8. Si hay información contradictoria entre fuentes, menciona ambas perspectivas
9. Usa párrafos bien estructurados

Genera el artículo completo ahora en español:"""

        chat_completion = groq_client.chat.completions.create(
            messages=[
                {
                    "role": "system",
                    "content": "Eres un escritor experto de enciclopedias. Escribes artículos informativos, precisos y bien estructurados en español."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            model="llama-3.3-70b-versatile",
            temperature=0.7,
            max_tokens=2500
        )
        
        articulo = chat_completion.choices[0].message.content
        
        return {
            'exito': True,
            'titulo': query.title(),
            'contenido': articulo,
            'fuente': f'Múltiples fuentes web ({len(resultados)} artículos) + IA Groq',
            'fuentes_detalle': fuentes,
            'num_fuentes': len(resultados)
        }
        
    except Exception as e:
        print(f"Error en búsqueda: {e}")
        return {
            'exito': False,
            'error': f'Error en búsqueda: {str(e)}'
        }


# ==================== ENDPOINT DE BÚSQUEDA SIMPLE ====================
@app.route('/search', methods=['POST'])
def search():
    """Endpoint simple que devuelve resultados crudos de DuckDuckGo"""
    data = request.get_json()
    query = data.get('query')

    if not query:
        return jsonify({'error': 'No se proporcionó una consulta'}), 400

    try:
        with DDGS() as ddgs:
            results = list(ddgs.text(query, max_results=10))
        return jsonify(results)
    except Exception as e:
        print(f"Ocurrió un error: {e}")
        return jsonify({'error': str(e)}), 500


# ==================== RUTAS - AUTENTICACIÓN ====================
@app.route('/api/registro', methods=['POST'])
def registro():
    """Registra nuevo usuario"""
    data = request.json
    username = data.get('username', '').strip()
    email = data.get('email', '').strip()
    password = data.get('password', '')

    if not all([username, email, password]) or len(password) < 8:
        return jsonify({'error': 'Datos inválidos o contraseña muy corta'}), 400

    try:
        conn = sqlite3.connect('wiki.db')
        c = conn.cursor()
        password_hash = hash_password(password)
        c.execute('INSERT INTO usuarios (username, email, password_hash) VALUES (?, ?, ?)',
                  (username, email, password_hash))
        conn.commit()
        conn.close()
        return jsonify({'mensaje': 'Usuario registrado exitosamente'}), 201
    except sqlite3.IntegrityError:
        return jsonify({'error': 'Usuario o email ya existe'}), 409


@app.route('/api/login', methods=['POST'])
def login():
    """Autentica usuario"""
    data = request.json
    username = data.get('username', '')
    password = data.get('password', '')

    conn = sqlite3.connect('wiki.db')
    c = conn.cursor()
    c.execute('SELECT id, password_hash FROM usuarios WHERE username = ?', (username,))
    usuario = c.fetchone()
    conn.close()

    if usuario and verify_password(password, usuario[1]):
        return jsonify({'id': usuario[0], 'username': username, 'token': secrets.token_hex(32)}), 200
    return jsonify({'error': 'Credenciales inválidas'}), 401


# ==================== RUTAS - ARTÍCULOS ====================
@app.route('/api/articulos', methods=['GET'])
def obtener_articulos():
    """Obtiene todos los artículos verificados"""
    conn = sqlite3.connect('wiki.db')
    c = conn.cursor()
    c.execute('''SELECT id, titulo, contenido, autor_id, created_at 
                 FROM articulos WHERE verificado = 1 ORDER BY created_at DESC''')
    articulos = c.fetchall()
    conn.close()

    return jsonify([{
        'id': a[0], 'titulo': a[1], 'contenido': a[2][:200],
        'autor_id': a[3], 'fecha': a[4]
    } for a in articulos])


@app.route('/api/articulos/<int:id>', methods=['GET'])
def obtener_articulo(id):
    """Obtiene un artículo completo"""
    conn = sqlite3.connect('wiki.db')
    c = conn.cursor()
    c.execute('SELECT * FROM articulos WHERE id = ? AND verificado = 1', (id,))
    articulo = c.fetchone()
    conn.close()
    
    if not articulo:
        return jsonify({'error': 'Artículo no encontrado'}), 404
    
    return jsonify({
        'id': articulo[0], 'titulo': articulo[1], 'contenido': articulo[2],
        'autor_id': articulo[3], 'created_at': articulo[6]
    })


@app.route('/api/articulos/crear', methods=['POST'])
def crear_articulo():
    """Permite crear artículos completos"""
    data = request.json
    titulo = data.get('titulo', '').strip()
    contenido = data.get('contenido', '').strip()
    usuario_id = data.get('usuario_id')

    if not all([titulo, contenido, usuario_id]):
        return jsonify({'error': 'Datos incompletos'}), 400

    verificacion = verificar_informacion_con_ia(contenido)

    try:
        conn = sqlite3.connect('wiki.db')
        c = conn.cursor()

        verificado = 1 if verificacion['confianza'] > 0.7 else 0
        estado = 'publicado' if verificado else 'pendiente'

        c.execute('''INSERT INTO articulos (titulo, contenido, autor_id, verificado, estado)
                     VALUES (?, ?, ?, ?, ?)''',
                  (titulo, contenido, usuario_id, verificado, estado))

        articulo_id = c.lastrowid
        conn.commit()
        conn.close()

        return jsonify({
            'id': articulo_id,
            'verificacion': verificacion,
            'estado': estado,
            'mensaje': 'Artículo publicado' if verificado else 'Artículo enviado para revisión'
        }), 201
    except sqlite3.IntegrityError:
        return jsonify({'error': 'Ya existe un artículo con ese título'}), 409


@app.route('/api/buscar-internet', methods=['POST'])
def buscar_internet_route():
    """Busca información en internet y la verifica con IA"""
    data = request.json
    query = data.get('query', '').strip()
    
    if not query:
        return jsonify({'error': 'Debe proporcionar un término de búsqueda'}), 400
    
    resultado = buscar_en_internet(query)
    return jsonify(resultado)


# ==================== RUTAS - APORTES ====================
@app.route('/api/aportes', methods=['POST'])
def crear_aporte():
    """Crea un aporte y lo verifica con IA"""
    data = request.json
    articulo_id = data.get('articulo_id')
    usuario_id = data.get('usuario_id')
    contenido_nuevo = data.get('contenido', '').strip()

    if not all([articulo_id, usuario_id, contenido_nuevo]):
        return jsonify({'error': 'Datos incompletos'}), 400

    conn = sqlite3.connect('wiki.db')
    c = conn.cursor()
    c.execute('SELECT contenido FROM articulos WHERE id = ?', (articulo_id,))
    articulo = c.fetchone()

    if not articulo:
        return jsonify({'error': 'Artículo no existe'}), 404

    verificacion = verificar_informacion_con_ia(contenido_nuevo, articulo[0])

    c.execute('''INSERT INTO aportes (articulo_id, usuario_id, contenido_nuevo,
                 verificacion_ia, confianza, estado)
                 VALUES (?, ?, ?, ?, ?, ?)''',
              (articulo_id, usuario_id, contenido_nuevo,
               str(verificacion['analisis']), verificacion['confianza'], 'pendiente'))

    aporte_id = c.lastrowid
    conn.commit()
    conn.close()

    return jsonify({
        'id': aporte_id,
        'verificacion': verificacion,
        'mensaje': 'Aporte enviado para revisión'
    }), 201


# ==================== INICIO ====================
if __name__ == '__main__':
    print("🤖 Iniciando DAVE IA con Groq (Llama 3.3)...")
    init_db()
    print("✅ Base de datos inicializada")
    print("🚀 Servidor corriendo en http://localhost:5000")
    app.run(debug=True, host='localhost', port=5000)