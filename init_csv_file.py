from tkinter.filedialog import askopenfilename
import pandas as pd


def ask_for_file(self):
    self.filename = askopenfilename()
    init_csv(self)


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
    self.df.to_csv("ouput.csv", sep=";")
