# main_asignacion.py

from PyQt5 import QtWidgets
import sys
# Importa la clase del controlador de la interfaz de Asignación
from load.load_ui_asignacion import Load_ui_asignacion 

def main():
    app = QtWidgets.QApplication(sys.argv)
    
    # Inicia la ventana de Asignación directamente
    window = Load_ui_asignacion()
    window.show()
    
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()