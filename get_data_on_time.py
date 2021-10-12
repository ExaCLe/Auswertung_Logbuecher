import tkinter as tk
from tkinter.constants import LEFT
from analyse_log_files import analyseArea

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
        label_instruction1 = tk.Label(
            frame1, text="1. Wähle eine Datei zur Analyse:", font=("Arial", 20)
        )
        label_instruction1.pack(padx=20, pady=20, side=LEFT, fill=tk.X)
        under_frame1 = tk.Frame(frame1)
        under_frame1.pack(side="left")

        # Let the user choose a file
        self.createButton(under_frame1, "Choose a file", self.ask_for_file)

        # Show the Filename to the user and show possible time frames
        self.file = tk.Label(under_frame1, text="")
        self.file.pack(padx=20, pady=20, side=LEFT)

        frame2 = tk.Frame(self)
        frame2.pack(fill=tk.X, side="top")
        label_instruction2 = tk.Label(
            frame2,
            text="2. Wähle einen Zeitpunkt zur Analyse aus: ",
            font=("Arial", 20),
        )
        label_instruction2.pack(side="left", padx=20)

        # Request the input of the user
        self.time_input = tk.Entry(frame2)
        self.time_input.pack(padx=20, side="left")

        # Button to start the analysis
        btn_analyse = tk.Button(frame2)
        btn_analyse["text"] = "Zeitpunkt Analysieren"
        btn_analyse["command"] = self.analyseArea
        btn_analyse.pack(padx=20, side="left")

        # Show the range of input times
        self.time_label = tk.Label(frame2)
        self.time_label.pack(padx=20, side="left")

        frame3 = tk.Frame(self)
        frame3.pack(side="top", fill=tk.X, padx=100, expand=True)
        # Set the label that will show the results
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
        self.btn_analyse_automatic = tk.Button(frame4)
        self.btn_analyse_automatic["text"] = "Automatische Analyse"
        self.btn_analyse_automatic["command"] = self.createAutomaticReport
        self.btn_analyse_automatic.pack(padx=20, side="left")

        # Wahl eines eigenen Abschnittes
        frame5 = tk.Frame(self)
        frame5.pack(side="top", fill=tk.X, padx=20)
        label_instruction4 = tk.Label(
            frame5,
            text="4. Abschnittsanalyse (Von ... bis ...): ",
            font=("Arial", 20),
        )
        label_instruction4.pack(side="left")
        self.time_input_left = tk.Entry(frame5)
        self.time_input_left.pack(padx=20, side="left")
        self.time_input_right = tk.Entry(frame5)
        self.time_input_right.pack(padx=20, side="left")
        self.btn_analyse_time_frame = tk.Button(frame5)
        self.btn_analyse_time_frame["text"] = "Abschnittsanalyse"
        self.btn_analyse_time_frame["command"] = self.analyseTimeFrame
        self.btn_analyse_time_frame.pack(padx=20, side="left")

        # Button to end the program
        quit = tk.Button(self, text="QUIT", fg="red", command=self.master.destroy)
        quit.pack(padx=20, pady=20)

    def ask_for_file(self):
        ask_for_file(self)

    def analyseArea(self):
        analyseArea(self)

    def analyseDrive(self):
        analyseDrive(self)

    def analyseTimeFrame(self):
        analyseTimeFrame(self)

    def createAutomaticReport(self):
        createAutomaticReport(self)

    def createButton(self, frame, text, onClick):
        file_button = tk.Button(frame)
        file_button["text"] = text
        file_button["command"] = onClick
        file_button.pack(padx=20, pady=20, side=LEFT)


def main():
    root = tk.Tk()
    root.geometry("1920x1080")
    app = Application(master=root)
    app.mainloop()


if __name__ == "__main__":
    main()
