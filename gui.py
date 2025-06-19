# gui.py

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QListWidget, QListWidgetItem, QHBoxLayout,
    QPushButton, QLineEdit, QAbstractItemView, QSpacerItem, QSizePolicy, QFrame
)
from PyQt5.QtGui import QPixmap, QIcon, QMouseEvent, QFont
from PyQt5.QtCore import Qt, QSize, QPoint, QTimer
import os
from storage import fetch_all_items, clear_all_items
import pyperclip

class ClipboardManagerApp(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowFlags(Qt.FramelessWindowHint)
        self.setStyleSheet("background-color: #121212; color: #eeeeee; font-family: 'Segoe UI';")

        self.setMinimumSize(800, 600)
        self.mouse_click_pos = None

        # === Main Layout ===
        self.layout = QVBoxLayout()
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(self.layout)

        # === Custom Top Bar ===
        self.top_bar = QHBoxLayout()
        self.top_bar.setContentsMargins(10, 6, 10, 6)

        self.title = QLabel("ClipSage")
        self.title.setStyleSheet("color: #ffffff; font-size: 16px;")
        self.top_bar.addWidget(self.title)

        self.top_bar.addSpacerItem(QSpacerItem(20, 10, QSizePolicy.Expanding, QSizePolicy.Minimum))

        self.minimize_button = QPushButton("–")
        self.minimize_button.setFixedSize(24, 24)
        self.minimize_button.setStyleSheet("background-color: #333; color: white; border: none;")
        self.minimize_button.clicked.connect(self.showMinimized)
        self.top_bar.addWidget(self.minimize_button)

        self.close_button = QPushButton("✕")
        self.close_button.setFixedSize(24, 24)
        self.close_button.setStyleSheet("background-color: #c62828; color: white; border: none;")
        self.close_button.clicked.connect(self.close)
        self.top_bar.addWidget(self.close_button)

        self.layout.addLayout(self.top_bar)

        # === Search + Refresh + Reset Buttons ===
        self.search_row = QHBoxLayout()

        self.search_bar = QLineEdit()
        self.search_bar.setPlaceholderText("🔎 Search clipboard history...")
        self.search_bar.setStyleSheet("padding: 6px; border-radius: 4px; background-color: #1e1e1e; color: white;")
        self.search_bar.textChanged.connect(self.load_clipboard_items)
        self.search_row.addWidget(self.search_bar)

        refresh_btn = QPushButton("🔄 Refresh")
        refresh_btn.setStyleSheet("background-color: #333; color: white; padding: 6px;")
        refresh_btn.clicked.connect(self.load_clipboard_items)
        self.search_row.addWidget(refresh_btn)

        reset_btn = QPushButton("🗑 Reset")
        reset_btn.setStyleSheet("background-color: #444; color: white; padding: 6px;")
        reset_btn.clicked.connect(self.reset_history)
        self.search_row.addWidget(reset_btn)

        self.layout.addLayout(self.search_row)

        # === Clipboard History List ===
        self.list_widget = QListWidget()
        self.list_widget.setSelectionMode(QAbstractItemView.MultiSelection)
        self.list_widget.itemClicked.connect(self.handle_item_click)
        self.list_widget.setStyleSheet("""
            QListWidget {
                background-color: #1e1e1e;
                border: none;
            }
            QListWidget::item {
                padding: 8px;
            }
            QListWidget::item:selected {
                background-color: #3949ab;
            }
        """)
        self.layout.addWidget(self.list_widget)

        # === Copy All Selected Button ===
        self.copy_all_btn = QPushButton("📋 Copy All Selected")
        self.copy_all_btn.setStyleSheet("background-color: #00acc1; color: white; padding: 10px;")
        self.copy_all_btn.clicked.connect(self.copy_all_selected)
        self.layout.addWidget(self.copy_all_btn)

        # === Toast Notification Widget ===
        self.toast = QLabel("", self)
        self.toast.setStyleSheet("""
            background-color: #222;
            color: white;
            padding: 10px 20px;
            border-radius: 8px;
        """)
        self.toast.setAlignment(Qt.AlignCenter)
        self.toast.setVisible(False)

        self.load_clipboard_items()

    def show_toast(self, message):
        """
        Shows a fading message in the bottom-right corner.
        """
        self.toast.setText(message)
        self.toast.adjustSize()
        self.toast.move(self.width() - self.toast.width() - 30, self.height() - self.toast.height() - 30)
        self.toast.setVisible(True)
        QTimer.singleShot(2200, lambda: self.toast.setVisible(False))

    def load_clipboard_items(self):
        """
        Load clipboard history from storage, apply search filter.
        """
        self.list_widget.clear()
        search_term = self.search_bar.text().lower()
        items = fetch_all_items()

        for item in items:
            if search_term and search_term not in (item['content'] or '').lower():
                continue

            display_text = f"[{item['type'].upper()}] {item['timestamp']}"
            list_item = QListWidgetItem()

            if item["type"] == "text":
                preview = (item["content"] or "")[:100].replace("\n", " ")
                list_item.setText(f"{display_text}\n{preview}")
                list_item.setData(Qt.UserRole, item)

            elif item["type"] == "image":
                label = item["content"] or "(No OCR)"
                image_path = item["image_path"]
                list_item.setText(f"{display_text}\n🖼️ {label[:100]}")
                list_item.setData(Qt.UserRole, item)

                if image_path and os.path.exists(image_path):
                    pixmap = QPixmap(image_path).scaled(QSize(64, 64), Qt.KeepAspectRatio)
                    list_item.setIcon(QIcon(pixmap))

            self.list_widget.addItem(list_item)

    def handle_item_click(self, list_item):
        """
        Copy clicked item to clipboard (text or image OCR).
        """
        item = list_item.data(Qt.UserRole)
        if not item:
            return

        if item["type"] == "text":
            pyperclip.copy(item["content"] or "")
            self.show_toast("✅ Text copied")

        elif item["type"] == "image" and item["content"]:
            pyperclip.copy(item["content"])
            self.show_toast("🖼️ OCR copied")

    def copy_all_selected(self):
        """
        Combine selected items and copy to clipboard.
        """
        selected_items = self.list_widget.selectedItems()
        if not selected_items:
            self.show_toast("⚠️ No selection")
            return

        combined = ""
        for item in selected_items:
            data = item.data(Qt.UserRole)
            if data["type"] == "text":
                combined += (data["content"] or "") + "\n\n"
            elif data["type"] == "image" and data["content"]:
                combined += data["content"] + "\n\n"

        if combined.strip():
            pyperclip.copy(combined.strip())
            self.show_toast("📋 Combined content copied")
        else:
            self.show_toast("⚠️ Nothing to copy")

    def reset_history(self):
        """
        Clears all saved clipboard entries (with confirmation).
        """
        clear_all_items()
        self.load_clipboard_items()
        self.show_toast("🗑 History cleared")

    # === Drag Support ===
    def mousePressEvent(self, event: QMouseEvent):
        if event.button() == Qt.LeftButton:
            self.mouse_click_pos = event.globalPos() - self.frameGeometry().topLeft()
            event.accept()

    def mouseMoveEvent(self, event: QMouseEvent):
        if self.mouse_click_pos and event.buttons() == Qt.LeftButton:
            self.move(event.globalPos() - self.mouse_click_pos)
            event.accept()

    def mouseReleaseEvent(self, event: QMouseEvent):
        self.mouse_click_pos = None
