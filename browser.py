import sys
import os
import json
from PyQt5.QtWidgets import (
    QApplication,
    QMainWindow,
    QLineEdit,
    QToolBar,
    QAction,
    QMenu,
    QToolButton,
    QWidget,
    QSizePolicy
)
from PyQt5.QtWebEngineWidgets import QWebEngineView
from PyQt5.QtCore import QUrl
from PyQt5.QtGui import QFont

class RetroBrowser(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Wiby Navigator 1.0")
        self.resize(800, 600)
        self.setStyleSheet("""
            QMainWindow {
                background-color: #C0C0C0;
            }
            QToolBar {
                background-color: #E0E0E0;
                padding: 4px;
                spacing: 4px;
            }
            QLineEdit {
                background-color: white;
                border: 1px solid gray;
                font-family: 'Courier New';
                padding: 2px;
            }
            QPushButton, QToolButton {
                background-color: #D0D0D0;
                border: 1px solid gray;
                font-family: 'Courier New';
                padding: 2px 6px;
            }
        """)

        font = QFont("Courier New", 9)

        # ── Web View ─────────────────────────────────────────────────────────────
        self.browser = QWebEngineView()
        self.browser.setUrl(QUrl("https://wiby.org"))
        self.setCentralWidget(self.browser)

        # ── Toolbar Setup ───────────────────────────────────────────────────────
        nav_bar = QToolBar("Navigation")
        nav_bar.setFont(font)
        self.addToolBar(nav_bar)

        # Back button
        back_btn = QAction("[Back]", self)
        back_btn.triggered.connect(self.browser.back)
        nav_bar.addAction(back_btn)

        # Forward button
        forward_btn = QAction("[Forward]", self)
        forward_btn.triggered.connect(self.browser.forward)
        nav_bar.addAction(forward_btn)

        # Reload button
        reload_btn = QAction("[Reload]", self)
        reload_btn.triggered.connect(self.browser.reload)
        nav_bar.addAction(reload_btn)

        # ── Left Spacer to push URL bar toward center ──────────────────────────
        left_spacer = QWidget()
        left_spacer.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        nav_bar.addWidget(left_spacer)

        # ── URL Bar ────────────────────────────────────────────────────────────
        self.url_bar = QLineEdit()
        self.url_bar.setFont(font)
        self.url_bar.returnPressed.connect(self.navigate_to_url)
        nav_bar.addWidget(self.url_bar)

        # ── Right Spacer to finish centering URL bar ─────────────────────────
        right_spacer = QWidget()
        right_spacer.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        nav_bar.addWidget(right_spacer)

        # ── "Surprise Me" button (just left of bookmarks) ─────────────────────
        surprise_btn = QAction("[Surprise Me]", self)
        surprise_btn.triggered.connect(self.go_to_surprise)
        nav_bar.addAction(surprise_btn)

        # ── Bookmarks Setup ────────────────────────────────────────────────────

        # Dictionary to keep track of QAction for each bookmarked URL
        self.bookmark_actions = {}

        # "Bookmark This Page" button
        self.bookmark_action = QAction("[Bookmark]", self)
        self.bookmark_action.triggered.connect(self.bookmark_current_page)
        nav_bar.addAction(self.bookmark_action)

        # Retrieve the widget for styling when toggled
        self.bookmark_btn_widget = nav_bar.widgetForAction(self.bookmark_action)

        # "Bookmarks" dropdown menu button
        self.bookmark_menu_btn = QToolButton()
        self.bookmark_menu_btn.setText("[Bookmarks]")
        self.bookmark_menu_btn.setPopupMode(QToolButton.InstantPopup)
        self.bookmark_menu = QMenu()
        self.bookmark_menu_btn.setMenu(self.bookmark_menu)
        nav_bar.addWidget(self.bookmark_menu_btn)

        # ── Bookmark Persistence ────────────────────────────────────────────────
        self.bookmarks_file = os.path.join(os.path.dirname(__file__), 'bookmarks.json')
        self.bookmarks = []
        self.load_bookmarks()

        # ── URL Change Signal ───────────────────────────────────────────────────
        self.browser.urlChanged.connect(self.update_url)

        # Initialize bookmark button color based on the starting URL
        self.update_bookmark_button(self.browser.url().toString())

    def navigate_to_url(self):
        url = self.url_bar.text()
        if not url.startswith("http"):
            url = "http://" + url
        self.browser.setUrl(QUrl(url))

    def update_url(self, q):
        """
        Called whenever the browser's URL changes.
        Updates the URL bar and adjusts the bookmark button's appearance.
        """
        url_str = q.toString()
        self.url_bar.setText(url_str)
        self.update_bookmark_button(url_str)

    def go_to_surprise(self):
        self.browser.setUrl(QUrl("https://wiby.me/surprise/"))

    def load_bookmarks(self):
        """
        Load bookmarks from the JSON file (if it exists),
        populate the bookmarks menu, and set up QAction mappings.
        """
        if os.path.exists(self.bookmarks_file):
            try:
                with open(self.bookmarks_file, 'r') as f:
                    data = json.load(f)
                    if isinstance(data, list):
                        self.bookmarks = data
            except Exception:
                self.bookmarks = []
        else:
            self.bookmarks = []

        # Populate the bookmarks dropdown menu and mapping
        for url in self.bookmarks:
            action = QAction(url, self)
            action.triggered.connect(lambda checked, u=url: self.browser.setUrl(QUrl(u)))
            self.bookmark_menu.addAction(action)
            self.bookmark_actions[url] = action

    def save_bookmarks(self):
        """
        Save the current list of bookmarks to the JSON file.
        """
        try:
            with open(self.bookmarks_file, 'w') as f:
                json.dump(self.bookmarks, f)
        except Exception:
            pass

    def bookmark_current_page(self):
        """
        Toggle bookmark for the current URL:
        - If not bookmarked, add to bookmarks, create QAction, update menu.
        - If already bookmarked, remove from bookmarks, remove QAction, update menu.
        Then save to disk and update the bookmark button's appearance.
        """
        url = self.browser.url().toString()
        if not url:
            return

        if url in self.bookmarks:
            # Remove bookmark
            self.bookmarks.remove(url)
            action_to_remove = self.bookmark_actions.pop(url, None)
            if action_to_remove:
                self.bookmark_menu.removeAction(action_to_remove)
        else:
            # Add bookmark
            self.bookmarks.append(url)
            action = QAction(url, self)
            action.triggered.connect(lambda checked, u=url: self.browser.setUrl(QUrl(u)))
            self.bookmark_menu.addAction(action)
            self.bookmark_actions[url] = action

        self.save_bookmarks()
        self.update_bookmark_button(url)

    def update_bookmark_button(self, url):
        """
        Change the bookmark button's background color if the given URL
        is already in the bookmarks list; otherwise reset its style.
        """
        if url in self.bookmarks:
            # Gold background to indicate "bookmarked" state
            self.bookmark_btn_widget.setStyleSheet("background-color: #FFD700;")
        else:
            # Reset to default PyQt button style
            self.bookmark_btn_widget.setStyleSheet("")

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = RetroBrowser()
    window.show()
    sys.exit(app.exec_())
