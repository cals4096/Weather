#Cameron Lee
import sys
import os
import requests
import tkinter as tk
from tkinter import *
from tkinter import font as tkfont
from PIL import Image
from PIL import ImageTk
from datetime import datetime, timedelta

def resource_path(relative):
    base = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base, relative)

BG_COLOR     = "#1a1a2e"
PANEL_COLOR  = "#16213e"
ACCENT_COLOR = "#0f3460"
HIGHLIGHT    = "#e94560"
TEXT_PRIMARY = "#eaeaea"
TEXT_MUTED   = "#a0a0b0"

class Window:
    def __init__(self, root):
        self.root = root
        self.root.geometry("1100x750")
        self.root.resizable(False, False)
        self.root.title("Weather Forecast")
        self.root.configure(bg=BG_COLOR)

        title_font    = tkfont.Font(family="Segoe UI", size=22, weight="bold")
        label_font    = tkfont.Font(family="Segoe UI", size=11, weight="bold")
        value_font    = tkfont.Font(family="Segoe UI", size=11)
        input_font    = tkfont.Font(family="Segoe UI", size=11)
        button_font   = tkfont.Font(family="Segoe UI", size=11, weight="bold")
        dropdown_font = tkfont.Font(family="Segoe UI", size=10)

        # ── Title bar ──────────────────────────────────────────────
        title_bar = tk.Frame(root, bg=ACCENT_COLOR, height=60)
        title_bar.pack(fill=X)
        title_bar.pack_propagate(False)
        tk.Label(title_bar, text="Weather Forecast", font=title_font,
                 bg=ACCENT_COLOR, fg=TEXT_PRIMARY).pack(side=LEFT, padx=20, pady=10)

        # ── Input row ─────────────────────────────────────────────
        input_frame = tk.Frame(root, bg=BG_COLOR, pady=14)
        input_frame.pack(fill=X, padx=20)

        tk.Label(input_frame, text="City:", font=label_font,
                 bg=BG_COLOR, fg=TEXT_MUTED).pack(side=LEFT, padx=(0, 6))

        self.entry1 = tk.Entry(input_frame, font=input_font, width=22,
                               bg=PANEL_COLOR, fg=TEXT_PRIMARY,
                               insertbackground=TEXT_PRIMARY,
                               relief=FLAT, bd=6)
        self.entry1.pack(side=LEFT, padx=(0, 10))
        self.entry1.bind("<Return>", lambda e: self.pullData())

        tk.Label(input_frame, text="Date:", font=label_font,
                 bg=BG_COLOR, fg=TEXT_MUTED).pack(side=LEFT, padx=(10, 6))

        self.dateOptions = ["Today"]
        date = datetime.now()
        for i in range(5):
            self.dateOptions.append((date + timedelta(days=i+1)).strftime("%A"))

        self.clicked = StringVar(value="Today")
        self.drop = OptionMenu(input_frame, self.clicked, *self.dateOptions)
        self._style_dropdown(self.drop, dropdown_font)
        self.drop.pack(side=LEFT, padx=(0, 10))

        tk.Label(input_frame, text="Time:", font=label_font,
                 bg=BG_COLOR, fg=TEXT_MUTED).pack(side=LEFT, padx=(10, 6))

        timeOptions = ["Now", "00:00:00", "03:00:00", "06:00:00", "09:00:00",
                       "12:00:00", "15:00:00", "18:00:00", "21:00:00"]
        self.clickedTime = StringVar(value="Now")
        self.dropTime = OptionMenu(input_frame, self.clickedTime, *timeOptions)
        self._style_dropdown(self.dropTime, dropdown_font)
        self.dropTime.pack(side=LEFT, padx=(0, 14))

        tk.Button(input_frame, text="Get Weather", font=button_font,
                  bg=HIGHLIGHT, fg="white", activebackground="#c73652",
                  activeforeground="white", relief=FLAT, bd=0,
                  padx=16, pady=6, cursor="hand2",
                  command=self.pullData).pack(side=LEFT)

        # ── Divider ───────────────────────────────────────────────
        tk.Frame(root, bg=ACCENT_COLOR, height=2).pack(fill=X, padx=20, pady=(0, 12))

        # ── Main content area ─────────────────────────────────────
        content = tk.Frame(root, bg=BG_COLOR)
        content.pack(fill=BOTH, expand=True, padx=20, pady=(0, 20))

        # Icon panel (left)
        icon_frame = tk.Frame(content, bg=PANEL_COLOR, width=480, height=480,
                              bd=0, relief=FLAT)
        icon_frame.pack(side=LEFT, padx=(0, 20))
        icon_frame.pack_propagate(False)

        self.photo = tk.Label(icon_frame, bg=PANEL_COLOR, image="")
        self.photo.place(relx=0.5, rely=0.5, anchor=CENTER)

        # Stats panel (right)
        stats_frame = tk.Frame(content, bg=BG_COLOR)
        stats_frame.pack(side=LEFT, fill=BOTH, expand=True)

        self.tempInfo     = self._stat_card(stats_frame, "Temperature", label_font, value_font)
        self.climateInfo  = self._stat_card(stats_frame, "Forecast",    label_font, value_font)
        self.windInfo     = self._stat_card(stats_frame, "Wind Speed",  label_font, value_font)
        self.humidityInfo = self._stat_card(stats_frame, "Humidity",    label_font, value_font)

    def _style_dropdown(self, menu, fnt):
        menu.config(bg=PANEL_COLOR, fg=TEXT_PRIMARY, activebackground=ACCENT_COLOR,
                    activeforeground=TEXT_PRIMARY, relief=FLAT, bd=0,
                    highlightthickness=0, font=fnt)
        menu["menu"].config(bg=PANEL_COLOR, fg=TEXT_PRIMARY,
                            activebackground=ACCENT_COLOR, activeforeground=TEXT_PRIMARY)

    def _stat_card(self, parent, title, label_font, value_font):
        card = tk.Frame(parent, bg=PANEL_COLOR, bd=0, relief=FLAT)
        card.pack(fill=X, pady=8, ipady=12, ipadx=16)

        tk.Label(card, text=title.upper(), font=label_font,
                 bg=PANEL_COLOR, fg=TEXT_MUTED).pack(anchor=W, padx=16, pady=(10, 2))

        tk.Frame(card, bg=HIGHLIGHT, height=2).pack(fill=X, padx=16)

        value_label = tk.Label(card, text="—", font=value_font,
                               bg=PANEL_COLOR, fg=TEXT_PRIMARY)
        value_label.pack(anchor=W, padx=16, pady=(6, 10))
        return value_label

    # ── Data fetching ─────────────────────────────────────────────
    def pullData(self):
        city = self.entry1.get().strip()
        if not city:
            return
        try:
            if self.clicked.get() == "Today" and self.clickedTime.get() == "Now":
                APIKey = "8410d732e0a639f6dea271e2f6e12ad7"
                URL    = (f"http://api.openweathermap.org/data/2.5/weather?"
                          f"appid={APIKey}&q={city}&units=imperial")
                data   = requests.get(URL).json()

                self.setClimate(data["weather"][0]["description"])
                self.setIcon(data["weather"][0]["id"])
                self.setTemp(data["main"]["temp"])
                self.setWind(data["wind"]["speed"])
                self.setHumidity(data["main"]["humidity"])
            else:
                APIKey = "8410d732e0a639f6dea271e2f6e12ad7"
                URL    = (f"http://api.openweathermap.org/data/2.5/forecast?"
                          f"appid={APIKey}&q={city}&units=imperial")
                data   = requests.get(URL).json()

                for i, opt in enumerate(self.dateOptions):
                    if opt == self.clicked.get():
                        target_date = str((datetime.now() + timedelta(days=i)).date())
                        break

                target_dt = target_date + " " + self.clickedTime.get()
                matched = False
                for entry in data["list"]:
                    if entry["dt_txt"] == target_dt:
                        matched = True
                        self.setClimate(entry["weather"][0]["description"])
                        self.setIcon(entry["weather"][0]["id"])
                        self.setTemp(entry["main"]["temp"])
                        self.setWind(entry["wind"]["speed"])
                        self.setHumidity(entry["main"]["humidity"])
                        break

                if not matched:
                    self.setIcon(0)
        except Exception as e:
            print(f"Error: {e}")
            self._show_error("Invalid city name or network error.")

    def _show_error(self, msg):
        self.photo.config(image="", text=msg, fg=HIGHLIGHT,
                          font=tkfont.Font(family="Segoe UI", size=10))
        self.photo.image = None

    # ── Setters ───────────────────────────────────────────────────
    def setClimate(self, climate):
        self.climateInfo.config(text=climate.title())

    def setTemp(self, temp):
        self.tempInfo.config(text=f"{temp} °F")

    def setWind(self, wind):
        self.windInfo.config(text=f"{wind} mph")

    def setHumidity(self, humidity):
        self.humidityInfo.config(text=f"{humidity}%")

    def setIcon(self, id):
        icon_map = [
            (200, 232, "weatherIcons\\weatherThunder.jpg"),
            (300, 321, "weatherIcons\\weatherRain.jpg"),
            (500, 531, "weatherIcons\\weatherRain.jpg"),
            (600, 622, "weatherIcons\\weatherSnow.jpg"),
            (701, 781, "weatherIcons\\weatherCloudy.jpg"),
            (800, 800, "weatherIcons\\weatherSunny.jpg"),
            (801, 802, "weatherIcons\\weatherPartlyCloudy.jpg"),
            (803, 804, "weatherIcons\\weatherCloudy.jpg"),
        ]
        path = next((p for lo, hi, p in icon_map if lo <= id <= hi), None)

        if path:
            img = Image.open(path).resize((460, 460))
            img = ImageTk.PhotoImage(img)
            self.photo.config(image=img, text="")
            self.photo.image = img
        else:
            self.photo.config(image="", text="No icon available",
                              fg=TEXT_MUTED,
                              font=tkfont.Font(family="Segoe UI", size=10))
            self.photo.image = None

root = tk.Tk()
app = Window(root)
root.mainloop()
