# clipboard_monitor.py

import time  # Used for adding a delay between clipboard polls
import hashlib  # For creating a unique fingerprint of text content
import pyperclip  # Cross-platform clipboard access for text
from PIL import ImageGrab  # Used to grab images from the system clipboard
from storage import save_clipboard_item  # Function to save clipboard items into storage
from ocr import extract_text_from_image  # Function to perform OCR on image content

class ClipboardMonitor:
    def __init__(self, poll_interval=1):
        """
        Initializes the ClipboardMonitor.
        :param poll_interval: How often to check the clipboard (in seconds)
        """
        self.last_hash = None  # Stores the last clipboard content hash to avoid duplicates
        self.poll_interval = poll_interval  # Defines how often we poll the clipboard

    def hash_content(self, content):
        """
        Creates a hash of the given content to detect changes.
        :param content: String content from clipboard
        :return: SHA-256 hash of the content
        """
        return hashlib.sha256(content.encode("utf-8")).hexdigest()

    def run(self):
        """
        Starts the clipboard monitoring loop. It checks for new text or images in the clipboard,
        hashes the text to detect changes, performs OCR on images, and saves all unique items.
        """
        print("[ClipboardMonitor] Started.")  # Log start

        while True:
            # ---- TEXT CLIPBOARD HANDLING ----
            try:
                clipboard_content = pyperclip.paste()  # Get current clipboard content (text)
                
                if clipboard_content:  # Only proceed if content is not empty
                    content_hash = self.hash_content(clipboard_content)  # Create a hash of the content

                    if content_hash != self.last_hash:  # Check if it's new content
                        self.last_hash = content_hash  # Update last seen hash
                        print(f"[ClipboardMonitor] New text detected: {clipboard_content[:50]}...")  # Log new text

                        # Save text content to history
                        save_clipboard_item("text", clipboard_content)

            except Exception as e:
                # Catch unexpected errors in text reading
                print(f"[ClipboardMonitor] Text check failed: {e}")

            # ---- IMAGE CLIPBOARD HANDLING ----
            try:
                image = ImageGrab.grabclipboard()  # Attempt to grab an image from clipboard

                # If an image is successfully retrieved and is a PIL Image object
                if isinstance(image, ImageGrab.Image.Image):
                    print("[ClipboardMonitor] New image detected.")  # Log image detection

                    # Extract text from the image using OCR
                    extracted_text = extract_text_from_image(image)

                    # Save image and extracted text
                    save_clipboard_item("image", extracted_text, image=image)

            except Exception as e:
                # Catch unexpected errors in image reading or OCR
                print(f"[ClipboardMonitor] Image check failed: {e}")

            # Wait for the next polling cycle
            time.sleep(self.poll_interval)
