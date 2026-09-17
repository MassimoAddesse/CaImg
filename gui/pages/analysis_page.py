from pathlib import Path
from PySide6.QtCore import Signal
from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QFileDialog,
    QLineEdit,
    QComboBox,
    QGroupBox,
    QMessageBox,
    QProgressBar,
    QTextEdit
)

from PySide6.QtCore import QThread

from gui.analysis_worker import AnalysisWorker

class AnalysisPage(QWidget):
        
    analysis_completed = Signal(
    object,
    str,
    str
    )
        
    def __init__(self):
        super().__init__()

        self.tiff_path = None
        self.output_folder = None

        self.thread = None
        self.worker = None

        self._build_ui()

    def _build_ui(self):

        layout = QVBoxLayout(
            self
        )

        title = QLabel(
            "New Analysis"
        )

        title.setStyleSheet(
            """
            QLabel {
                font-size: 26px;
                font-weight: bold;
            }
            """
        )

        layout.addWidget(
            title
        )

        input_group = QGroupBox(
            "Input"
        )

        input_layout = QVBoxLayout(
            input_group
        )

        file_layout = QHBoxLayout()

        self.file_edit = QLineEdit()

        self.file_edit.setPlaceholderText(
            "Select a TIFF recording..."
        )

        self.file_edit.setReadOnly(
            True
        )

        self.browse_button = QPushButton(
            "Browse..."
        )

        self.browse_button.clicked.connect(
            self.select_tiff
        )

        file_layout.addWidget(
            self.file_edit
        )

        file_layout.addWidget(
            self.browse_button
        )

        input_layout.addLayout(
            file_layout
        )

        output_layout = QHBoxLayout()


        self.output_edit = QLineEdit()

        self.output_edit.setPlaceholderText(
            "Select output folder..."
        )

        self.output_edit.setReadOnly(
            True
        )

        self.output_button = QPushButton("Browse...")
        self.output_button.clicked.connect(
            self.select_output_folder
        )

        output_layout.addWidget(
            self.output_edit
        )
        output_layout.addWidget(
            self.output_button
        )

        input_layout.addLayout(
            output_layout
        )

        layout.addWidget(
            input_group
        )

        recording_group = QGroupBox(
            "Recording"
        )

        recording_layout = QHBoxLayout(
            recording_group
        )

        recording_layout.addWidget(
            QLabel("Frame rate:")
        )

        self.frame_rate_edit = QLineEdit(
            "4.0"
        )

        self.frame_rate_edit.setMaximumWidth(
            100
        )

        recording_layout.addWidget(
            self.frame_rate_edit
        )

        recording_layout.addWidget(
            QLabel("Hz")
        )

        recording_layout.addStretch()

        layout.addWidget(
            recording_group
        )

        detection_group = QGroupBox(
            "Event Detection"
        )

        detection_layout = QHBoxLayout(
            detection_group
        )

        detection_layout.addWidget(
            QLabel("Method:")
        )

        self.method_combo = QComboBox()

        self.method_combo.addItems(
            [
                "Adaptive STD",
                "Adaptive MAD",
                "SG + Prominence"
            ]
        )

        detection_layout.addWidget(
            self.method_combo
        )

        detection_layout.addStretch()

        layout.addWidget(
            detection_group
        )

        self.analyze_button = QPushButton(
            "Run Analysis"
        )

        self.analyze_button.setMinimumHeight(
            45
        )

        self.analyze_button.clicked.connect(
            self.run_analysis
        )

        layout.addSpacing(
            20
        )

        layout.addWidget(
            self.analyze_button
        )

        self.progress_bar = QProgressBar()

        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        self.progress_bar.setVisible(False)

        layout.addWidget(
            self.progress_bar
        )

        self.status_label = QLabel(
              "Ready"
        )

        self.status_label.setStyleSheet(
              """
                font-size: 15px;
                font-weight: bold;
              """
        )

        layout.addWidget(
              self.status_label
        )

        self.detail_label = QLabel(
              ""
        )

        self.detail_label.setStyleSheet(
              """
                QLabel{
                    font-size: 13px;
                }
              """
        )

        layout.addWidget(
              self.detail_label
        )

        self.activity_log = QTextEdit()

        self.activity_log.setReadOnly(True)
        self.activity_log.setMaximumHeight(180)

        self.activity_log.setPlaceholderText(
            "Analysis progress will appear here..."
        )

        layout.addWidget(self.activity_log)

        self.status_label = QLabel(
            "Ready"
        )

        layout.addWidget(
            self.status_label
        )

        layout.addStretch()


    def select_tiff(self):

        path, _ = QFileDialog.getOpenFileName(
            self,
            "Select TIFF recording",
            "",
            "TIFF files (*.tif *.tiff)"
        )

        if not path:
            return

        self.tiff_path = Path(
            path
        )

        self.file_edit.setText(
            str(self.tiff_path)
        )

        self.status_label.setText(
            "TIFF file selected."
        )

        if self.output_folder is None:

            self.output_folder = (
                self.tiff_path.parent
            )

            self.output_edit.setText(
                str(self.output_folder)
            )

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
            str(
                self.output_folder
            )
        )

    def validate_inputs(self):

        if self.tiff_path is None:

            QMessageBox.warning(
                self,
                "Missing input",
                "Please select a TIFF recording."
            )

            return False

        try:

            frame_rate = float(
                self.frame_rate_edit.text()
            )

        except ValueError:

            QMessageBox.warning(
                self,
                "Invalid frame rate",
                "Frame rate must be a number."
            )

            return False

        if frame_rate <= 0:

            QMessageBox.warning(
                self,
                "Invalid frame rate",
                "Frame rate must be greater than zero."
            )

            return False

        if self.output_folder is None:

            QMessageBox.warning(
                self,
                "Missing output folder",
                "Please select an output folder."
            )

            return False

        return True

    def run_analysis(self):

        if not self.validate_inputs():
            return

        frame_rate = float(
            self.frame_rate_edit.text()
        )

        method = self.method_combo.currentText()

        self.analyze_button.setEnabled(False)
        self.browse_button.setEnabled(False)
        self.output_button.setEnabled(False)

        self.method_combo.setEnabled(False)
        self.frame_rate_edit.setEnabled(False)

        self.progress_bar.setValue(0)
        self.progress_bar.setVisible(True)

        self.status_label.setText(
            "Starting analysis..."
        )

        self.detail_label.setText(
            ""
        )

        self.activity_log.clear()

        self.thread = QThread()

        self.worker = AnalysisWorker(
            tiff_path = str(self.tiff_path),
            method = method,
            frame_rate = frame_rate
        )

        self.worker.progress.connect(
            self.progress_bar.setValue
        )

        self.worker.status.connect(
            self.update_status
        )

        self.worker.detail.connect(
            self.update_detail
        )

        self.worker.finished.connect(
            self.analysis_finished
        )

        self.worker.error.connect(
            self.analysis_error
        )

        self.worker.moveToThread(
            self.thread
        )

        self.thread.started.connect(
            self.worker.run
        )

        self.worker.status.connect(
            self.update_status
        )

        self.worker.progress.connect(
                    self.update_progress
                )

        self.worker.finished.connect(
            self.analysis_finished
        )

        self.worker.error.connect(
            self.analysis_error
        )

        self.worker.finished.connect(
            self.thread.quit
        )

        self.worker.error.connect(
            self.thread.quit
        )

        self.thread.finished.connect(
            self.thread_finished
        )

        self.thread.start()

    def update_status(self, message):

        self.status_label.setText(
            message
        )

        self.activity_log.append(
            f" • {message}"
        )

    def update_progress(self, value):

        self.progress_bar.setValue(value)

    def analysis_finished(self, results):

        self.progress_bar.setValue(
            100
        )

        self.status_label.setText(
            "Analysis completed"
        )

        self.detail_label.setText(
            "Analysis completed successfully."
        )

        self.activity_log.append(
            "✓ Analysis completed successfully."
        )

        recording_name = (
            self.tiff_path.name
        )

        method = (
            self.method_combo.currentText()
        )

        self.analysis_completed.emit(
            results,
            recording_name,
            method
        )

    def analysis_error(self, message):

        self.status_label.setText(
            "Analysis failed"
        )

        self.detail_label.setText(
            message
        )

        self.activity_log.append(
            f"✗ {message}"
        )

        self.progress_bar.setVisible(
            False
        )

    def thread_finished(self):

        self.analyze_button.setEnabled(True)
        self.browse_button.setEnabled(True)
        self.output_button.setEnabled(True)

        self.method_combo.setEnabled(True)
        self.frame_rate_edit.setEnabled(True)

        self.worker.deleteLater()
        self.thread.deleteLater()

        self.worker = None
        self.thread = None

    def update_status(self, message):

        self.status_label.setText(
            message
        )

        self.activity_log.append(
            f"→ {message}"
        )

        scrollbar = (
            self.activity_log
            .verticalScrollBar()
        )

        scrollbar.setValue(
            scrollbar.maximum()
        )


    def update_detail(self, message):

        self.detail_label.setText(
            message
        )
