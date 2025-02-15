import ctypes
from ctypes import wintypes

# Gerekli WinAPI fonksiyonlarını ve türlerini tanımla
user32 = ctypes.WinDLL('user32', use_last_error=True)
kernel32 = ctypes.WinDLL('kernel32', use_last_error=True)

# Pencere başlıklarını almak için buffer boyutu
n_max_count = 256

# EnumWindows işlevi ve diğer yardımcı fonksiyonlar
EnumWindows = user32.EnumWindows
EnumWindowsProc = ctypes.WINFUNCTYPE(ctypes.c_bool, wintypes.HWND, wintypes.LPARAM)
GetWindowText = user32.GetWindowTextW
GetWindowTextLength = user32.GetWindowTextLengthW
IsWindowVisible = user32.IsWindowVisible

def get_window_titles():
    titles = []

    # Callback fonksiyonu
    def enum_windows_callback(hwnd, lParam):
        if IsWindowVisible(hwnd):  # Sadece görünür pencereleri kontrol et
            length = GetWindowTextLength(hwnd)
            if length > 0:  # Başlık boş değilse
                buffer = ctypes.create_unicode_buffer(length + 1)
                GetWindowText(hwnd, buffer, length + 1)
                titles.append(buffer.value)
        return True

    # Callback işleviyle tüm pencereleri dolaş
    EnumWindows(EnumWindowsProc(enum_windows_callback), 0)
    return titles

# Pencere isimlerini al ve yazdır
window_titles = get_window_titles()
for title in window_titles:
    print(title)
