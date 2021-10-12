import uuid
import os
import pandas as pd
import webbrowser
import matplotlib.pyplot as plt
import numpy as np

from create_report import createHTMLReportFile

THRESHOLD_FOR_ACCIDENT_SWITCH = 10  # seconds


def analyseTimeFrame(self):
    left_time = self.time_input_left.get()
    right_time = self.time_input_right.get()
    drive = (left_time, right_time)
    filename = str(uuid.uuid4())
    foldername = filename
    filename = filename + ".html"
    if not os.path.exists(foldername):
        os.mkdir(foldername)
    result = [analyseDrive(self, drive, foldername, 1)]
    createHTMLReportFile(self, result, filename, foldername)
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
        time_frames = detect_drives(self)
        results = []
        index = 1
        for drive in time_frames:
            results.append(analyseDrive(self, drive, foldername, index))
            index += 1
        createHTMLReportFile(self, results, filename, foldername)
    webbrowser.open_new_tab("file://" + os.path.realpath(filename))


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
        "Zeitstempel <= '" + str(time[1]) + "' & Zeitstempel >= '" + str(time[0]) + "'"
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
