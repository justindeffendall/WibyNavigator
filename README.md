Dependencies (paste into terminal):

pip install pyqt5 pyqtwebengine pyinstaller

To create .exe:

python -m PyInstaller --noconsole --onefile --add-data "bookmarks.json;." --name WibyNavigator browser.py