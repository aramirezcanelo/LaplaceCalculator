from PyQt6.QtCore import Qt, QPropertyAnimation, QEasingCurve
from PyQt6.QtGui import QCursor, QGuiApplication, QColor
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
                             QLineEdit, QPushButton, QLabel,
                             QGraphicsOpacityEffect, QListWidget,
                             QScrollArea, QFrame, QSizePolicy, QGraphicsDropShadowEffect)
from PyQt6.QtWebEngineCore import QWebEngineSettings
from PyQt6.QtWebEngineWidgets import QWebEngineView


# ── Paleta Estilo Windows 11 Oscuro ──────────────────────────────────────────
THEMES = {
    "dark": {
        "bg":           "#1c1c1c",
        "bg2":          "#202020",
        "surface":      "#2d2d2d",
        "border":       "rgba(255, 255, 255, 0.05)",
        "accent":       "#60cdff",
        "accent_hover": "#52b1dc",
        "accent_press": "#4396bd",
        "text":         "#ffffff",
        "text2":        "#e3e3e3",
        "text3":        "#a6a6a6",
        "danger":       "#ff99a4",
        "danger_bg":    "rgba(255, 153, 164, 0.1)",
        "danger_hover": "rgba(255, 153, 164, 0.2)",
        "edo_bg":       "#2d2d2d", "edo_fg": "#ffffff", "edo_hover": "#323232",
        "var_bg":       "#2d2d2d", "var_fg": "#ffffff", "var_hover": "#323232",
        "func_bg":      "#2d2d2d", "func_fg": "#ffffff", "func_hover": "#323232",
        "op_bg":        "#202020", "op_fg":  "#ffffff", "op_hover":  "#282828",
        "web_bg":       "#252525", "web_text": "#ffffff", "web_bold": "#a6a6a6",
        "theme_icon":   "🌙",
        "dlg_code_bg":  "#202020", "dlg_code_fg": "#60cdff",
    }
}


PLANTILLA_WEB = """
<html>
<head>
  <script type="text/x-mathjax-config">
    MathJax.Hub.Config({{
      messageStyle: "none",
      tex2jax: {{
        inlineMath: [['$','$'],["\\\\(","\\\\)"]],
        displayMath: [['$$','$$'],["\\\\[","\\\\]"]],
        processEscapes: true
      }},
      "SVG": {{ font: "TeX" }}
    }});
  </script>
  <script type="text/javascript"
    src="https://cdnjs.cloudflare.com/ajax/libs/mathjax/2.7.9/MathJax.js?config=TeX-MML-AM_SVG">
  </script>
  <script>
    window.addEventListener('load', function() {{
      if (window.MathJax) MathJax.Hub.Queue(["Typeset", MathJax.Hub]);
    }});
  </script>
  <style>
  /* Estilo de scrollbar nativo de Chromium (Escapado para Python .format) */
    ::-webkit-scrollbar {{ width: 6px; }}
    ::-webkit-scrollbar-track {{ background: transparent; }}
    ::-webkit-scrollbar-thumb {{ 
      background: rgba(255,255,255,0.15); 
      border-radius: 3px; 
    }}
    ::-webkit-scrollbar-thumb:hover {{ background: rgba(255,255,255,0.25); }}
    #MathJax_ProcessMessage {{ display:none !important; }}
    .MathJax_SVG_Display {{ overflow-x: auto; }}
    html, body {{
      margin: 0; padding: 10px 12px;
      background-color: {web_bg};
      font-family: -apple-system, 'SF Pro Text', 'Segoe UI', sans-serif;
      color: {web_text};
      font-size: 13px;
      line-height: 1.65;
    }}
    b {{ color: {web_bold}; }}
    svg {{ font-size: 15px; }}
  </style>
</head>
<body>{contenido}</body>
</html>
"""


def build_stylesheet(t: dict) -> str:
    return f"""
    QWidget {{
        background-color: {t['bg']};
        font-family: -apple-system, 'SF Pro Display', 'Segoe UI', sans-serif;
        color: {t['text']};
    }}
    QLineEdit {{
        border: 1px solid {t['border']};
        border-radius: 4px;
        padding: 8px 12px;
        font-size: 18px;
        font-weight: 600;
        color: {t['text']};
        background-color: transparent;
        selection-background-color: {t['accent']};
    }}
    QLineEdit:focus {{
        border-bottom: 2px solid {t['accent']};
    }}
    QPushButton {{
        border: 1px solid {t['border']};
        border-radius: 4px;
        padding: 10px 4px;
        font-size: 13px;
        font-weight: 400;
    }}
    QPushButton[category="edo"] {{ background-color: {t['edo_bg']}; color: {t['edo_fg']}; }}
    QPushButton[category="edo"]:hover  {{ background-color: {t['edo_hover']}; }}
    QPushButton[category="var"] {{ background-color: {t['var_bg']}; color: {t['var_fg']}; }}
    QPushButton[category="var"]:hover  {{ background-color: {t['var_hover']}; }}
    QPushButton[category="func"] {{ background-color: {t['func_bg']}; color: {t['func_fg']}; }}
    QPushButton[category="func"]:hover {{ background-color: {t['func_hover']}; }}
    QPushButton[category="op"] {{ background-color: {t['op_bg']}; color: {t['op_fg']}; }}
    QPushButton[category="op"]:hover  {{ background-color: {t['op_hover']}; }}

    QPushButton#btn_info {{
        background-color: transparent; color: {t['text2']};
        border: none; border-radius: 4px; font-size: 14px;
        min-width: 32px; max-width: 32px; min-height: 32px; max-height: 32px;
    }}
    QPushButton#btn_info:hover {{ background-color: {t['surface']}; color: {t['text']}; }}

    QPushButton#btn_ir {{
        background-color: {t['accent']}; color: #000000;
        border-radius: 4px; font-size: 14px; font-weight: 500;
        padding: 10px; border: none;
    }}
    QPushButton#btn_ir:hover   {{ background-color: {t['accent_hover']}; }}
    QPushButton#btn_ir:pressed {{ background-color: {t['accent_press']}; }}

    QPushButton#btn_limpiar {{
        background-color: {t['op_bg']}; color: {t['text']};
        border-radius: 4px; font-size: 14px;
        padding: 10px; border: 1px solid {t['border']};
    }}
    QPushButton#btn_limpiar:hover {{ background-color: {t['op_hover']}; }}

    QListWidget {{
        border: 1px solid {t['border']}; border-radius: 4px;
        background-color: {t['bg2']}; color: {t['text2']};
        padding: 6px; font-size: 12px; outline: none;
    }}
    QListWidget::item {{ padding: 6px 8px; border-radius: 4px; }}
    QListWidget::item:hover {{ background-color: {t['surface']}; color: {t['text']}; }}
    QListWidget::item:selected {{ background-color: {t['surface']}; color: {t['accent']}; }}

    QLabel {{ color: {t['text3']}; font-size: 11px; font-weight: 600; letter-spacing: 0.4px; background: transparent; }}
    QLabel#lbl_titulo {{ color: {t['text']}; font-size: 14px; font-weight: 600; letter-spacing: -0.1px; }}

    QWebEngineView {{
        border: 1px solid {t['border']};
        border-radius: 4px;
        background-color: #252525;
    }}
    QFrame#panel_ejemplos_interno {{
        background-color: {t['bg2']};
        border-left: 1px solid {t['border']};
    }}
    """


# ── Panel lateral de guía de sintaxis ────────────────────────────────────────
class PanelEjemplosLateral(QFrame):
    def __init__(self, parent, tema: dict):
        super().__init__(parent)
        self.parent_ref = parent
        self.setObjectName("panel_ejemplos_interno")
        self.init_panel(tema)

    def init_panel(self, t: dict):
        if self.layout():
            QWidget().setLayout(self.layout())

        layout = QVBoxLayout(self)
        layout.setContentsMargins(18, 14, 18, 14)
        layout.setSpacing(10)

        lbl_titulo = QLabel("📐   Guía de Sintaxis")
        lbl_titulo.setStyleSheet(f"font-size: 13px; font-weight: 700; color: {t['text']};")
        layout.addWidget(lbl_titulo)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll.setStyleSheet("background: transparent; border: none;")

        cw = QWidget()
        cw.setStyleSheet("background: transparent;")
        cl = QVBoxLayout(cw)
        cl.setContentsMargins(0, 0, 4, 0)
        cl.setSpacing(10)

        ejemplos = [
            ("TRANSFORMADAS DIRECTAS", [
                ("Constante",   "5"),
                ("Potencia",    "t**3"),
                ("Exponencial", "exp(-2*t)"),
                ("Seno",        "sin(3*t)"),
                ("Coseno",      "cos(3*t)"),
            ]),
            ("ECUACIONES DIFERENCIALES", [
                ("1er orden",   "y' + 2*y = 0; y(0)=1"),
                ("2do orden",   "y'' + 3*y' + 2*y = 0; y(0)=1; y'(0)=5"),
                ("Oscilatorio", "y'' + 4*y = cos(t); y(0)=0; y'(0)=0"),
            ]),
            ("SINTAXIS REQUERIDA", [
                ("Potencia t²",    "t**2   (no t^2)"),
                ("Multiplicación", "2*t    (no 2t)"),
                ("Separador CI",   "; entre EDO y condiciones"),
            ]),
        ]

        for titulo_sec, items in ejemplos:
            lbl_s = QLabel(titulo_sec)
            lbl_s.setStyleSheet(
                f"font-size: 9px; font-weight: 700; color: {t['text3']};"
                "letter-spacing: 0.5px; margin-top: 4px;"
            )
            cl.addWidget(lbl_s)
            for nombre, codigo in items:
                fila = QHBoxLayout()
                fila.setSpacing(6)
                lbl_n = QLabel(nombre)
                lbl_n.setStyleSheet(
                    f"color: {t['text2']}; font-size: 11px;"
                    "min-width: 90px; max-width: 90px;"
                )
                lbl_n.setWordWrap(True)

                lbl_c = QPushButton(codigo)
                lbl_c.setStyleSheet(f"""
                    background-color: {t['dlg_code_bg']}; color: {t['dlg_code_fg']};
                    font-family: 'SF Mono', 'Consolas', monospace; text-align: left;
                    font-size: 10px; font-weight: 600;
                    border: 1px solid {t['border']};
                    border-radius: 4px; padding: 4px 6px;
                """)
                lbl_c.setCursor(Qt.CursorShape.PointingHandCursor)
                lbl_c.clicked.connect(lambda checked, c=codigo: self.parent_ref.insertar_ejemplo(c))

                fila.addWidget(lbl_n)
                fila.addWidget(lbl_c, stretch=1)
                cl.addLayout(fila)

        cl.addStretch()
        scroll.setWidget(cw)
        layout.addWidget(scroll)


# ── Ventana principal ─────────────────────────────────────────────────────────
class InterfazCalculadora(QWidget):
    def __init__(self):
        super().__init__()
        self._tema_actual = "dark"
        self._ultimo_html_contenido = (
            "<p style='text-align:center; margin-top:10px; font-size:12px; opacity:0.6;'>"
            "Ingresa una expresión o EDO para comenzar</p>"
        )
        self.init_ui()
        self._aplicar_tema()
        self._render_web(self._ultimo_html_contenido)

    def init_ui(self):
        self.setWindowTitle("Transformadas de Laplace")

        pantalla = QGuiApplication.primaryScreen().availableGeometry()
        self.ancho_base = 430
        self.ancho_extendido = 700
        alto_reducido = pantalla.height() - 40

        self.resize(self.ancho_base, alto_reducido)
        self.setMinimumSize(self.ancho_base, 460)
        self.setMaximumSize(self.ancho_extendido, alto_reducido)
        self.move(pantalla.x() + (pantalla.width() - self.ancho_base) // 2, pantalla.y())

        layout_global = QHBoxLayout(self)
        layout_global.setContentsMargins(0, 0, 0, 0)
        layout_global.setSpacing(0)

        self.widget_calculadora = QWidget()
        main_layout = QVBoxLayout(self.widget_calculadora)
        main_layout.setSpacing(8)
        main_layout.setContentsMargins(14, 14, 14, 14)

        # ── Barra superior ────────────────────────────────────────────────────
        barra = QHBoxLayout()
        barra.setSpacing(6)
        self.lbl_titulo = QLabel("Transformadas de Laplace")
        self.lbl_titulo.setObjectName("lbl_titulo")
        barra.addWidget(self.lbl_titulo)
        barra.addStretch()

        self.btn_info = QPushButton("☰")
        self.btn_info.setObjectName("btn_info")
        self.btn_info.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_info.clicked.connect(self.toggle_ejemplos_lateral)
        barra.addWidget(self.btn_info)
        main_layout.addLayout(barra)

        # ── Campo de entrada ──────────────────────────────────────────────────
        self.entry = QLineEdit()
        self.entry.setPlaceholderText("Ej: y'' + 3*y' + 2*y = 0; y(0)=1")
        main_layout.addWidget(self.entry)

        # ── Teclado virtual ───────────────────────────────────────────────────
        pad_grid = QGridLayout()
        pad_grid.setSpacing(4)
        pad_grid.setContentsMargins(0, 2, 0, 2)

        botones = [
            ('y',      'y',       'edo',  0, 0), ('7',      '7',       'op',  0, 5),
            ("y'",     "y'",      'edo',  0, 1), ('8',      '8',       'op',  0, 6),
            ("y''",    "y''",     'edo',  0, 2), ('9',      '9',       'op',  0, 7),
            ('=',      '=',       'edo',  0, 3), ('/',      '/',       'op',  0, 8),
            (';',      '; ',      'edo',  0, 4),

            ('t',      't',       'var',  1, 0), ('4',      '4',       'op',  1, 5),
            ('s',      's',       'var',  1, 1), ('5',      '5',       'op',  1, 6),
            ('π',      'pi',      'var',  1, 2), ('6',      '6',       'op',  1, 7),
            ('α',      'a',       'var',  1, 3), ('*',      '*',       'op',  1, 8),
            ('s²',     's**2',    'op',   1, 4),

            ('sin',    'sin(',    'func', 2, 0), ('1',      '1',       'op',  2, 5),
            ('cos',    'cos(',    'func', 2, 1), ('2',      '2',       'op',  2, 6),
            ('eⁿ',     'exp(',    'func', 2, 2), ('3',      '3',       'op',  2, 7),
            ('(',      '(',       'op',   2, 3), ('-',      '-',       'op',  2, 8),
            (')',      ')',       'op',   2, 4),

            ('sinh',   'sinh(',   'func', 3, 0), ('0',      '0',       'op',  3, 5),
            ('cosh',   'cosh(',   'func', 3, 1), ('.',      '.',       'op',  3, 6),
            ("y'(0)=", "y'(0)=",  'edo',  3, 2), ('+',      '+',       'op',  3, 7),
            ('tⁿ',     't**n',    'op',   3, 3),
        ]

        self._botones_pad = []
        for txt, val, cat, fila, col in botones:
            btn = QPushButton(txt)
            btn.setProperty("category", cat)
            btn.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
            btn.clicked.connect(lambda checked, v=val: self.insertar(v))
            pad_grid.addWidget(btn, fila, col)
            self._botones_pad.append(btn)
        main_layout.addLayout(pad_grid)

        # ── Botones de acción ─────────────────────────────────────────────────
        layout_acciones = QHBoxLayout()
        layout_acciones.setSpacing(4)

        self.btn_limpiar_todo = QPushButton("C")
        self.btn_limpiar_todo.setObjectName("btn_limpiar")
        self.btn_limpiar_todo.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_limpiar_todo.clicked.connect(lambda: self.entry.clear())
        self.btn_limpiar_todo.setFixedWidth(50)

        self.btn_ir = QPushButton("Calcular")
        self.btn_ir.setObjectName("btn_ir")
        self.btn_ir.setCursor(Qt.CursorShape.PointingHandCursor)

        self.btn_limpiar = QPushButton("⌫")
        self.btn_limpiar.setObjectName("btn_limpiar")
        self.btn_limpiar.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_limpiar.clicked.connect(lambda: self.entry.backspace())

        layout_acciones.addWidget(self.btn_limpiar_todo, stretch=1)
        layout_acciones.addWidget(self.btn_ir, stretch=4)
        layout_acciones.addWidget(self.btn_limpiar, stretch=1)
        main_layout.addLayout(layout_acciones)

        # ── Área de resultado ─────────────────────────────────────────────────
        self.lbl_res = QLabel("RESULTADO")
        main_layout.addWidget(self.lbl_res)

        self.web_view = QWebEngineView()
        self.web_view.page().setBackgroundColor(QColor("#252525"))
        self.web_view.setStyleSheet("background-color: #252525;")
        self.web_view.settings().setAttribute(QWebEngineSettings.WebAttribute.JavascriptEnabled, True)
        self.web_view.settings().setAttribute(QWebEngineSettings.WebAttribute.LocalContentCanAccessRemoteUrls, True)
        
        # NUEVA CONFIGURACIÓN CORRECTA:
        self.web_view.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.web_view.setMinimumHeight(80)

        # Aplicamos el efecto de opacidad directamente al web_view
        self.fade_effect = QGraphicsOpacityEffect(self)
        self.web_view.setGraphicsEffect(self.fade_effect)
        
        # Agregamos el web_view directo al layout, sin QScrollArea
        main_layout.addWidget(self.web_view, stretch=2)

        # ── Historial ─────────────────────────────────────────────────────────
        self.lbl_historial = QLabel("HISTORIAL")
        main_layout.addWidget(self.lbl_historial)

        self.historial_list = QListWidget()
        self.historial_list.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        main_layout.addWidget(self.historial_list, stretch=1)

        layout_global.addWidget(self.widget_calculadora, stretch=1)

        self.panel_ejemplos = PanelEjemplosLateral(self, THEMES[self._tema_actual])
        self.panel_ejemplos.setVisible(False)
        layout_global.addWidget(self.panel_ejemplos)

        self.setLayout(layout_global)

    # ── Tema ──────────────────────────────────────────────────────────────────
    def _aplicar_tema(self):
        t = THEMES[self._tema_actual]
        self.setStyleSheet(build_stylesheet(t))
        self.panel_ejemplos.init_panel(t)
        for btn in self._botones_pad:
            btn.style().unpolish(btn)
            btn.style().polish(btn)

    # ── WebView ───────────────────────────────────────────────────────────────
    def _render_web(self, contenido: str):
        t = THEMES[self._tema_actual]
        html = PLANTILLA_WEB.format(
            web_bg=t["web_bg"], web_text=t["web_text"], web_bold=t["web_bold"],
            contenido=contenido,
        )
        self.web_view.setHtml(html)

    def mostrar_html(self, html_str: str):
        import re
        match = re.search(r'<body[^>]*>(.*?)</body>', html_str, re.DOTALL | re.IGNORECASE)
        contenido = match.group(1).strip() if match else html_str
        self._ultimo_html_contenido = contenido
        self._render_web(contenido)

    # ── Panel lateral ─────────────────────────────────────────────────────────
    def toggle_ejemplos_lateral(self):
        pantalla = QGuiApplication.primaryScreen().availableGeometry()
        if self.panel_ejemplos.isVisible():
            self.panel_ejemplos.setVisible(False)
            self.setMinimumWidth(self.ancho_base)
            self.setMaximumWidth(self.ancho_base)
            self.resize(self.ancho_base, self.height())
        else:
            self.panel_ejemplos.setVisible(True)
            self.setMinimumWidth(self.ancho_extendido)
            self.setMaximumWidth(self.ancho_extendido)
            self.resize(self.ancho_extendido, self.height())
        self.move(pantalla.x() + (pantalla.width() - self.width()) // 2, self.y())

    def insertar_ejemplo(self, formula: str):
        self.entry.clear()
        if "   (" in formula:
            formula = formula.split("   (")[0]
        self.insertar(formula)

    # ── API pública ───────────────────────────────────────────────────────────
    def insertar(self, val):
        self.entry.insert(val)
        self.entry.setFocus()

    def animar_calculo(self):
        self.anim_fade = QPropertyAnimation(self.fade_effect, b"opacity")
        self.anim_fade.setDuration(300)
        self.anim_fade.setEasingCurve(QEasingCurve.Type.OutCubic)
        self.anim_fade.setStartValue(0.0)
        self.anim_fade.setEndValue(1.0)
        self.anim_fade.start()

    def obtener_texto(self):
        return self.entry.text().strip()
