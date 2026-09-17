from PySide6.QtWidgets import (
    QMainWindow,
    QWidget,
    QHBoxLayout,
    QVBoxLayout,
    QPushButton,
    QLabel,
    QStackedWidget,
    QFrame,
)

from PySide6.QtCore import Qt
from gui.pages.welcome_page import WelcomePage
from gui.pages.analysis_page import AnalysisPage
from gui.pages.export_page import ExportPage

class MainWindow(QMainWindow):

    def __init__(self):

        super().__init__()

        self.setWindowTitle(
            "CaImg Analyzer"
        )

        self.resize(
            1200,
            750
        )

        self._build_ui()

    def _build_ui(self):

        central_widget = QWidget()

        self.setCentralWidget(
            central_widget
        )

        main_layout = QHBoxLayout(
            central_widget
        )

        main_layout.setContentsMargins(
            0,
            0,
            0,
            0
        )

        sidebar = QFrame()

        sidebar.setFixedWidth(
            220
        )

        sidebar_layout = QVBoxLayout(
            sidebar
        )

        title = QLabel(
            "CaImg Analyzer"
        )

        title.setAlignment(
            Qt.AlignCenter
        )

        title.setStyleSheet(
        """
            QLabel {
                font-size: 22px;
                font-weight: bold;
                padding: 20px;
            }
        """
        )

        sidebar_layout.addWidget(
            title
        )

        self.new_analysis_button = QPushButton(
            "New Analysis"
        )

        self.export_button = QPushButton(
            "Export"
        )

        self.compare_button = QPushButton(
            "Compare"
        )

        self.statistics_button = QPushButton(
            "Statistics"
        )

        sidebar_layout.addWidget(
            self.new_analysis_button
        )

        sidebar_layout.addWidget(
            self.export_button
        )

        sidebar_layout.addWidget(
            self.compare_button
        )

        sidebar_layout.addWidget(
            self.statistics_button
        )

        sidebar_layout.addStretch()

        self.pages = QStackedWidget()

        self.welcome_page = (
            WelcomePage()
        )

        self.analysis_page = (
            AnalysisPage()
        )

        self.export_page = (
            ExportPage()
        )

        self.pages.addWidget(
            self.welcome_page
        )

        self.pages.addWidget(
            self.analysis_page
        )

        self.pages.addWidget(
            self.export_page
        )

        self.new_analysis_button.clicked.connect(
            lambda:
            self.pages.setCurrentWidget(
                self.analysis_page
            )
        )

        self.export_button.clicked.connect(
            lambda:
            self.pages.setCurrentWidget(
                self.export_page
            )
        )

        if hasattr(
            self.welcome_page,
            "new_button"
        ):

            self.welcome_page.new_button.clicked.connect(
                lambda:
                self.pages.setCurrentWidget(
                    self.analysis_page
                )
            )

        self.analysis_page.analysis_completed.connect(
            self.analysis_completed
        )

        main_layout.addWidget(
            sidebar
        )

        main_layout.addWidget(
            self.pages
        )

    def analysis_completed(
        self,
        results,
        recording_name,
        method
    ):

        self.export_page.set_results(
            results,
            recording_name,
            method
        )

        self.pages.setCurrentWidget(
            self.analysis_page
        )
