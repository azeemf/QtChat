from PySide6.QtWidgets import QApplication
from main_window import ChatWindow

if __name__ == "__main__":
    app = QApplication()
    window = ChatWindow()
    window.show()
    app.exec()