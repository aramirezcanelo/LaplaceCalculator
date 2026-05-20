import sys
from PyQt6.QtWidgets import QApplication

from view.interfaz_grafica import InterfazCalculadora
from model.solve_math import SolverLaplace
from view.utilidades_html import generar_html

class ControladorCalculadora:
    def __init__(self):
        self.view = InterfazCalculadora()
        self.modelo = SolverLaplace()
        
        self.view.btn_ir.clicked.connect(self.ejecutar_calculo)
        self.view.entry.returnPressed.connect(self.ejecutar_calculo)
        self.view.historial_list.itemClicked.connect(self.cargar_historial)
        
        self.view.btn_limpiar.clicked.connect(self.limpiar_pantalla)

        self.view.mostrar_html(generar_html("<h3>F(s) = </h3>"))

    def ejecutar_calculo(self):
        texto_entrada = self.view.obtener_texto()
        if not texto_entrada:
            return
            
        self.view.animar_calculo()
        
        estado, resultado_html = self.modelo.procesar_expresion(texto_entrada)
        
        if estado == "inversa":
            self.view.lbl_res.setText("Estado: Operación No Soportada")
        elif estado == "directa":
            self.view.lbl_res.setText("Procedimiento y Solución: ")
        else:
            self.view.lbl_res.setText("Procedimiento y Solución: ")

        self.view.mostrar_html(resultado_html)
        
        items_historial = [self.view.historial_list.item(i).text() for i in range(self.view.historial_list.count())]
        if texto_entrada not in items_historial:
            self.view.historial_list.insertItem(0, texto_entrada)

    def cargar_historial(self, item):
        self.view.entry.setText(item.text())
        self.ejecutar_calculo()

    def limpiar_pantalla(self):
        self.view.entry.clear()
        self.view.lbl_res.setText("Procedimiento y Solución:")
        self.view.mostrar_html(generar_html("<h3>F(s) = </h3>"))
        self.view.entry.setFocus()

    def iniciar(self):
        self.view.show()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    controlador = ControladorCalculadora()
    controlador.iniciar()
    sys.exit(app.exec())