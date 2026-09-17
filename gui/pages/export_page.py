from pathlib import Path

from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QFileDialog,
    QLineEdit,
    QGroupBox,
    QCheckBox,
)


class ExportPage(QWidget):

    def __init__(self):

        super().__init__()

        self.results = None
        self.recording_name = None
        self.method = None
        self.output_folder = None

        self._build_ui()
        
    def _build_ui(self):

        layout = QVBoxLayout(
            self
        )

        title = QLabel(
            "Export Results"
        )

        title.setStyleSheet("""
            QLabel {
                font-size: 26px;
                font-weight: bold;
            }
        """)

        layout.addWidget(
            title
        )

        analysis_group = QGroupBox(
            "Analysis"
        )

        analysis_layout = QVBoxLayout(
            analysis_group
        )

        self.recording_label = QLabel(
            "Recording: —"
        )

        self.method_label = QLabel(
            "Detection method: —"
        )

        analysis_layout.addWidget(
            self.recording_label
        )

        analysis_layout.addWidget(
            self.method_label
        )

        layout.addWidget(
            analysis_group
        )

        output_group = QGroupBox(
            "Output folder"
        )

        output_layout = QHBoxLayout(
            output_group
        )

        self.output_edit = QLineEdit()

        self.output_edit.setReadOnly(
            True
        )

        browse_button = QPushButton(
            "Browse..."
        )

        browse_button.clicked.connect(
            self.select_output_folder
        )

        output_layout.addWidget(
            self.output_edit
        )

        output_layout.addWidget(
            browse_button
        )

        layout.addWidget(
            output_group
        )

        format_group = QGroupBox(
            "Export formats"
        )

        format_layout = QVBoxLayout(
            format_group
        )

        self.excel_check = QCheckBox(
            "Excel workbook"
        )

        self.csv_check = QCheckBox(
            "CSV files"
        )

        self.pdf_check = QCheckBox(
            "PDF report"
        )

        self.excel_check.setChecked(
            True
        )

        self.pdf_check.setChecked(
            True
        )

        format_layout.addWidget(
            self.excel_check
        )

        format_layout.addWidget(
            self.csv_check
        )

        format_layout.addWidget(
            self.pdf_check
        )

        layout.addWidget(
            format_group
        )

        self.export_button = QPushButton(
            "Export Results"
        )

        self.export_button.setMinimumHeight(
            45
        )

        self.export_button.clicked.connect(
            self.export_results
        )

        layout.addSpacing(
            20
        )

        layout.addWidget(
            self.export_button
        )


        self.status_label = QLabel(
            "Ready"
        )

        layout.addWidget(
            self.status_label
        )

        layout.addStretch()

    def select_output_folder(self):

        folder = QFileDialog.getExistingDirectory(
            self,
            "Select output folder"
        )

        if not folder:
            return

        self.output_folder = Path(
            folder
        )

        self.output_edit.setText(
            str(self.output_folder)
        )

    def set_results(
        self,
        results,
        recording_name,
        method
    ):

        self.results = results

        self.recording_name = (
            recording_name
        )

        self.method = method

        self.recording_label.setText(
            f"Recording: {recording_name}"
        )

        self.method_label.setText(
            f"Detection method: {method}"
        )

        self.status_label.setText(
            "Analysis results ready for export."
        )

    def export_results(self):

        if self.results is None:

            self.status_label.setText(
                "No analysis results available."
            )

            return

        if self.output_folder is None:

            self.status_label.setText(
                "Please select an output folder."
            )

            return

        if not any([
            self.excel_check.isChecked(),
            self.csv_check.isChecked(),
            self.pdf_check.isChecked(),
        ]):

            self.status_label.setText(
                "Select at least one export format."
            )

            return

        self.status_label.setText(
            "Export options selected."
        )
