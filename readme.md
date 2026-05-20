# 🧮 Calculadora de Transformadas de Laplace

> **Herramienta de escritorio** para calcular transformadas directas e inversas de Laplace y resolver ecuaciones diferenciales ordinarias, con visualización matemática renderizada por MathJax.

---

## 📋 Tabla de Contenidos

- [Vista General](#vista-general)
- [Arquitectura del Sistema](#arquitectura-del-sistema)
- [Estructura de Archivos](#estructura-de-archivos)
- [Flujo de Datos](#flujo-de-datos)
- [Módulos en Detalle](#módulos-en-detalle)
- [Casos de Uso Soportados](#casos-de-uso-soportados)
- [Sintaxis de Entrada](#sintaxis-de-entrada)
- [Instalación y Ejecución](#instalación-y-ejecución)
- [Decisiones de Diseño](#decisiones-de-diseño)

---

## Vista General

```
┌─────────────────────────────────────────────────────────────────┐
│                                                                 │
│   Usuario escribe: sin(3*t)   →   F(s) = 3 / (s² + 9)         │
│                                                                 │
│   Usuario escribe: y'' + 3y' + 2y = 0; y(0)=1; y'(0)=5        │
│                     →   y(t) = 6e⁻ᵗ - 5e⁻²ᵗ                   │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

La aplicación recibe una expresión matemática en texto plano, la analiza con **SymPy**, genera HTML con notación LaTeX paso a paso y lo renderiza en un widget **QWebEngineView** con **MathJax**.

---

## Arquitectura del Sistema

La app sigue el patrón **MVC (Modelo - Vista - Controlador)** clásico, separando completamente la lógica matemática de la interfaz gráfica.

```
┌──────────────────────────────────────────────────────────────────────┐
│                        PATRÓN MVC                                    │
│                                                                      │
│  ┌─────────────┐    eventos    ┌──────────────────┐                  │
│  │             │ ─────────── ▶ │                  │                  │
│  │    VISTA    │               │  CONTROLADOR     │                  │
│  │             │ ◀ ─────────── │                  │                  │
│  │ interfaz_   │   HTML result │  main.py         │                  │
│  │ grafica.py  │               │  Controlador-    │                  │
│  │             │               │  Calculadora     │                  │
│  └─────────────┘               └────────┬─────────┘                  │
│                                         │ llama                      │
│                                         ▼                            │
│                                ┌────────────────┐                    │
│                                │    MODELO      │                    │
│                                │  solve_math.py │                    │
│                                │  SolverLaplace │                    │
│                                └────────────────┘                    │
│                                                                      │
│  ┌─────────────────────────────────────────────────────────────┐    │
│  │  UTILIDADES COMPARTIDAS: view/utilidades_html.py            │    │
│  │  generar_html()  ·  PLANTILLA_BASE  ·  GUIA_ERRORES_HTML    │    │
│  └─────────────────────────────────────────────────────────────┘    │
└──────────────────────────────────────────────────────────────────────┘
```

### ¿Por qué MVC?

| Principio | Aplicación en este proyecto |
|---|---|
| **Separación de responsabilidades** | `solve_math.py` no sabe nada de botones ni colores; `interfaz_grafica.py` no hace ningún cálculo |
| **Testabilidad** | El modelo puede ejecutarse y testearse solo, sin GUI |
| **Mantenibilidad** | Cambiar el motor matemático (ej: reemplazar SymPy) no toca la UI |
| **Extensibilidad** | Agregar una vista web o CLI es trivial; el modelo no cambia |

---

## Estructura de Archivos

```
laplace_app/
│
├── main.py                        ← 🎮 Punto de entrada + Controlador
│
├── model/
│   └── solve_math.py              ← 🧠 Motor matemático (SymPy)
│
└── view/
    ├── interfaz_grafica.py        ← 🖼️  Interfaz PyQt6 completa
    └── utilidades_html.py         ← 🎨 Plantillas HTML/MathJax
```

> **Regla de dependencias:** Las flechas de importación solo van en una dirección:
> `main.py` importa de `model/` y `view/`. Ningún módulo de `model/` importa de `view/`.

---

## Flujo de Datos

Aquí se muestra exactamente qué ocurre desde que el usuario presiona **"Calcular"** hasta que ve el resultado:

```
Usuario presiona "Calcular"
         │
         ▼
┌─────────────────────────┐
│  InterfazCalculadora    │  obtener_texto() → "sin(3*t)"
│  (interfaz_grafica.py)  │
└────────────┬────────────┘
             │ señal clicked
             ▼
┌─────────────────────────┐
│  ControladorCalculadora │  ejecutar_calculo()
│  (main.py)              │
└────────────┬────────────┘
             │ llama a
             ▼
┌─────────────────────────┐
│  SolverLaplace          │  procesar_expresion("sin(3*t)")
│  (solve_math.py)        │
│                         │
│  1. ¿Tiene '='?  → EDO  │
│  2. ¿Tiene 's'?  → Inv  │
│  3. ¿Add?        → Lin  │
│  4. sin/cos/exp  → Dir  │
│                         │
│  → ("directa", html)    │
└────────────┬────────────┘
             │ retorna tupla (estado, html_str)
             ▼
┌─────────────────────────┐
│  ControladorCalculadora │  view.mostrar_html(html_str)
└────────────┬────────────┘
             │
             ▼
┌─────────────────────────┐
│  InterfazCalculadora    │  _render_web(contenido)
│  → QWebEngineView       │  → setHtml(PLANTILLA_WEB + contenido)
│  → MathJax renderiza    │  → usuario ve fórmulas bonitas ✓
└─────────────────────────┘
```

---

## Módulos en Detalle

### 🧠 `model/solve_math.py` — El Cerebro

Contiene la clase `SolverLaplace`. Es el único módulo que hace matemáticas.

#### Árbol de decisión interno

```
procesar_expresion(texto)
│
├── ¿Contiene '='? ──────────────────────────────▶ resolver_edo()
│
└── ¿No tiene '='?
    │
    ├── ¿Tiene símbolo 's'? ─────────────────────▶ Aviso: es Inversa
    │
    └── ¿Solo tiene 't'?
        │
        ├── ¿es Number / literal? ───────────────▶ CASO 1: Constante
        │     → F(s) = c/s
        │
        ├── ¿es sp.Add? ──────────────────────────▶ CASO 2: Linealidad
        │     → L{f±g} = L{f} ± L{g}
        │
        ├── ¿es sp.Mul con exp()? ──────────────▶ CASO 3: 1er Teorema
        │     → L{eᵃᵗ f(t)} = F(s-a)
        │
        └── Resto ────────────────────────────────▶ CASO 4: Elementales
              sin, cos, sinh, cosh, tⁿ
```

#### Notación LaTeX consistente

Para garantizar que la `L` de Laplace siempre se vea igual, se define una constante global y dos funciones helper al inicio del archivo:

```python
# ← Una sola línea controla el aspecto de la L en toda la app
L_TEX = r'\mathscr{L}'

def _L(expr: str) -> str:
    """  L{expr}   """
    return rf"{L_TEX}\{{{expr}\}}"

def _Linv(expr: str) -> str:
    """  L⁻¹{expr}  """
    return rf"{L_TEX}^{{-1}}\left\{{ {expr} \right\}}"
```

> **¿Por qué esto soluciona el bug?** Antes, cada `paso.append(...)` en el código
> escribía `\\mathcal{{L}}` directamente en el string. Si en algún lugar se olvidaba
> el doble escape o se usaba `\mathcal L` sin llaves, MathJax lo renderizaba
> diferente. Ahora **hay una sola fuente de verdad** para la notación.

#### Resolución de EDOs — Pipeline algebraico

```
Texto: "y'' + 3*y' + 2*y = 0; y(0)=1; y'(0)=5"
│
├── Split por ';'  →  edo="y'' + 3*y' + 2*y = 0"  +  CIs
│
├── Reemplazar y'', y' por símbolos intermedios
│   y'' → y_double_prime,   y' → y_prime
│
├── sympify() con contexto extendido
│
├── Sustituir teoremas de derivada:
│   y_double_prime → s²Y - sy(0) - y'(0)
│   y_prime        → sY  - y(0)
│   y              → Y
│
├── sp.solve(ecuación, Y)  →  Y(s) algebraico
│
├── sp.apart(Y, s)         →  Fracciones Parciales
│
└── sp.inverse_laplace_transform(Y, s, t)  →  y(t) ✓
```

---

### 🖼️ `view/interfaz_grafica.py` — La Cara

Construida con **PyQt6**. Contiene dos clases:

#### `PanelEjemplosLateral` (QFrame)

Panel lateral deslizable que muestra la guía de sintaxis. Se activa con el botón `☰`.

```
┌─────────────────┐ ┌──────────────────┐
│  Calculadora    │ │ 📐 Guía Sintaxis  │
│                 │ │                  │
│  [entrada]      │ │ TRANSFORMADAS    │
│  [teclado]      │ │  Constante → 5   │
│  [Calcular]     │ │  Potencia  → t**3│
│  [resultado]    │ │                  │
│  [historial]    │ │ ECUACIONES DIFS  │
│                 │ │  1er orden → ... │
└─────────────────┘ └──────────────────┘
  430 px              +270 px = 700 px
```

Cada ejemplo en el panel es un botón que al hacer clic **inserta directamente** la fórmula en el campo de entrada.

#### `InterfazCalculadora` (QWidget)

La ventana principal. Responsabilidades:

| Método | Qué hace |
|---|---|
| `init_ui()` | Construye todos los widgets y layouts |
| `_aplicar_tema()` | Aplica el stylesheet completo de Windows 11 Dark |
| `_render_web(contenido)` | Inyecta HTML en QWebEngineView con la plantilla base |
| `mostrar_html(html_str)` | Extrae `<body>` del HTML recibido y lo pasa a `_render_web` |
| `toggle_ejemplos_lateral()` | Expande/colapsa el panel lateral animando el ancho de la ventana |
| `animar_calculo()` | Animación fade-in (opacidad 0→1) al mostrar nuevo resultado |
| `insertar(val)` | Inserta texto en el QLineEdit del teclado virtual |
| `obtener_texto()` | Lee y limpia el texto del campo de entrada |

#### El Teclado Virtual

Los botones están clasificados en 4 categorías con colores distintos:

```
  Categoría    Color         Ejemplos
  ─────────    ───────────   ────────────────────
  edo          #2d2d2d       y,  y',  y'',  =,  ;
  var          #2d2d2d       t,  s,  π,  α,  s²
  func         #2d2d2d       sin, cos, eⁿ, sinh, cosh
  op           #202020       0-9, +, -, *, /, (, )
```

---

### 🎨 `view/utilidades_html.py` — Las Plantillas

Módulo de plantillas puras, sin lógica.

```python
PLANTILLA_BASE          # HTML completo con MathJax 2.7 (CDN)
GUIA_ERRORES_HTML       # Tabla de errores de sintaxis comunes
generar_html(contenido) # Función: inserta contenido en PLANTILLA_BASE
```

> **Nota:** `PLANTILLA_BASE` usa fondo blanco (`#ffffff`) porque es la plantilla
> genérica de utilidades. La plantilla con tema oscuro (`PLANTILLA_WEB`) vive en
> `interfaz_grafica.py` y usa las variables del tema activo.

---

### 🎮 `main.py` — El Director de Orquesta

Contiene `ControladorCalculadora`. Su único trabajo es **conectar** Vista y Modelo:

```python
class ControladorCalculadora:
    def __init__(self):
        self.view   = InterfazCalculadora()   # instancia la Vista
        self.modelo = SolverLaplace()         # instancia el Modelo

        # Conecta señales de la Vista con métodos del Controlador
        self.view.btn_ir.clicked.connect(self.ejecutar_calculo)
        self.view.entry.returnPressed.connect(self.ejecutar_calculo)
        self.view.historial_list.itemClicked.connect(self.cargar_historial)

    def ejecutar_calculo(self):
        texto = self.view.obtener_texto()          # 1. Lee entrada
        estado, html = self.modelo.procesar_expresion(texto)  # 2. Calcula
        self.view.mostrar_html(html)               # 3. Muestra resultado
        # + gestión de historial
```

---

## Casos de Uso Soportados

### Transformadas Directas `L{f(t)}`

| Tipo | Ejemplo de entrada | Resultado |
|---|---|---|
| Constante | `7` | `7/s` |
| Potencia | `t**4` | `24/s⁵` |
| Exponencial | `exp(-2*t)` | `1/(s+2)` |
| Seno | `sin(3*t)` | `3/(s²+9)` |
| Coseno | `cos(3*t)` | `s/(s²+9)` |
| Seno hiperbólico | `sinh(2*t)` | `2/(s²-4)` |
| Coseno hiperbólico | `cosh(2*t)` | `s/(s²-4)` |
| Linealidad | `t**2 + sin(t)` | Aplica L a cada término |
| 1er Teo. Traslación | `exp(-t)*cos(2*t)` | Desplaza s→s+1 |

### Ecuaciones Diferenciales

| Orden | Ejemplo de entrada |
|---|---|
| 1er orden | `y' + 2*y = 0; y(0)=1` |
| 2do orden homogénea | `y'' + 3*y' + 2*y = 0; y(0)=1; y'(0)=5` |
| 2do orden forzada | `y'' + 4*y = cos(t); y(0)=0; y'(0)=0` |
| Hasta orden 10 | Soportado vía sustitución algebraica |

---

## Sintaxis de Entrada

```
✅ CORRECTO              ❌ INCORRECTO
─────────────────────   ─────────────────────
t**2                    t^2   o   t2
2*t                     2t
exp(-3*t)               e^(-3t)
sin(2*t)                sin2t
y'' + 2*y = 0           y" + 2y = 0
y(0)=1; y'(0)=0         y(0)=1, y'(0)=0
```

**Separador de condiciones iniciales:** siempre `;` (punto y coma)

---

## Instalación y Ejecución

### Requisitos

```bash
Python >= 3.9
PyQt6
PyQt6-WebEngine
sympy
```

### Instalación

```bash
# Clonar el repositorio
git clone <url-del-repo>
cd laplace_app

# Instalar dependencias
pip install PyQt6 PyQt6-WebEngine sympy
```

### Ejecución

```bash
python main.py
```

---

## Decisiones de Diseño

### ¿Por qué QWebEngineView para mostrar resultados?

Los resultados matemáticos requieren renderizado LaTeX de calidad. Las opciones eran:

| Opción | Ventaja | Desventaja |
|---|---|---|
| `QLabel` con texto plano | Simple | No renderiza LaTeX |
| `matplotlib` embebido | Renderiza LaTeX | Lento, feo para texto mixto |
| **`QWebEngineView` + MathJax** | Renderizado profesional, HTML completo | Requiere WebEngine |

Se eligió MathJax 2.7 sobre MathJax 3 por mayor compatibilidad con el motor de renderizado interno de Qt.

### ¿Por qué `\mathscr{L}` en lugar de `\mathcal{L}`?

`\mathcal{L}` en MathJax depende del paquete cargado. En algunas configuraciones produce una L con serifa, en otras una caligráfica, y en otras falla silenciosamente. `\mathscr{L}` con AMSfonts siempre produce la L de script clásica de los libros de Laplace.

Para cambiar la notación en toda la app basta modificar **una línea** en `solve_math.py`:

```python
L_TEX = r'\mathscr{L}'   # ← cambiar aquí
```

### ¿Por qué SymPy y no un motor propio?

SymPy provee `laplace_transform`, `inverse_laplace_transform`, `apart` (fracciones parciales) y el CAS completo. Reimplementar esto manualmente introduciría errores y no aportaría valor educativo al proyecto.

---

*Proyecto académico — Transformadas de Laplace con PyQt6 y SymPy*