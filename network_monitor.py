import tkinter as tk
from tkinter import ttk, colorchooser, messagebox
from pathlib import Path
import json, time, socket, subprocess, re
import psutil

APP = "Network Monitor"
CONFIG = Path.home() / "NetworkMonitor_settings.json"
HOST = "1.1.1.1"

DEFAULTS = {
    "theme": "Dark", "bg_color": "#151a22", "text_color": "#edf2f8",
    "down_color": "#65d68a", "up_color": "#69b7ff",
    "opacity": 100, "font_size": 10, "widget_scale": 100,
    "refresh": 1000, "position": "Bottom Right",
    "show_download": True, "show_upload": True,
    "show_ping": True, "show_status": True,
}

class Monitor:
    def __init__(self, root):
        self.root = root
        self.cfg = DEFAULTS.copy()
        self.load_config()
        self.root.title(APP)
        self.root.overrideredirect(True)
        self.root.attributes("-topmost", True)
        self.root.resizable(False, False)
        self.last = psutil.net_io_counters()
        self.last_time = time.monotonic()
        self.vars = {k: tk.StringVar(value=v) for k, v in {
            "download": "↓ 0.00 MB/s", "upload": "↑ 0.00 MB/s",
            "ping": "Ping: -- ms", "status": "● Checking"
        }.items()}
        self.settings_window = None
        self.build_widget()
        self.apply_config()
        self.refresh_stats()
        self.refresh_ping()

    def load_config(self):
        try:
            data = json.loads(CONFIG.read_text(encoding="utf-8"))
            self.cfg.update({k: v for k, v in data.items() if k in DEFAULTS})
        except Exception:
            pass

    def save_config(self):
        try:
            CONFIG.write_text(json.dumps(self.cfg, indent=2), encoding="utf-8")
        except OSError as e:
            messagebox.showerror(APP, f"Could not save settings:\n{e}")

    def palette(self):
        if self.cfg["theme"] == "Light":
            return {"bg": self.cfg["bg_color"], "fg": self.cfg["text_color"],
                    "muted": "#667085", "border": "#b8c2cf"}
        return {"bg": self.cfg["bg_color"], "fg": self.cfg["text_color"],
                "muted": "#aab6c7", "border": "#394354"}

    def build_widget(self):
        p = self.palette()
        scale = max(70, min(160, int(self.cfg["widget_scale"]))) / 100
        fs = max(7, round(int(self.cfg["font_size"]) * scale))
        pad_x, pad_y = round(10 * scale), round(7 * scale)
        self.frame = tk.Frame(self.root, bg=p["bg"], padx=pad_x, pady=pad_y,
                              highlightthickness=1, highlightbackground=p["border"])
        self.frame.pack()
        self.items = {}
        def add(key, color, bold=False):
            w = tk.Label(self.frame, textvariable=self.vars[key], bg=p["bg"], fg=color,
                         font=("Segoe UI", fs, "bold" if bold else "normal"))
            w.pack(side="left", padx=max(3, round(7*scale)))
            self.items[key] = w
        self.brand = tk.Label(self.frame, text="NET", bg=p["bg"], fg=p["muted"],
                              font=("Segoe UI", max(8, fs-2), "bold"))
        self.brand.pack(side="left", padx=(0, max(3, round(5*scale))))
        add("download", self.cfg["down_color"], True)
        add("upload", self.cfg["up_color"], True)
        add("ping", p["fg"])
        add("status", "#65d68a", True)
        self.gear = tk.Label(self.frame, text="⚙", bg=p["bg"], fg=p["muted"],
                             font=("Segoe UI Symbol", fs+1), cursor="hand2")
        self.gear.pack(side="left", padx=(6, 4))
        self.gear.bind("<Button-1>", lambda e: self.open_settings())
        self.close = tk.Label(self.frame, text="×", bg=p["bg"], fg=p["muted"],
                              font=("Segoe UI", fs+2, "bold"), cursor="hand2")
        self.close.pack(side="left", padx=(4, 0))
        self.close.bind("<Button-1>", lambda e: self.root.destroy())
        for w in [self.frame, self.brand, *self.items.values()]:
            w.bind("<Button-1>", self.drag_start, add="+")
            w.bind("<B1-Motion>", self.drag_move, add="+")

    def apply_config(self):
        p = self.palette()
        self.root.attributes("-alpha", max(.45, min(1.0, int(self.cfg["opacity"])/100)))
        for key in ("download", "upload", "ping", "status"):
            w = self.items[key]
            w.pack_forget()
            if self.cfg["show_" + key]:
                w.pack(side="left", padx=7)
        self.root.update_idletasks()
        self.place_window()

    def place_window(self):
        self.root.update_idletasks()
        w, h = self.root.winfo_reqwidth(), self.root.winfo_reqheight()
        sw, sh = self.root.winfo_screenwidth(), self.root.winfo_screenheight()
        pos = self.cfg["position"]
        x = 16 if pos.endswith("Left") else sw-w-16
        y = 16 if pos.startswith("Top") else sh-h-58
        self.root.geometry(f"{w}x{h}+{x}+{y}")

    def drag_start(self, e):
        self.drag_x = e.x_root - self.root.winfo_x()
        self.drag_y = e.y_root - self.root.winfo_y()

    def drag_move(self, e):
        self.root.geometry(f"+{e.x_root-self.drag_x}+{e.y_root-self.drag_y}")

    def open_settings(self):
        if self.settings_window and self.settings_window.winfo_exists():
            self.settings_window.lift()
            return
        win = tk.Toplevel(self.root)
        self.settings_window = win
        win.title("Network Monitor Settings")
        win.attributes("-topmost", True)
        win.resizable(False, False)
        win.configure(bg="#202733")
        win.geometry("390x650")
        tk.Label(win, text="Network Monitor Settings", bg="#202733", fg="white",
                 font=("Segoe UI", 14, "bold")).pack(anchor="w", padx=16, pady=(14, 8))
        body = tk.Frame(win, bg="#202733")
        body.pack(fill="both", expand=True, padx=16)

        theme = tk.StringVar(value=self.cfg["theme"])
        position = tk.StringVar(value=self.cfg["position"])
        refresh = tk.StringVar(value=str(self.cfg["refresh"]))
        opacity = tk.IntVar(value=self.cfg["opacity"])
        font_size = tk.IntVar(value=self.cfg["font_size"])
        widget_scale = tk.IntVar(value=self.cfg["widget_scale"])
        bg_color = tk.StringVar(value=self.cfg["bg_color"])
        text_color = tk.StringVar(value=self.cfg["text_color"])
        down_color = tk.StringVar(value=self.cfg["down_color"])
        up_color = tk.StringVar(value=self.cfg["up_color"])
        flags = {k: tk.BooleanVar(value=self.cfg["show_"+k])
                 for k in ("download", "upload", "ping", "status")}

        def label(text):
            tk.Label(body, text=text, bg="#202733", fg="#dce4ee",
                     font=("Segoe UI", 9, "bold")).pack(anchor="w", pady=(8, 2))
        def combo(title, var, values):
            label(title)
            ttk.Combobox(body, textvariable=var, values=values,
                         state="readonly", width=34).pack(anchor="w")
        def slider(title, var, lo, hi):
            label(title)
            tk.Scale(body, from_=lo, to=hi, orient="horizontal", variable=var,
                     bg="#202733", fg="white", troughcolor="#465366",
                     highlightthickness=0, length=330).pack(anchor="w")
        combo("Theme", theme, ["Dark", "Light"])
        combo("Screen position", position,
              ["Bottom Right", "Bottom Left", "Top Right", "Top Left"])
        slider("Widget size (%)", widget_scale, 70, 160)
        slider("Font size", font_size, 8, 18)
        slider("Transparency (%)", opacity, 45, 100)
        combo("Refresh interval", refresh, ["500", "1000", "2000", "3000"])
        label("Show / Hide")
        for key, title in [("download","Download speed"),("upload","Upload speed"),
                           ("ping","Ping"),("status","Connection status")]:
            tk.Checkbutton(body, text=title, variable=flags[key], bg="#202733",
                           fg="white", selectcolor="#202733",
                           activebackground="#202733").pack(anchor="w")

        def color_button(title, var):
            row = tk.Frame(body, bg="#202733")
            row.pack(fill="x", pady=3)
            tk.Label(row, text=title, bg="#202733", fg="#dce4ee").pack(side="left")
            swatch = tk.Label(row, text=var.get(), bg=var.get(), fg="white", padx=8)
            swatch.pack(side="right")
            def choose():
                picked = colorchooser.askcolor(color=var.get(), parent=win)
                if picked and picked[1]:
                    var.set(picked[1]); swatch.config(text=picked[1], bg=picked[1])
            tk.Button(row, text="Choose", command=choose, relief="flat").pack(side="right", padx=8)
        label("Colors")
        color_button("Background", bg_color)
        color_button("Text", text_color)
        color_button("Download", down_color)
        color_button("Upload", up_color)

        def save():
            self.cfg.update({
                "theme": theme.get(), "position": position.get(),
                "refresh": int(refresh.get()), "opacity": opacity.get(),
                "font_size": font_size.get(), "widget_scale": widget_scale.get(),
                "bg_color": bg_color.get(), "text_color": text_color.get(),
                "down_color": down_color.get(), "up_color": up_color.get(),
                **{"show_"+k: v.get() for k, v in flags.items()}
            })
            self.save_config()
            win.destroy()
            self.root.destroy()
            new_root = tk.Tk()
            Monitor(new_root)
            new_root.mainloop()

        buttons = tk.Frame(win, bg="#202733")
        buttons.pack(fill="x", padx=16, pady=12)
        tk.Button(buttons, text="Save settings", command=save, bg="#2878d0",
                  fg="white", relief="flat", padx=16, pady=8).pack(side="left")
        tk.Button(buttons, text="Reset defaults", command=lambda: self.reset_settings(win),
                  bg="#465366", fg="white", relief="flat", padx=12, pady=8).pack(side="left", padx=8)

    def reset_settings(self, win):
        self.cfg = DEFAULTS.copy()
        self.save_config()
        win.destroy()
        self.root.destroy()
        new_root = tk.Tk()
        Monitor(new_root)
        new_root.mainloop()

    def refresh_stats(self):
        now = time.monotonic()
        current = psutil.net_io_counters()
        elapsed = max(now - self.last_time, 0.001)
        down = max(0, current.bytes_recv - self.last.bytes_recv) / elapsed / (1024*1024)
        up = max(0, current.bytes_sent - self.last.bytes_sent) / elapsed / (1024*1024)
        self.vars["download"].set(f"↓ {down:.2f} MB/s")
        self.vars["upload"].set(f"↑ {up:.2f} MB/s")
        self.vars["status"].set("● Connected" if self.check_connection() else "● Offline")
        self.last, self.last_time = current, now
        self.root.after(int(self.cfg["refresh"]), self.refresh_stats)

    @staticmethod
    def check_connection():
        try:
            socket.create_connection((HOST, 53), timeout=1).close()
            return True
        except OSError:
            return False

    def refresh_ping(self):
        try:
            result = subprocess.run(["ping", "-n", "1", "-w", "1200", HOST],
                capture_output=True, text=True, timeout=2.5,
                creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0))
            match = re.search(r"time[=<]\s*(\d+)\s*ms", result.stdout, re.I)
            self.vars["ping"].set(f"Ping: {match.group(1)} ms" if match else "Ping: -- ms")
        except Exception:
            self.vars["ping"].set("Ping: -- ms")
        self.root.after(5000, self.refresh_ping)

if __name__ == "__main__":
    app_root = tk.Tk()
    Monitor(app_root)
    app_root.mainloop()
