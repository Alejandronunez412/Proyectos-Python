// Configuración
const API_URL = 'http://127.0.0.1:5000/api';
let usuarioActual = null;

// ==================== INICIALIZACIÓN ====================
document.addEventListener('DOMContentLoaded', () => {
    const searchButton = document.getElementById('searchButton');
    const searchInput = document.getElementById('searchInput');
    
    // Búsqueda web
    searchButton.addEventListener('click', buscarEnWeb);
    searchInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') buscarEnWeb();
    });
    
    // Cargar artículos
    cargarArticulos();
    actualizarUI();
});

// ==================== NAVEGACIÓN ====================
function mostrarSeccion(seccion) {
    document.getElementById('seccionBusqueda').style.display = 
        seccion === 'busqueda' ? 'block' : 'none';
    document.getElementById('seccionArticulos').style.display = 
        seccion === 'articulos' ? 'block' : 'none';
    
    if (seccion === 'articulos') {
        cargarArticulos();
    }
}

// ==================== BÚSQUEDA WEB ====================
async function buscarEnWeb() {
    const searchInput = document.getElementById('searchInput');
    const resultsContainer = document.getElementById('resultsContainer');
    const query = searchInput.value.trim();
    
    if (!query) {
        resultsContainer.innerHTML = '<p>Por favor, ingresa un término de búsqueda.</p>';
        return;
    }

    resultsContainer.innerHTML = '<div class="loader"></div><p style="text-align:center;">Buscando en internet y verificando con IA...</p>';

    try {
        const response = await fetch(`${API_URL}/buscar-internet`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ query: query }),
        });

        if (!response.ok) {
            throw new Error(`Error del servidor: ${response.statusText}`);
        }

        const data = await response.json();
        
        if (data.exito) {
            displaySearchResults(data);
        } else {
            resultsContainer.innerHTML = `<p style="color: #ef4444;">${data.error}</p>`;
        }

    } catch (error) {
        console.error('Error al realizar la búsqueda:', error);
        resultsContainer.innerHTML = '<p style="color: #ef4444;">Ocurrió un error al conectar con el servidor de búsqueda.</p>';
    }
}

function displaySearchResults(data) {
    const resultsContainer = document.getElementById('resultsContainer');
    
    if (!data.fuentes_detalle || data.fuentes_detalle.length === 0) {
        resultsContainer.innerHTML = '<p>No se encontraron resultados para tu búsqueda.</p>';
        return;
    }

    const fuentesHTML = data.fuentes_detalle.map((f, i) => 
        `<li style="margin-bottom: 0.5rem;">
            <a href="${f.url}" target="_blank" style="color: #60a5fa; text-decoration: none;">
                ${i + 1}. ${f.titulo}
            </a>
        </li>`
    ).join('');
    
    resultsContainer.innerHTML = `
        <div class="verificacion-box">
            <h4>✅ Información Recopilada de ${data.num_fuentes} Fuentes</h4>
            <p><strong>Título:</strong> ${data.titulo}</p>
            
            <details style="margin: 1rem 0;">
                <summary style="cursor: pointer; color: #60a5fa; font-weight: bold;">
                    📚 Ver Fuentes Consultadas (${data.num_fuentes})
                </summary>
                <ul style="margin-top: 1rem; line-height: 1.8;">
                    ${fuentesHTML}
                </ul>
            </details>
            
            <p><strong>Artículo Sintetizado por IA:</strong></p>
            <div style="max-height: 400px; overflow-y: auto; background: rgba(0,0,0,0.3); padding: 1rem; border-radius: 4px; margin-top: 0.5rem; line-height: 1.8;">
                ${data.contenido.replace(/\n/g, '<br>')}
            </div>
            
            ${usuarioActual ? `
                <button onclick='guardarArticuloWeb(${JSON.stringify(data.titulo)}, ${JSON.stringify(data.contenido)})' 
                        class="btn-primary" style="width: 100%; margin-top: 1rem;">
                    💾 Guardar como Artículo Verificado
                </button>
            ` : `
                <p style="text-align: center; margin-top: 1rem; color: #94a3b8;">
                    <a href="#" onclick="abrirModalLogin(); return false;" style="color: #60a5fa;">Inicia sesión</a> 
                    para guardar este artículo
                </p>
            `}
        </div>
    `;
}

async function guardarArticuloWeb(titulo, contenido) {
    if (!usuarioActual) {
        mostrarAlerta('Debes iniciar sesión para guardar artículos', 'error');
        return;
    }

    try {
        const res = await fetch(`${API_URL}/articulos/crear`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                titulo: titulo,
                contenido: contenido,
                usuario_id: usuarioActual.id
            })
        });

        const data = await res.json();

        if (res.ok) {
            mostrarAlerta('¡Artículo guardado exitosamente!', 'exito');
            setTimeout(() => {
                mostrarSeccion('articulos');
            }, 2000);
        } else {
            mostrarAlerta(data.error || 'Error al guardar artículo', 'error');
        }
    } catch (error) {
        mostrarAlerta('Error de conexión', 'error');
    }
}

// ==================== ARTÍCULOS ====================
async function cargarArticulos() {
    try {
        const res = await fetch(`${API_URL}/articulos`);
        const articulos = await res.json();
        mostrarArticulos(articulos);
    } catch (error) {
        console.error('Error al cargar artículos:', error);
    }
}

function mostrarArticulos(articulos) {
    const grid = document.getElementById('articulos');
    
    if (articulos.length === 0) {
        grid.innerHTML = '<p style="grid-column: 1/-1; text-align: center; color: #94a3b8;">No hay artículos disponibles aún. ¡Busca en internet y crea el primero!</p>';
        return;
    }

    grid.innerHTML = articulos.map(art => `
        <div class="articulo-card" onclick="verArticulo(${art.id})">
            <h3>${art.titulo}</h3>
            <p>${art.contenido}...</p>
            <div class="fecha">📅 ${new Date(art.fecha).toLocaleDateString('es-ES')}</div>
        </div>
    `).join('');
}

async function verArticulo(id) {
    try {
        const res = await fetch(`${API_URL}/articulos/${id}`);
        const articulo = await res.json();
        
        const resultsContainer = document.getElementById('resultsContainer');
        resultsContainer.innerHTML = `
            <div class="verificacion-box">
                <h4>${articulo.titulo}</h4>
                <div style="line-height: 1.8; margin-top: 1rem;">
                    ${articulo.contenido.replace(/\n/g, '<br>')}
                </div>
                <p style="margin-top: 1rem; color: #94a3b8;">
                    📅 Creado: ${new Date(articulo.created_at).toLocaleDateString('es-ES')}
                </p>
            </div>
        `;
        
        mostrarSeccion('busqueda');
    } catch (error) {
        mostrarAlerta('Error al cargar artículo', 'error');
    }
}

// ==================== CREAR ARTÍCULO ====================
async function crearArticulo(e) {
    e.preventDefault();
    
    if (!usuarioActual) {
        mostrarAlerta('Debes iniciar sesión', 'error');
        return;
    }

    const titulo = document.getElementById('crearTitulo').value.trim();
    const contenido = document.getElementById('crearContenido').value.trim();

    try {
        const res = await fetch(`${API_URL}/articulos/crear`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                titulo,
                contenido,
                usuario_id: usuarioActual.id
            })
        });

        const data = await res.json();

        if (res.ok) {
            const verificacionDiv = document.getElementById('verificacionCrear');
            const confianza = data.verificacion.confianza;
            const porcentaje = (confianza * 100).toFixed(0);
            
            verificacionDiv.innerHTML = `
                <div class="verificacion-box">
                    <h4>🤖 Verificación de IA</h4>
                    <p style="color: ${confianza > 0.7 ? '#10b981' : confianza > 0.4 ? '#f59e0b' : '#ef4444'};">
                        Nivel de confianza: ${porcentaje}%
                    </p>
                    <p><strong>Estado:</strong> ${data.estado}</p>
                    <p><strong>Análisis:</strong> ${data.verificacion.analisis}</p>
                </div>
            `;
            
            mostrarAlerta(data.mensaje, 'exito');
            
            setTimeout(() => {
                cerrarModal('modalCrear');
                document.getElementById('crearTitulo').value = '';
                document.getElementById('crearContenido').value = '';
                verificacionDiv.innerHTML = '';
                cargarArticulos();
                mostrarSeccion('articulos');
            }, 3000);
        } else {
            mostrarAlerta(data.error || 'Error al crear artículo', 'error');
        }
    } catch (error) {
        mostrarAlerta('Error de conexión', 'error');
    }
}

// ==================== AUTENTICACIÓN ====================
async function login(e) {
    e.preventDefault();
    const username = document.getElementById('loginUsername').value;
    const password = document.getElementById('loginPassword').value;

    try {
        const res = await fetch(`${API_URL}/login`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ username, password })
        });

        if (res.ok) {
            const data = await res.json();
            usuarioActual = data;
            mostrarAlerta('¡Sesión iniciada correctamente!', 'exito');
            cerrarModal('modalLogin');
            actualizarUI();
        } else {
            mostrarAlerta('Usuario o contraseña inválidos', 'error');
        }
    } catch (error) {
        mostrarAlerta('Error de conexión', 'error');
    }
}

async function registro(e) {
    e.preventDefault();
    const username = document.getElementById('regUsername').value;
    const email = document.getElementById('regEmail').value;
    const password = document.getElementById('regPassword').value;

    try {
        const res = await fetch(`${API_URL}/registro`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ username, email, password })
        });

        if (res.ok) {
            mostrarAlerta('¡Registro exitoso! Ahora puedes iniciar sesión', 'exito');
            cerrarModal('modalRegistro');
            document.getElementById('regUsername').value = '';
            document.getElementById('regEmail').value = '';
            document.getElementById('regPassword').value = '';
        } else {
            const data = await res.json();
            mostrarAlerta(data.error || 'Error en el registro', 'error');
        }
    } catch (error) {
        mostrarAlerta('Error de conexión', 'error');
    }
}

function cerrarSesion() {
    usuarioActual = null;
    mostrarAlerta('Sesión cerrada', 'exito');
    actualizarUI();
}

function actualizarUI() {
    const btnCerrar = document.getElementById('btnCerrar');
    const btnCrear = document.getElementById('btnCrear');
    if (usuarioActual) {
        btnCerrar.style.display = 'block';
        btnCrear.style.display = 'block';
    } else {
        btnCerrar.style.display = 'none';
        btnCrear.style.display = 'none';
    }
}

// ==================== MODALES ====================
function abrirModal(id) {
    document.getElementById(id).classList.add('activo');
}

function cerrarModal(id) {
    document.getElementById(id).classList.remove('activo');
}

function abrirModalLogin() {
    abrirModal('modalLogin');
}

function abrirModalRegistro() {
    abrirModal('modalRegistro');
}

function abrirModalCrear() {
    if (!usuarioActual) {
        mostrarAlerta('Debes iniciar sesión para crear artículos', 'error');
        return;
    }
    abrirModal('modalCrear');
}

// ==================== UTILIDADES ====================
function mostrarAlerta(mensaje, tipo) {
    const alerta = document.getElementById('alerta');
    alerta.textContent = mensaje;
    alerta.className = `alerta activa alerta-${tipo}`;
    setTimeout(() => alerta.classList.remove('activa'), 4000);
}