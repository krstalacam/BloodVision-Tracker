from PyQt5 import QtWidgets, QtGui, QtCore
import sys
import ctypes


class RedHighlightOverlay(QtWidgets.QWidget):
    def __init__(self, screen_geometry):
        super().__init__()
        self.screen_geometry = screen_geometry
        self.initUI()

    def initUI(self):
        # Pencereyi seçilen monitörün geometrisine ayarla
        self.setWindowFlags(
            QtCore.Qt.WindowType.FramelessWindowHint |
            QtCore.Qt.WindowType.WindowStaysOnTopHint |
            QtCore.Qt.WindowType.Tool
        )
        self.setAttribute(QtCore.Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setAttribute(QtCore.Qt.WidgetAttribute.WA_NoSystemBackground)
        self.setGeometry(self.screen_geometry)

        # Tıklanamaz pencere
        self.make_window_clickthrough()

    def make_window_clickthrough(self):
        hwnd = self.winId()
        hwnd = int(hwnd)

        # Mevcut pencere stilini oku
        styles = ctypes.windll.user32.GetWindowLongW(hwnd, -20)  # GWL_EXSTYLE
        ctypes.windll.user32.SetWindowLongW(hwnd, -20, styles | 0x00000020)  # WS_EX_TRANSPARENT

    def paintEvent(self, event):
        painter = QtGui.QPainter(self)
        painter.setRenderHint(QtGui.QPainter.Antialiasing)

        # Arka plan gri tonlaması
        painter.setBrush(QtGui.QColor(0, 0, 0, 155))  # Yarı saydam gri renk
        painter.setPen(QtCore.Qt.PenStyle.NoPen)
        painter.drawRect(self.rect())

        # Kırmızı vurgulama
        highlight_color = QtGui.QColor(255, 0, 0, 255)  # Parlak kırmızı
        painter.setBrush(highlight_color)

        # Kırmızı daire (merkezde)
        screen = self.rect()
        painter.drawEllipse(screen.center(), 150, 150)
        painter.end()


def choose_screen(app):
    # Kullanıcıya ekran seçimi yaptıran bir dialog
    screens = app.screens()
    screen_options = [f"Ekran {i + 1}: {screen.geometry()}" for i, screen in enumerate(screens)]

    # Seçim penceresi oluştur
    dialog = QtWidgets.QInputDialog()
    dialog.setWindowTitle("Ekran Seçimi")
    dialog.setLabelText("Görüntülenecek ekranı seçin:")
    dialog.setComboBoxItems(screen_options)
    dialog.resize(300, 100)

    if dialog.exec_() == QtWidgets.QDialog.Accepted:
        selected_index = dialog.textValue()
        selected_screen_index = screen_options.index(selected_index)
        return screens[selected_screen_index].geometry()
    else:
        return None


def main():
    app = QtWidgets.QApplication(sys.argv)

    # Ekran seçimini yap
    selected_screen_geometry = choose_screen(app)
    if not selected_screen_geometry:
        print("Ekran seçilmedi. Çıkılıyor.")
        sys.exit(0)

    # Overlay'i seçilen ekran üzerinde göster
    overlay = RedHighlightOverlay(selected_screen_geometry)
    overlay.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
