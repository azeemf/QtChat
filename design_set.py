from PySide6.QtWidgets import QApplication, QPushButton, QMainWindow
from PySide6.QtGui import QLinearGradient, QColor, QPalette, QBrush, QFont
from PySide6.QtCore import Qt

class DesignSet:
    def __init__(self, useDefaultColors):
        self.design_set = {
            "Colors": None,
            "Widgets": ["GradButton"]
        }

        if useDefaultColors:
            self.design_set["Colors"] = {
                "Primary": QColor(100, 181, 246),
                "Secondary": QColor(66, 165, 245)
            }
    
    def getPrimary(self):
        return self.design_set["Colors"]["Primary"]
    
    def getSecondary(self):
        return self.design_set["Colors"]["Secondary"]
    