# vista/interfaz_grafica.py
from PyQt6.QtCore import Qt, QPropertyAnimation
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, 
                             QLineEdit, QPushButton, QLabel, QGraphicsDropShadowEffect, 
                             QGraphicsOpacityEffect, QListWidget, QMessageBox)
from PyQt6.QtWebEngineCore import QWebEngineSettings
from PyQt6.QtWebEngineWidgets import QWebEngineView

class InterfazCalculadora(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("Calculadora de Transformadas Directas de Laplace")
        self.resize(600, 750)
        self.setMinimumSize(500, 600)
        
        self.setStyleSheet("""
            QWidget { background-color: #f8fafc; font-family: 'Segoe UI', Arial, sans-serif; }
            QLineEdit { border: 2px solid #cbd5e1; border-radius: 8px; padding: 10px; font-size: 16px; color: #0f172a; background-color: #ffffff; }
            QLineEdit:focus { border: 2px solid #10b981; background-color: #ffffff; }
            QPushButton { background-color: #f1f5f9; border: 1px solid #e2e8f0; border-radius: 6px; padding: 10px; font-size: 13px; font-weight: bold; color: #334155; }
            QPushButton:hover { background-color: #e2e8f0; }
            QPushButton#btn_info { background-color: #0f172a; color: white; border-radius: 8px; font-size: 14px; font-weight: bold; min-width: 45px; max-width: 45px; border: none; }
            QPushButton#btn_info:hover { background-color: #1e293b; }
            
            /* CSS para el botón Calcular */
            QPushButton#btn_ir { background-color: #10b981; color: white; border-radius: 8px; font-size: 16px; padding: 12px; border: none; }
            QPushButton#btn_ir:hover { background-color: #059669; }
            QPushButton#btn_ir:pressed { background-color: #047857; }
            
            /* CSS para el botón Eliminar */
            QPushButton#btn_limpiar {background-color: #ef4444; color: white; border-radius: 8px; font-size: 16px; padding: 12px; border: none; }
            QPushButton#btn_limpiar:hover { background-color: #dc2626; }
            QPushButton#btn_limpiar:pressed { background-color: #b91c1c; }

            QListWidget { border: 2px solid #cbd5e1; border-radius: 8px; background-color: #ffffff; color: #0f172a; padding: 5px; }
            QListWidget::item { padding: 6px; border-bottom: 1px solid #f1f5f9; }
            QListWidget::item:hover { background-color: #f1f5f9; }
        """)

        main_layout = QVBoxLayout()
        main_layout.setSpacing(12)
        main_layout.setContentsMargins(30, 25, 30, 25)

        input_line_layout = QHBoxLayout()
        self.entry = QLineEdit()
        self.entry.setPlaceholderText("Ej. t**2 * exp(-3*t) o sin(2*t)")
        input_line_layout.addWidget(self.entry)

        self.btn_info = QPushButton("!?")
        self.btn_info.setObjectName("btn_info")
        self.btn_info.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_info.clicked.connect(self.mostrar_ejemplos)
        input_line_layout.addWidget(self.btn_info)
        main_layout.addLayout(input_line_layout)

        pad_layout_1 = QHBoxLayout()
        botones_1 = [('t\u207f', 't**n'), ('s', 's'), ('e\u02e3', 'exp('), ('sin', 'sin('), ('cos', 'cos('), ('/', '/')]
        for txt, val in botones_1:
            btn = QPushButton(txt)
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            btn.clicked.connect(lambda checked, v=val: self.insertar(v))
            pad_layout_1.addWidget(btn)
        main_layout.addLayout(pad_layout_1)

        pad_layout_2 = QHBoxLayout()
        botones_2 = [('sinh', 'sinh('), ('cosh', 'cosh('), ('\u03c0', 'pi'), ('alpha', 'a'), ('+', '+'), ('-', '-'), ('*', '*'), ('(', '('), (')', ')')]
        for txt, val in botones_2:
            btn = QPushButton(txt)
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            btn.clicked.connect(lambda checked, v=val: self.insertar(v))
            pad_layout_2.addWidget(btn)
        main_layout.addLayout(pad_layout_2)

        # Nueva organización de botones de acción inferiores
        layout_botones_accion = QHBoxLayout()
        
        self.btn_ir = QPushButton("Calcular")
        self.btn_ir.setObjectName("btn_ir")
        self.btn_ir.setCursor(Qt.CursorShape.PointingHandCursor)

        self.btn_limpiar = QPushButton("Eliminar")
        self.btn_limpiar.setObjectName("btn_limpiar")
        self.btn_limpiar.setCursor(Qt.CursorShape.PointingHandCursor)
        
        shadow_ir = QGraphicsDropShadowEffect()
        shadow_ir.setBlurRadius(10)
        shadow_ir.setColor(Qt.GlobalColor.black)
        shadow_ir.setOffset(0, 2)
        self.btn_ir.setGraphicsEffect(shadow_ir)

        shadow_limpiar = QGraphicsDropShadowEffect()
        shadow_limpiar.setBlurRadius(10)
        shadow_limpiar.setColor(Qt.GlobalColor.black)
        shadow_limpiar.setOffset(0, 2)
        self.btn_limpiar.setGraphicsEffect(shadow_limpiar)

        layout_botones_accion.addWidget(self.btn_ir, stretch=3)
        layout_botones_accion.addWidget(self.btn_limpiar, stretch=1)
        
        main_layout.addLayout(layout_botones_accion)

        self.lbl_res = QLabel("Procedimiento y Solución:")
        self.lbl_res.setStyleSheet("font-size: 14px; font-weight: bold; color: #334155; margin-top: 5px;")
        main_layout.addWidget(self.lbl_res)

        self.web_view = QWebEngineView()
        self.web_view.setStyleSheet("border: 2px solid #e2e8f0; border-radius: 8px; background-color: #ffffff;")
        self.web_view.settings().setAttribute(QWebEngineSettings.WebAttribute.JavascriptEnabled, True)
        self.web_view.settings().setAttribute(QWebEngineSettings.WebAttribute.LocalContentCanAccessRemoteUrls, True)
        
        self.fade_effect = QGraphicsOpacityEffect()
        self.web_view.setGraphicsEffect(self.fade_effect)
        main_layout.addWidget(self.web_view, stretch=1)

        self.lbl_historial = QLabel("Historial de Consultas:")
        self.lbl_historial.setStyleSheet("font-size: 14px; font-weight: bold; color: #334155; margin-top: 5px;")
        main_layout.addWidget(self.lbl_historial)
        
        self.historial_list = QListWidget()
        main_layout.addWidget(self.historial_list)

        self.setLayout(main_layout)

    def insertar(self, val):
        self.entry.insert(val)
        self.entry.setFocus()

    def mostrar_ejemplos(self):
        msg = QMessageBox(self)
        msg.setWindowTitle("Formatos y Ejemplos de Transformadas")
        msg.setIcon(QMessageBox.Icon.Information)
        msg.setText("<b>Formatos estructurales requeridos para transformadas directas:</b>")
        msg.setInformativeText(
            "<b>Constante:</b> 5 o k\n"
            "<b>Potencia:</b> t**3 o t**n\n"
            "<b>Exponencial:</b> exp(2*t) o exp(-a*t)\n"
            "<b>Seno / Coseno:</b> sin(3*t) o cos(k*t)\n"
            "<b>Hiperbólicas:</b> sinh(2*t) o cosh(a*t)\n"
            "<b>Primer Teorema de Traslación:</b> t**2 * exp(-3*t)\n"
            "<b>Linealidad (Combinadas):</b> t**2 + sin(2*t) - 5*exp(t)"
        )
        msg.setStyleSheet("""
            QLabel { font-size: 13px; color: #0f172a; min-width: 380px; max-width: 380px; }
            QPushButton { background-color: #0f172a; color: white; padding: 6px 16px; font-weight: bold; border-radius: 4px; }
            QPushButton:hover { background-color: #1e293b; }
        """)
        msg.exec()

    def animar_calculo(self):
        # Se ha eliminado el cálculo matemático de QRect para evitar reducciones del botón.
        # Ahora se controla con pseudo-clases CSS (:pressed) y solo se ejecuta el desvanecimiento.
        self.anim_fade = QPropertyAnimation(self.fade_effect, b"opacity")
        self.anim_fade.setDuration(250)
        self.anim_fade.setStartValue(0.0)
        self.anim_fade.setEndValue(1.0)
        self.anim_fade.start()

    def mostrar_html(self, html_str):
        self.web_view.setHtml(html_str)
        
    def obtener_texto(self):
        return self.entry.text().strip()