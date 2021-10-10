import tkinter as tk
from tkinter.constants import LEFT
from tkinter.filedialog import askopenfilename
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import uuid
import os
import webbrowser
from math import floor

THRESHOLD_FOR_ACCIDENT_SWITCH = 10  # seconds


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
        file_button = tk.Button(under_frame1)
        file_button["text"] = "Choose a file"
        file_button["command"] = self.ask_for_file
        file_button.pack(padx=20, pady=20, side=LEFT)

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
        self.filename = askopenfilename()
        self.init_csv()

    def init_csv(self):
        self.file["text"] = str(self.filename)
        self.df = pd.read_csv(str(self.filename), delimiter=";", encoding="cp1252")
        self.df["Motorstatus"] = (
            self.df["Motorstatus"]
            .str.encode("ascii", "ignore")
            .str.decode(encoding="ascii")
        )
        for i in range(len(self.df)):
            time = self.df.loc[i]["Zeitstempel"]
            if not pd.isna(time):
                self.time_label["text"] = (
                    "(Zwischen: "
                    + time
                    + " und "
                    + self.df.loc[len(self.df) - 1]["Zeitstempel"]
                    + ")"
                )
                break
        # Convert the row Zeitstempel into a date
        self.df["Zeitstempel"] = self.df["Zeitstempel"].str.replace(
            "[\(\)]", "", regex=True
        )
        self.df["Zeitstempel"] = pd.to_datetime(
            self.df["Zeitstempel"], format="%d.%m.%Y %H:%M:%S"
        )
        # Set the active camera in the dataframe
        cameras = []
        view = 0
        for i in range(len(self.df)):
            row = self.df.iloc[i]
            if row["Eintragstext"] == "Fahrsicht 1":
                view = 1
            elif row["Eintragstext"] == "Fahrsicht 2":
                view = 2
            elif row["Eintragstext"] == "Fahrsicht 3":
                view = 3
            cameras.append(view)
        cameras = pd.Series(cameras)
        self.df["Camera"] = cameras
        self.df.to_csv("ouput.csv")

    def analyseTimeFrame(self):
        left_time = self.time_input_left.get()
        right_time = self.time_input_right.get()
        drive = (left_time, right_time)
        filename = str(uuid.uuid4())
        foldername = filename
        filename = filename + ".html"
        if not os.path.exists(foldername):
            os.mkdir(foldername)
        result = [self.analyseDrive(drive, foldername)]
        self.createHTMLReportFile(result, filename, foldername)
        webbrowser.open_new_tab("file://" + os.path.realpath(filename))

    def analyseArea(self):
        # Filter the table by the input time
        filtered_df = self.df.query("Zeitstempel <= '" + self.time_input.get() + "'")

        # Figure out the gear
        filtered_ganglage = filtered_df.dropna(axis=0, subset=["Ganglage (Ist)"])
        gang = filtered_ganglage.iloc[len(filtered_ganglage) - 1]["Ganglage (Ist)"]
        self.label_gang["text"] = "Gang: " + gang

        # Figure out the view
        view = filtered_df.iloc[len(filtered_df) - 1]["Camera"]
        self.label_view["text"] = "Kamera: " + str(view)

        # Ermitteln der Geschwindigkeit
        index = len(filtered_df) - 1
        speed = filtered_df.iloc[index]["Geschwindigkeit [km/h]"]
        while pd.isna(speed):
            index -= 1
            speed = filtered_df.iloc[index]["Geschwindigkeit [km/h]"]
        self.label_speed["text"] = "Geschwindigkeit: " + str(speed)

    def createAutomaticReport(self):
        if not self.df is None:
            filename = str(uuid.uuid4())
            foldername = filename
            filename = os.path.join(foldername, "Berichte" + ".html")
            if not os.path.exists(foldername):
                os.mkdir(foldername)
            time_frames = self.detect_drives()
            results = []
            index = 1
            for drive in time_frames:
                results.append(self.analyseDrive(drive, foldername, index))
                index += 1
            self.createHTMLReportFile(results, filename, foldername)
        webbrowser.open_new_tab("file://" + os.path.realpath(filename))

    def createHTMLReportFile(self, reports, filename, foldername):

        # Create a nice header
        self.writeHTMLHeader(filename)

        counter = 0
        with open(filename, "a") as file:
            # Create the reports
            for result in reports:
                counter += 1
                # Header
                file.write("<div class='report'><h2>Bericht " + str(counter) + "</h2>")
                file.write(
                    "<h3>Fahrt von "
                    + str(result["Time"][0])
                    + " bis "
                    + str(result["Time"][1])
                    + "</h3"
                )
                file.write("<br><br>")

                # Write the data
                file.write(
                    "<p>Durchschnittsgeschwindigkeit: "
                    + str(result["Average Speed"])
                    + " </p>"
                )

                unusual_things_backwards = result["Unusual Things Backwards"]
                unusual_things_forwards = result["Unusual Things Forwards"]
                if len(unusual_things_backwards) + len(unusual_things_forwards) != 0:
                    file.write(
                        "<table><tr><th>Zeitstempel</th><th>Ganglage (Ist)</th><th>Geschwindigkeit [km/h]</th><th>Kamera</th></tr>"
                    )
                    for i in range(len(unusual_things_backwards)):
                        row = unusual_things_backwards.iloc[i]
                        file.write(
                            "<tr><td>"
                            + str(row["Zeitstempel"])
                            + "</td><td>"
                            + row["Ganglage (Ist)"]
                            + "</td><td>"
                            + str(row["Geschwindigkeit [km/h]"])
                            + "</td><td>"
                            + str(row["Camera"])
                            + "</td></tr>"
                        )
                    for i in range(len(unusual_things_forwards)):
                        row = unusual_things_forwards.iloc[i]
                        file.write(
                            "<tr><td>"
                            + str(row["Zeitstempel"])
                            + "</td><td>"
                            + row["Ganglage (Ist)"]
                            + "</td><td>"
                            + str(row["Geschwindigkeit [km/h]"])
                            + "</td><td>"
                            + str(row["Camera"])
                            + "</td></tr>"
                        )
                    file.write("</table>")

                # The time in the cameras
                times = result["Time In Camera"]
                total_time = times[0] + times[1] + times[2]
                file.write("<p>Verbrachte Zeit in Kameras:</p>")
                file.write(
                    "<table><tr><th>Gesamt</th><th>Kamera 1</th><th>Kamera 2</th><th>Kamera 3</th><tr>"
                )
                file.write(
                    "<tr><td>"
                    + to_time_format(total_time)
                    + "</td><td>"
                    + to_time_format(times[0])
                    + "</td><td>"
                    + to_time_format(times[1])
                    + "</td><td>"
                    + to_time_format(times[2])
                    + "</td></tr></table>"
                )

                file.write("<h3>Kamerawechsel: </h3>")
                switches = result["Camera Switches"]
                total_switches = np.array(switches).sum()
                file.write(
                    "<table><tr><th>Gesamt</th><th>Von 1 zu 2</th><th>Von 1 zu 3</th><th>Von 2 zu 1</th><th>Von 2 zu 3</th><th>Von 3 zu 1</th><th>Von 3 zu 2</th></tr>"
                )
                file.write(
                    "<tr><td>"
                    + str(total_switches)
                    + "</td><td>"
                    + str(switches[0][1])
                    + "</td><td>"
                    + str(switches[0][2])
                    + "</td><td>"
                    + str(switches[1][0])
                    + "</td><td>"
                    + str(switches[1][2])
                    + "</td><td>"
                    + str(switches[2][0])
                    + "</td><td>"
                    + str(switches[2][1])
                    + "</td></tr></table>"
                )

                accidential_switches = result["Accidential Switches"]
                if len(accidential_switches) != 0:
                    file.write(
                        "<h3>Versehentliche Kamerawechsel:</h3><table><tr><th>Von Kamera</th><th>Zu Kamera</th><th>Wechsel bei</th><th>War aktiv für [s]</th><tr>"
                    )
                    for ele in accidential_switches:
                        file.write(
                            "<tr><td>"
                            + str(ele["From"])
                            + "</td><td>"
                            + str(ele["To"])
                            + "</td><td>"
                            + str(ele["At"])
                            + "</td><td>"
                            + str(ele["Duration"])
                            + "</td></tr>"
                        )
                file.write("</table>")

                file.write(
                    "<img src='"
                    + result["View Speed Graph"]
                    + "' style='width:100%;''/>"
                )

                # Output all the error messages
                if len(result["Errors Freq"]) > 0:
                    file.write(
                        "<h3>Fehlermeldungen nach Häufigkeit:</h3><table><tr><th>Name</th><th>Häufigkeit</th></tr>"
                    )
                    for error in result["Errors Freq"]:
                        file.write(
                            "<tr><td>"
                            + error[0]
                            + "</td><td>"
                            + str(error[1])
                            + "</td></tr>"
                        )
                    file.write("</table>")
                    file.write(
                        "<a href='file://"
                        + os.path.realpath(result["Errors File"])
                        + "'><button>Fehlerdatei</button></a>"
                    )
                file.write(
                    "<a href='file://"
                    + os.path.realpath(result["Drive Log"])
                    + "'><button>Logbuch der Fahrt</button></a>"
                )

                file.write("</div>")

        # Write the closing for the file
        with open(filename, "a") as file:
            file.write("</body></html>")

    def writeHTMLHeader(self, filename):
        with open("header.html", "r") as file:
            text = file.read()

        with open(filename, mode="w") as file:
            file.write(text)

    def analyseDrive(self, time, foldername, index):
        """
        Analyses a drive that is within the time frame given by the time tuple.
        """

        # set the folder path
        subfolder = "Bericht " + str(index)
        folder = os.path.join(foldername, subfolder)
        if not os.path.exists(folder):
            os.mkdir(folder)

        # Filter the data to match the timestamps of the drive
        filtered_df = self.df.query(
            "Zeitstempel <= '"
            + str(time[1])
            + "' & Zeitstempel >= '"
            + str(time[0])
            + "'"
        )

        # get the average speed
        time_since = (
            filtered_df.iloc[len(filtered_df) - 1]["Zeitstempel"]
            - filtered_df.iloc[0]["Zeitstempel"]
        )
        hours = time_since.seconds / 3600
        filtered_df_distance = filtered_df.dropna(subset=["Gesamtkilometer [km]"])
        driven_kilometers = (
            -filtered_df_distance.iloc[0]["Gesamtkilometer [km]"]
            + filtered_df_distance.iloc[len(filtered_df_distance) - 1][
                "Gesamtkilometer [km]"
            ]
        )
        average_speed = driven_kilometers / hours

        # Analyse the View
        filtered_df_view = filtered_df[
            filtered_df["Eintragstext"].str.contains("Fahrsicht")
        ]
        # Find the times where the view was not equal to the gear and the car was moving
        unusual_things_backwards = filtered_df_view[
            (filtered_df_view["Eintragstext"] == "Fahrsicht 3")
            & (filtered_df_view["Ganglage (Ist)"].str.contains("V"))
            & (filtered_df_view["Geschwindigkeit [km/h]"] != 0)
        ]
        unusual_things_forwards = filtered_df[
            (
                (filtered_df["Eintragstext"] == "Fahrsicht 1")
                | (filtered_df["Eintragstext"] == "Fahrsicht 2")
            )
            & (filtered_df["Ganglage (Ist)"].str.contains("R"))
            & (filtered_df["Geschwindigkeit [km/h]"] != 0)
        ]

        # Draw a figure with the view as the background and the speed as a curve
        fig, ax = plt.subplots(figsize=(30, 10))
        plt.plot(
            filtered_df["Zeitstempel"],
            filtered_df["Geschwindigkeit [km/h]"],
            color="black",
        )
        x = np.array(filtered_df["Zeitstempel"])
        y_min = np.repeat(ax.get_ylim()[0], len(filtered_df))
        y_max = np.repeat(ax.get_ylim()[1], len(filtered_df))
        y = np.array([y_min, y_max])
        x = np.array([x, x])
        x.shape, y.shape
        ax.pcolormesh(
            x,
            y,
            [filtered_df["Camera"][0 : len(filtered_df) - 1]],
            cmap=plt.cm.get_cmap("jet", 3),
            shading="auto",
            alpha=0.4,
        )
        # Save the plot
        # plt.colorbar(
        #     plt.cm.ScalarMappable(cmap=plt.cm.get_cmap("jet", 3)),
        #     ticks=[0, 1, 2, 3],
        #     alpha=0.4,
        # )
        filename_view_speed_graph = "Geschwindigkeitsgrafik" + ".jpg"
        plt.savefig(
            os.path.join(folder, filename_view_speed_graph),
            format="jpg",
            dpi=100,
            bbox_inches="tight",
        )
        plt.close("all")

        # Figure out the time spend in each Camera
        cameras = [0, 0, 0]
        switches = [[0, 0, 0], [0, 0, 0], [0, 0, 0]]
        accidential_switches = []
        start = filtered_df.iloc[0]["Zeitstempel"]
        camera = filtered_df.iloc[0]["Camera"] - 1
        for i in range(len(filtered_df)):
            cam = filtered_df.iloc[i]["Camera"] - 1
            timestamp = filtered_df.iloc[i]["Zeitstempel"]
            if cam != camera:
                time_passed = (timestamp - start).seconds
                if time_passed < THRESHOLD_FOR_ACCIDENT_SWITCH:
                    accidential_switches.append(
                        {
                            "From": camera + 1,
                            "To": cam + 1,
                            "At": timestamp,
                            "Duration": time_passed,
                        }
                    )
                start = timestamp
                cameras[camera] += time_passed
                switches[camera][cam] += 1
                camera = cam
        time_passed = (
            filtered_df.iloc[len(filtered_df) - 1]["Zeitstempel"] - start
        ).seconds
        cameras[camera] += time_passed

        # Get all the error messages by frequency
        filtered_df_errors = filtered_df[
            (filtered_df["Eintragstext"].str.contains("Kamera"))
            | (filtered_df["Eintragstext"].str.contains("Video"))
        ]
        counts = filtered_df_errors.groupby(["Eintragstext"]).count()
        errors = {}
        for i in range(len(counts)):
            row = counts.iloc[i]
            errors[row.name] = row["Eintragstyp"]
        errors = sorted(errors.items(), key=lambda x: x[1], reverse=True)
        errors_file = os.path.join(folder, "Fehleruebersicht" + ".csv")
        if len(filtered_df_errors) > 0:
            filtered_df_errors.to_csv(errors_file, sep=";")

        # Create the .csv file from the drive
        drive_export_filename = os.path.join(
            folder, "Logbuch des Berichts " + str(index) + ".csv"
        )
        filtered_df.to_csv(drive_export_filename, sep=";")

        # Return all the results
        return {
            "Time": time,
            "Average Speed": average_speed,
            "Unusual Things Backwards": unusual_things_backwards,
            "Unusual Things Forwards": unusual_things_forwards,
            "Folder": folder,
            "View Speed Graph": os.path.join(subfolder, filename_view_speed_graph),
            "Time In Camera": cameras,
            "Camera Switches": switches,
            "Accidential Switches": accidential_switches,
            "Errors Freq": errors,
            "Errors File": os.path.join(folder, "Fehleruebersicht" + ".csv"),
            "Drive Log": os.path.join(
                folder, "Logbuch des Berichts " + str(index) + ".csv"
            ),
        }

    def detect_drives(self):

        # Neue Erkennung nach Motorzeiten

        # Identifizieren der verschiedenen Fahrten
        start_stop_times = self.df[self.df["Eintragstyp"] == "MSTA"]
        running = False
        drives = []
        start = None
        for i in range(len(start_stop_times)):
            row = start_stop_times.iloc[i]
            if not running and row["Motorstatus"] == "luft":
                start = row["Zeitstempel"]
                running = True
            elif running and row["Motorstatus"] == "steht":
                drives.append((start, row["Zeitstempel"]))
                running = False
        return drives

        """ Alte Version der Erkennung, die sich nicht nach dem Motor richtet: 
        # Identifizieren der verschiedenen Fahrten
        start_stop_times = self.df[
            (self.df["Eintragstyp"] == "SO") | (self.df["Eintragstyp"] == "SI")
        ]

        # Store all of the times in tuples in drives
        drives = []
        time = (None, None)
        for i in range(len(start_stop_times)):
            row = start_stop_times.iloc[i]
            if row["Eintragstyp"] == "SO":
                if time[0] is not None:
                    time = (time[0], row["Zeitstempel"])
                    drives.append(time)
                    time = (None, None)
            elif row["Eintragstyp"] == "SI":
                time = (row["Zeitstempel"], None)
        return drives
        """


def to_time_format(seconds):
    return (
        "{:02d}".format(seconds // 3600)
        + ":"
        + "{:02d}".format(seconds % 3600 // 60)
        + ":"
        + "{:02d}".format(seconds % 60)
    )


def main():
    root = tk.Tk()
    root.geometry("1920x1080")
    app = Application(master=root)
    app.mainloop()


if __name__ == "__main__":
    main()
