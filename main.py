# main.py

import sys
import threading
from PyQt5.QtWidgets import QApplication
from gui import ClipboardManagerApp
from clipboard_monitor import ClipboardMonitor
import qt_material  # ✅ New: import theme library

def start_clipboard_monitor():
    monitor = ClipboardMonitor()
    monitor.run()

def main():
    # Start clipboard monitoring in a separate thread
    monitor_thread = threading.Thread(target=start_clipboard_monitor, daemon=True)
    monitor_thread.start()

    # Start the GUI app
    app = QApplication(sys.argv)

    # ✅ Apply a modern Material theme (dark_teal is a great one to start with)
    qt_material.apply_stylesheet(app, theme='dark_teal.xml')

    window = ClipboardManagerApp()
    window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
