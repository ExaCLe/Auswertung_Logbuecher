import tkinter as tk
from tkinter.constants import LEFT
from analyse_log_files import analyseArea
import pandas as pd

from init_csv_file import ask_for_file
from analyse_log_files import (
    analyseArea,
    analyseDrive,
    analyseTimeFrame,
    createAutomaticReport,
)


class Application(tk.Frame):
    def __init__(self, master=None):
        super().__init__(master)
        self.master = master
        self.pack(expand=False, fill=tk.X)
        self.create_widgets()
        self.filename = None
        self.df = None

    def create_widgets(self):
        frame1 = tk.Frame(self)
        frame1.pack(fill=tk.X, side="top")

        # File Choosing
        tk.Label(
            frame1, text="1. Wähle eine Datei zur Analyse:", font=("Arial", 20)
        ).pack(padx=20, pady=20, side=LEFT, fill=tk.X)
        under_frame1 = tk.Frame(frame1)
        under_frame1.pack(side="left")
        self.createButton(under_frame1, "Choose a file", self.ask_for_file)

        # Filename
        self.file = tk.Label(under_frame1, text="")
        self.file.pack(padx=20, pady=20, side=LEFT)

        # Instruction Zeitpunkt
        frame2 = tk.Frame(self)
        frame2.pack(fill=tk.X, side="top")
        tk.Label(
            frame2,
            text="2. Wähle einen Zeitpunkt zur Analyse aus: ",
            font=("Arial", 20),
        ).pack(side="left", padx=20)

        # Input for Zeitpunkt-Analyse
        self.time_input = tk.Entry(frame2)
        self.time_input.pack(padx=20, side="left")

        # Button-Zeitpunktanalyse
        self.createButton(frame2, "Zeitpunkt analysieren", self.analyseArea)

        # Labels for the possible range of time inputs
        self.time_label = tk.Label(frame2)
        self.time_label.pack(padx=20, side="left")

        # The results of the Zeitpunkt-Analyse
        frame3 = tk.Frame(self)
        frame3.pack(side="top", fill=tk.X, padx=100, expand=True)
        label_ergebnisse = tk.Label(frame3, text="Ergebnisse: ", font=("Arial", 18))
        label_ergebnisse.pack(side="left")
        self.label_gang = tk.Label(frame3, text="Gang: ", font=("Arial", 15))
        self.label_gang.pack(padx=20, pady=20, side=LEFT)
        self.label_speed = tk.Label(frame3, text="Geschwindigkeit", font=("Arial", 15))
        self.label_speed.pack(padx=20, pady=20, side=LEFT)
        self.label_view = tk.Label(frame3, text="Kamera: ", font=("Arial", 15))
        self.label_view.pack(padx=20, pady=20, side=LEFT)

        # Abschnittsanalyse
        frame4 = tk.Frame(self)
        frame4.pack(side="top", fill=tk.X, padx=20)
        label_instruction3 = tk.Label(
            frame4,
            text="3. Automatische Erkennung von Fahrten mit zugehöriger Analyse:",
            font=("Arial", 20),
        )
        label_instruction3.pack(side="left")
        self.createButton(frame4, "Automatische Analyse", self.createAutomaticReport)

        # Wahl eines eigenen Abschnittes
        frame5 = tk.Frame(self)
        frame5.pack(side="top", fill=tk.X, padx=20)
        label_instruction4 = tk.Label(
            frame5,
            text="4. Abschnittsanalyse (Von ... bis ...) Format: DD.MM.YYYY HH:MM:SS: ",
            font=("Arial", 20),
        )
        label_instruction4.pack(side="left")
        self.time_input_left = tk.Entry(frame5)
        self.time_input_left.pack(padx=20, side="left")
        self.time_input_right = tk.Entry(frame5)
        self.time_input_right.pack(padx=20, side="left")
        self.createButton(frame5, "Abschnittsanalyse", self.analyseTimeFrame)

        # Button to end the program
        quit = tk.Button(self, text="QUIT", fg="red", command=self.master.destroy)
        quit.pack(padx=20, pady=20)

    def ask_for_file(self):
        ask_for_file(self)

    def analyseArea(self):
        time_input = self.time_input.get()
        gang, view, speed = analyseArea(self.df, time_input)
        self.label_gang["text"] = "Gang: " + gang
        self.label_view["text"] = "Kamera: " + str(view)
        self.label_speed["text"] = "Geschwindigkeit: " + str(speed)

    def analyseTimeFrame(self):
        left_time = pd.to_datetime(
            self.time_input_left.get(), format="%d.%m.%Y %H:%M:%S"
        )
        right_time = pd.to_datetime(
            self.time_input_right.get(), format="%d.%m.%Y %H:%M:%S"
        )
        analyseTimeFrame(self.df, left_time, right_time)

    def createAutomaticReport(self):
        createAutomaticReport(self.df)

    def createButton(self, frame, text, onClick):
        button = tk.Button(frame)
        button["text"] = text
        button["command"] = onClick
        button.pack(padx=20, pady=20, side=LEFT)
        return button


def main():
    root = tk.Tk()
    root.geometry("1920x1080")
    app = Application(master=root)
    app.mainloop()


if __name__ == "__main__":
    main()
