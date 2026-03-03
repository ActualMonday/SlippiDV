import sys
import threading
import time
from PyQt5.QtWidgets import QApplication, QMainWindow, QFileDialog
from PyQt5.QtWebEngineWidgets import QWebEngineView
from PyQt5.QtCore import QUrl

from bokeh.server.server import Server
from bokeh.application import Application
from bokeh.application.handlers.script import ScriptHandler



def start_bokeh():
    def _run():
        import sys, os
        sys.path.insert(0, os.path.abspath("app"))  # make `app/` top-level
        
        import asyncio

        asyncio.set_event_loop(asyncio.new_event_loop())  # <<< FIX

        handler = ScriptHandler(filename="app/app.py")
        app = Application(handler)

        server = Server(
            {"/app": app},
            port=5006,
            allow_websocket_origin=["localhost:5006"],
        )
        server.start()
        server.io_loop.start()

    t = threading.Thread(target=_run, daemon=True)
    t.start()


def main():
    # Standard PyQt5 init
    app = QApplication(sys.argv)
    """
    # ---- Step 1: Ask user for file ----
    file_dialog = QFileDialog()
    file_path, _ = file_dialog.getOpenFileName(
        None,
        'Select "SlippiDV_FullData.json" file',
        ".",
        "Data Files (*.json);;All Files (*)",
    )

    if not file_path:
        print("No file selected.")
        return
    """
    # Start server
    start_bokeh()

    

    window = QMainWindow()
    window.setWindowTitle("Slippi Data Visualizer")
    window.resize(1920, 1080)

    view = QWebEngineView()


    # Point to local server route; app.py handles file selection
    view.load(QUrl("http://localhost:5006/app"))
    window.setCentralWidget(view)
    window.show()

    sys.exit(app.exec_())


if __name__ == "__main__":
    main()


