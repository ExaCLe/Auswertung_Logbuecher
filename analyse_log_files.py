import uuid
import os
import pandas as pd
import webbrowser
import matplotlib.pyplot as plt
import numpy as np

from create_report import createHTMLReportFile

THRESHOLD_FOR_ACCIDENT_SWITCH = 10  # seconds


def analyseTimeFrame(df, left_time, right_time):
    """
    Analyses the DataFrame for the time in between the two bounds. The time has to be in the format
    YYYY-MM-DD HH:MM(:SS) // the seconds are optional
    """
    drive = (left_time, right_time)

    # Filenames and folders for the report
    filename, foldername = createFilesAndFolders()

    # Analyse
    result = [analyseDrive(df, drive, foldername, 1)]
    # Create Report
    createHTMLReportFile(result, filename)
    # Open Report
    webbrowser.open_new_tab("file://" + os.path.realpath(filename))


def analyseArea(df, time_input):
    """
    Analyses the speed, the gear and the view of the DataFrame at the given time_input.

    Returns: gear, view, speed
    """
    # Filter the table by the input time
    filtered_df = df.query("Zeitstempel <= '" + time_input + "'")

    # Figure out the gear
    filtered_ganglage = filtered_df.dropna(axis=0, subset=["Ganglage (Ist)"])
    gang = filtered_ganglage.iloc[len(filtered_ganglage) - 1]["Ganglage (Ist)"]

    # Figure out the view
    view = filtered_df.iloc[len(filtered_df) - 1]["Camera"]

    # Ermitteln der Geschwindigkeit
    index = len(filtered_df) - 1
    speed = filtered_df.iloc[index]["Geschwindigkeit [km/h]"]
    while pd.isna(speed):
        index -= 1
        speed = filtered_df.iloc[index]["Geschwindigkeit [km/h]"]

    return gang, view, speed


def createAutomaticReport(df):
    """
    Creates an automatic report by first detecting the different drives, analysing those and then creating and opening the report.
    Exports the reports to an html file.
    """
    if not df is None:
        # Filenames and Folders for the report
        filename, foldername = createFilesAndFolders("Berichte")

        # Iterate over the drives and analyse them
        time_frames = detect_drives(df)
        results = []
        index = 1
        for drive in time_frames:
            results.append(analyseDrive(df, drive, foldername, index))
            index += 1
        # Create the report
        createHTMLReportFile(results, filename)
    # Open the report
    webbrowser.open_new_tab("file://" + os.path.realpath(filename))


def createFilesAndFolders(name="File"):
    """
    Creates a folder with a unique id and in there an html file with the given name.

    Returns filepath, foldername
    """
    filename = str(uuid.uuid4())
    foldername = filename
    filename = os.path.join(foldername, name + ".html")
    if not os.path.exists(foldername):
        os.mkdir(foldername)
    return filename, foldername


def analyseDrive(df, time, foldername, index=1):
    """
    Analyses a drive that is within the time frame given by the time tuple. The index is for the naming of the Report File.

    Returns a dict with all the results. Keys:
    - Time (the original input)
    - Average Speed
    - Unusual Things Backwards (driving backwards and looking forwards)
    - Unusual Things Forwards (driving forward and looking backwards)
    - Folder (the name of the folder of all the files)
    - View Speed Graph (The relative path to the view-speed-graph)
    - Time In Camera (a list with the times in each camera (reference by index))
    - Camera Switches (a 2d-list with the switch from 1-2 being at [0][1])
    - Accidential Switches (a list of accidential switches (each is a dict with "From", "To", "Duration", "At"))
    - Error Freq (a list with the errors and the number of occurences (tuple with [0] = error and [1] = freq))
    - Errors File (the path to the error file )
    - Drive Log (the path to the log of the file with the drive df)
    """

    # set the folder path
    subfolder = "Bericht " + str(index)
    folder = os.path.join(foldername, subfolder)
    if not os.path.exists(folder):
        os.mkdir(folder)

    # Filter the data to match the timestamps of the drive
    filtered_df = df.query(
        "Zeitstempel <= '" + str(time[1]) + "' & Zeitstempel >= '" + str(time[0]) + "'"
    )

    # get the average speed
    average_speed = get_average_speed(filtered_df)

    # Find the times where the view was not equal to the gear and the car was moving
    unusual_things_backwards, unusual_things_forwards = find_unusual_things(filtered_df)

    # Draw a figure with the view as the background and the speed as a curve
    filename_view_speed_graph = draw_view_speed_graph(filtered_df, folder)

    # Figure out the time spend in each Camera
    cameras, switches, accidential_switches = detect_time_spend_in_cam(filtered_df)

    # Get all the error messages by frequency
    errors = filter_errors_by_freq(filtered_df, folder)

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


def detect_drives(df):

    # Neue Erkennung nach Motorzeiten

    # Identifizieren der verschiedenen Fahrten
    start_stop_times = df[df["Eintragstyp"] == "MSTA"]
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


def get_average_speed(filtered_df):
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
    return driven_kilometers / hours


def find_unusual_things(df):
    """
    Detects when the car was moving forward but looking backwards or vice versa
    Returns two dataframes: unusual_things_backwards, unusual_things_forwards
    """
    unusual_things_backwards = df[
        (df["Camera"] == "3")
        & (df["Ganglage (Ist)"].str.contains("V"))
        & (df["Geschwindigkeit [km/h]"] != 0)
    ]
    unusual_things_forwards = df[
        ((df["Camera"] == "1") | (df["Camera"] == "2"))
        & (df["Ganglage (Ist)"].str.contains("R"))
        & (df["Geschwindigkeit [km/h]"] != 0)
    ]
    return unusual_things_backwards, unusual_things_forwards


def draw_view_speed_graph(df, folder):
    fig, ax = plt.subplots(figsize=(30, 10))
    plt.plot(
        df["Zeitstempel"],
        df["Geschwindigkeit [km/h]"],
        color="black",
    )
    x = np.array(df["Zeitstempel"])
    y_min = np.repeat(ax.get_ylim()[0], len(df))
    y_max = np.repeat(ax.get_ylim()[1], len(df))
    y = np.array([y_min, y_max])
    x = np.array([x, x])
    x.shape, y.shape
    ax.pcolormesh(
        x,
        y,
        [df["Camera"][0 : len(df) - 1]],
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
    return filename_view_speed_graph


def detect_time_spend_in_cam(df):
    cameras = [0, 0, 0]
    switches = [[0, 0, 0], [0, 0, 0], [0, 0, 0]]
    accidential_switches = []
    start = df.iloc[0]["Zeitstempel"]
    camera = df.iloc[0]["Camera"] - 1
    for i in range(len(df)):
        cam = df.iloc[i]["Camera"] - 1
        timestamp = df.iloc[i]["Zeitstempel"]
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
    time_passed = (df.iloc[len(df) - 1]["Zeitstempel"] - start).seconds
    cameras[camera] += time_passed
    return cameras, switches, accidential_switches


def filter_errors_by_freq(df, folder):
    filtered_df_errors = df[
        (df["Eintragstext"].str.contains("Kamera"))
        | (df["Eintragstext"].str.contains("Video"))
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
