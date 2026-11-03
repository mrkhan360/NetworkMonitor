import tkinter as tk
from tkinter import messagebox
import time
import threading
import subprocess
import socket
import psutil

APP_TITLE = "Network Monitor"
REFRESH_MS = 1000
PING_HOST = "1.1.1.1"

class NetworkMonitor:
    def __init__(self, root):
        self.root = root
        self.root.title(APP_TITLE)
        self.root.overrideredirect(True)
        self.root.attributes("-topmost", True)
        self.root.configure(bg="#151a22")
        self.root.resizable(False, False)

        self.last = psutil.net_io_counters()
        self.last_time = time.time()
        self.ping_text = "Checking..."
        self.connected = self.check_connection()

        self.download_var = tk.StringVar(value="↓ 0.00 MB/s")
        self.upload_var = tk.StringVar(value="↑ 0.00 MB/s")
        self.status_var = tk.StringVar(value="● Connected" if self.connected else "● Offline")
        self.ping_var = tk.StringVar(value="Ping: -- ms")

        frame = tk.Frame(root, bg="#151a22", padx=12, pady=7,
                         highlightthickness=1, highlightbackground="#394354")
        frame.pack()

        tk.Label(frame, text="NET", fg="#9aa8bb", bg="#151a22",
                 font=("Segoe UI", 8, "bold")).pack(side="left", padx=(0, 9))
        tk.Label(frame, textvariable=self.download_var, fg="#65d68a", bg="#151a22",
                 font=("Segoe UI", 9, "bold")).pack(side="left", padx=(0, 12))
        tk.Label(frame, textvariable=self.upload_var, fg="#69b7ff", bg="#151a22",
                 font=("Segoe UI", 9, "bold")).pack(side="left", padx=(0, 12))
        tk.Label(frame, textvariable=self.ping_var, fg="#e5c879", bg="#151a22",
                 font=("Segoe UI", 8)).pack(side="left", padx=(0, 10))
        tk.Label(frame, textvariable=self.status_var, fg="#65d68a", bg="#151a22",
                 font=("Segoe UI", 8, "bold")).pack(side="left", padx=(0, 10))

        close = tk.Label(frame, text="×", fg="#aeb8c7", bg="#151a22",
                         font=("Segoe UI", 12, "bold"), cursor="hand2")
        close.pack(side="left")
        close.bind("<Button-1>", lambda _e: root.destroy())

        # Drag the compact monitor if it covers another item.
        for widget in (frame, *frame.winfo_children()):
            widget.bind("<Button-1>", self.start_drag, add="+")
            widget.bind("<B1-Motion>", self.do_drag, add="+")

        self.position_near_taskbar()
        self.update_stats()
        self.update_ping()

    def position_near_taskbar(self):
        self.root.update_idletasks()
        width = self.root.winfo_reqwidth()
        height = self.root.winfo_reqheight()
        sw = self.root.winfo_screenwidth()
        sh = self.root.winfo_screenheight()
        # A compact always-on-top strip just above the Windows taskbar.
        self.root.geometry(f"{width}x{height}+{sw-width-18}+{sh-height-58}")

    def start_drag(self, event):
        self.drag_x = event.x_root - self.root.winfo_x()
        self.drag_y = event.y_root - self.root.winfo_y()

    def do_drag(self, event):
        x = event.x_root - getattr(self, "drag_x", 0)
        y = event.y_root - getattr(self, "drag_y", 0)
        self.root.geometry(f"+{x}+{y}")

    @staticmethod
    def check_connection():
        try:
            socket.create_connection((PING_HOST, 53), timeout=1.5).close()
            return True
        except OSError:
            return False

    def update_stats(self):
        now = time.time()
        current = psutil.net_io_counters()
        elapsed = max(now - self.last_time, 0.001)
        down = max(0, current.bytes_recv - self.last.bytes_recv) / elapsed / (1024 * 1024)
        up = max(0, current.bytes_sent - self.last.bytes_sent) / elapsed / (1024 * 1024)

        self.download_var.set(f"↓ {down:.2f} MB/s")
        self.upload_var.set(f"↑ {up:.2f} MB/s")
        online = self.check_connection()
        self.status_var.set("● Connected" if online else "● Offline")
        self.status_var.set("● Connected" if online else "● Offline")
        # Keep status text color consistent with its state.
        self.last = current
        self.last_time = now
        self.root.after(REFRESH_MS, self.update_stats)

    def update_ping(self):
        try:
            result = subprocess.run(
                ["ping", "-n", "1", "-w", "1200", PING_HOST],
                capture_output=True, text=True, timeout=2.5,
                creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0)
            )
            import re
            match = re.search(r"time[=<]\s*(\d+)\s*ms", result.stdout, re.I)
            self.ping_var.set(f"Ping: {match.group(1)} ms" if match else "Ping: -- ms")
        except Exception:
            self.ping_var.set("Ping: -- ms")
        self.root.after(5000, self.update_ping)

if __name__ == "__main__":
    root = tk.Tk()
    app = NetworkMonitor(root)
    root.mainloop()
