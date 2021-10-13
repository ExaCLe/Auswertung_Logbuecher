import numpy as np
import os


def createHTMLReportFile(reports, filename):

    # Create a nice header
    writeHTMLHeader(filename)

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
                "<img src='" + result["View Speed Graph"] + "' style='width:100%;''/>"
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


def writeHTMLHeader(filename):
    with open("header.html", "r") as file:
        text = file.read()

    with open(filename, mode="w") as file:
        file.write(text)


def to_time_format(seconds):
    return (
        "{:02d}".format(seconds // 3600)
        + ":"
        + "{:02d}".format(seconds % 3600 // 60)
        + ":"
        + "{:02d}".format(seconds % 60)
    )
