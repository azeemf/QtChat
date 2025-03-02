from PySide6.QtWidgets import QApplication, QPushButton, QMainWindow
from PySide6.QtGui import QLinearGradient, QColor, QPalette, QBrush, QFont
from PySide6.QtCore import Qt

def create_styled_pushbutton(text, gradient_start, gradient_end, text_color, font_size):
    """
    Creates a QPushButton with the specified style.

    Args:
        text (str): The text to display on the button.
        gradient_start (QColor): The starting color of the linear gradient.
        gradient_end (QColor): The ending color of the linear gradient.
        text_color (QColor): The color of the text.
        font_size (int): The font size of the text.

    Returns:
        QPushButton: The styled QPushButton.
    """

    button = QPushButton(text)

    # Set the font
    font = QFont()
    font.setPointSize(font_size)
    button.setFont(font)
    button.setMaximumWidth(250)
    button.setMaximumHeight(50)

    # Create the linear gradient
    gradient = QLinearGradient(0, 0, button.width(), button.height())
    gradient.setColorAt(0, gradient_start)
    gradient.setColorAt(1, gradient_end)

    # Set the style sheet
    button.setStyleSheet(f"""
        QPushButton {{
            background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 0, stop: 0 {gradient_start.name()}, stop: 1 {gradient_end.name()});
            color: {text_color.name()};
            border-width: 1px;
            border-style: solid;
            border-radius: 10px;
            border-color: {gradient_start.name()};
            padding: 10px 20px; 
        }}
        QPushButton:hover {{
            background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 0, stop: 0 {gradient_start.lighter(120).name()}, stop: 1 {gradient_end.lighter(120).name()});
        }}
        QPushButton:pressed {{
            background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 0, stop: 0 {gradient_start.darker(120).name()}, stop: 1 {gradient_end.darker(120).name()});
        }}
    """)

    return button

if __name__ == "__main__":
    app = QApplication([])

    # Define the button style
    button_text = "PLAY NOW ->"
    gradient_start_color = QColor(100, 181, 246)  # Light blue
    gradient_end_color = QColor(66, 165, 245)    # Slightly darker blue
    text_color = QColor(255, 255, 255)          # White text
    font_size = 14
    border_radius = 20

    # Create the styled button
    button = create_styled_pushbutton(button_text, gradient_start_color, gradient_end_color, text_color, font_size)

    window = QMainWindow()
    window.setCentralWidget(button)
    window.show()
    app.exec()