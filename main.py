import sys

from PySide6.QtWidgets import QApplication

from desktop.window import CompanionWindow

def main():
    app = QApplication(sys.argv)

    window = CompanionWindow()
    window.show()
    print("Companion window is running...")

    sys.exit(app.exec())

if __name__ == "__main__":
    main()