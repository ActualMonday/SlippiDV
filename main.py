import subprocess
import sys
import time
from PyQt5.QtWidgets import QApplication, QFileDialog
from PyQt5.QtWebEngineWidgets import QWebEngineView

def main():
    qt_app = QApplication([])

    # ---- Step 1: Ask user for .dat file ----
    file_dialog = QFileDialog()
    file_path, _ = file_dialog.getOpenFileName(
        None,
        'Select "SlippiDV_FullData.dat" file',
        ".",
        "Data Files (*.dat);;All Files (*)"
    )

    if not file_path:
        print("No file selected.")
        return

    # ---- Step 2: Start Bokeh server with file path passed as an argument ----
    bokeh_proc = subprocess.Popen([
        sys.executable, "-m", "bokeh", "serve", "app",
        "--allow-websocket-origin=localhost:5006",
        "--args", f"file={file_path}"
    ])

    # Give server time to start
    time.sleep(2)

    # ---- Step 3: Launch Qt window with embedded browser ----
    view = QWebEngineView()
    view.load("http://localhost:5006/app")
    view.setWindowTitle("Data Visualizer")
    view.show()

    qt_app.exec_()

    # Close Bokeh server when Qt exits
    bokeh_proc.terminate()

if __name__ == "__main__":
    main()