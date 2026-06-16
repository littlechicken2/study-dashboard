import ctypes
import json
import time
import urllib.request
from ctypes import wintypes


API = "http://127.0.0.1:8765/api/activity-ping"
POLL_SECONDS = 5

user32 = ctypes.WinDLL("user32", use_last_error=True)
kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)


class LASTINPUTINFO(ctypes.Structure):
    _fields_ = [("cbSize", wintypes.UINT), ("dwTime", wintypes.DWORD)]


def idle_seconds():
    info = LASTINPUTINFO()
    info.cbSize = ctypes.sizeof(info)
    user32.GetLastInputInfo(ctypes.byref(info))
    return max(0, (kernel32.GetTickCount() - info.dwTime) / 1000)


def foreground_info():
    hwnd = user32.GetForegroundWindow()
    pid = wintypes.DWORD()
    user32.GetWindowThreadProcessId(hwnd, ctypes.byref(pid))
    title_len = user32.GetWindowTextLengthW(hwnd) + 1
    title = ctypes.create_unicode_buffer(title_len)
    user32.GetWindowTextW(hwnd, title, title_len)
    handle = kernel32.OpenProcess(0x1000, False, pid.value)
    exe = ""
    if handle:
        buf = ctypes.create_unicode_buffer(1024)
        size = wintypes.DWORD(len(buf))
        if kernel32.QueryFullProcessImageNameW(handle, 0, buf, ctypes.byref(size)):
            exe = buf.value.rsplit("\\", 1)[-1].lower()
        kernel32.CloseHandle(handle)
    return exe, title.value


def classify(exe, title, idle):
    if idle > 60:
        return None
    if exe in {"anki.exe"}:
        return "verb", "anki-desktop"
    if exe in {"acrobat.exe", "acrord32.exe"}:
        return "grammar", "adobe-acrobat"
    return None


def post(payload):
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(API, data=data, headers={"Content-Type": "application/json"}, method="POST")
    try:
        urllib.request.urlopen(req, timeout=2).read()
    except OSError:
        pass


def main():
    while True:
        start = time.time()
        exe, title = foreground_info()
        idle = idle_seconds()
        result = classify(exe, title, idle)
        if result:
            category, source = result
            post({
                "category": category,
                "source": source,
                "seconds": POLL_SECONDS,
                "title": title[:120],
                "idleSeconds": round(idle, 1),
                "capturedAt": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
            })
        time.sleep(max(1, POLL_SECONDS - (time.time() - start)))


if __name__ == "__main__":
    main()
