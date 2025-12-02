from PyQt5 import QtWidgets
import sys
# Asegúrate de que la ruta sea correcta
from load.load_ui_empleados import Load_ui_empleados 

def main():
    app = QtWidgets.QApplication(sys.argv)
    window = Load_ui_empleados()
    window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()