from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QLabel,
    QPushButton
)
from PySide6.QtCore import Qt

class WelcomePage(QWidget):

    def __init__(self):
        super().__init__()

        layout = QVBoxLayout(
            self
        )

        layout.setAlignment(
            Qt.AlignCenter
        )

        title = QLabel(
            "Welcome to CaImg Analyzer"
        )

        title.setStyleSheet(
            """
            QLabel{
                font-size: 28px;
                font-weight: bold;
            }
            """
        )

        subtitle = QLabel(
            "Calcium imaging analysis"
        )

        subtitle.setStyleSheet(
            """
            QLabel {
                font-size: 16px;
                padding: 10px;
            }
            """
        )

        self.new_button = QPushButton(
            "New Analysis"
        )

        self.new_button.setFixedWidth(
            200
        )

        layout.addWidget(
            title,
            alignment = Qt.AlignCenter
        )

        layout.addWidget(
            subtitle,
            alignment = Qt.AlignCenter
        )

        layout.addSpacing(
            20
        )

        layout.addWidget(
            self.new_button,
            alignment = Qt.AlignCenter
        )
