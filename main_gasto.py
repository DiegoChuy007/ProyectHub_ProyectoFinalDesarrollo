from PyQt5 import QtWidgets
import sys
# Asume que load_ui_gasto.py está en la ruta correcta
from load.load_ui_gasto import Load_ui_gastos 

def main():
    app = QtWidgets.QApplication(sys.argv)
    window = Load_ui_gastos()
    window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()