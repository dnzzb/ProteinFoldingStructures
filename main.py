# main.py
import sys
from PySide6.QtWidgets import QApplication, QMainWindow

from app import NavigationController


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Protein Folding Structures")
        self.resize(1000, 600)
        self.controller = NavigationController(self)


def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()

# Example build command:
# pyinstaller --onefile --noconsole --collect-all vtkmodules --add-data "assets;assets" main.py
