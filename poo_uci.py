import requests
from bs4 import BeautifulSoup
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from unidecode import unidecode
from datetime import datetime
from IPython.display import display

class Rider:
    def __init__(self, ridername, ridercode):
        self.ridername = ridername
        self.ridercode = ridercode
        self.uci_points = None
        self.racedays = None
        self.age = None
        self.weight = None
        self.height = None

    def get_rider_data(self):
        """
        Fetch the data for the rider such as UCI points, racedays, age, weight, and height.
        """
        self.uci_points = self.get_uci_points()
        self.racedays = self.get_days()
        self.age = self.get_age()
        self.weight = self.get_weight()
        self.height = self.get_height()

    def get_uci_points(self):
        url = f'https://www.procyclingstats.com/rider/{self.ridercode}/{datetime.now().strftime("%Y")}'
        response = requests.get(url)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            uci_div = soup.find('div', class_='rdrResultsSum')
            if uci_div:
                uci_text = uci_div.text
                index_uci = uci_text.find('UCI')
                if index_uci != -1:
                    uci_points = ''.join(filter(str.isdigit, uci_text[index_uci + 3:]))
                    return int(uci_points) if uci_points else None
        return None

    def get_days(self):
        url = f'https://www.procyclingstats.com/rider/{self.ridercode}/{datetime.now().strftime("%Y")}'
        response = requests.get(url)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            div = soup.find('div', class_='rdrResultsSum')
            if div:
                text = div.text
                index_days = text.find('days')
                if index_days != -1:
                    days = ''.join(filter(str.isdigit, text[index_days - 6:]))
                    return int(days) if days else None
        return None

    def get_age(self):
        url = f'https://www.procyclingstats.com/rider/{self.ridercode}/{datetime.now().strftime("%Y")}'
        response = requests.get(url)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            div = soup.find('div', class_='rdr-info-cont')
            if div:
                text = div.text
                index_age = text.find('(')
                if index_age != -1:
                    age = ''.join(filter(str.isdigit, text[index_age:]))
                    return int(age) if age else None
        return None

    def get_weight(self):
        url = f'https://www.procyclingstats.com/rider/{self.ridercode}/{datetime.now().strftime("%Y")}'
        response = requests.get(url)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            div = soup.find('div', class_='rdr-info-cont')
            if div:
                text = div.text
                index_w = text.find('Weight')
                if index_w != -1:
                    w = ''.join(filter(str.isdigit, text[index_w:]))
                    return int(w) if w else None
        return None

    def get_height(self):
        url = f'https://www.procyclingstats.com/rider/{self.ridercode}/{datetime.now().strftime("%Y")}'
        response = requests.get(url)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            div = soup.find('div', class_='rdr-info-cont')
            if div:
                text = div.text
                index_h = text.find('Height')
                if index_h != -1:
                    h = ''.join([char for char in text[index_h:] if char.isdigit() or char == "."])
                    return float(h) if h else None
        return None

class Team:
    def __init__(self, teamcode, teamname=None):
        self.teamcode = teamcode
        self.teamname = teamname if teamname else teamcode
        self.riders = self.get_riders()

    def get_riders(self):
        """
        Fetches all the riders of the team and returns them as a list of Rider objects.
        """
        url = f'https://www.procyclingstats.com/team/{self.teamcode}-{datetime.now().strftime("%Y")}'
        response = requests.get(url)
        soup = BeautifulSoup(response.text, 'html.parser')
        table = soup.find('table')
        rows = table.find_all('tr')[1:]
        riders = []

        for row in rows:
            cols = [col.text.strip() for col in row.find_all('td')]
            ridername = cols[1]
            ridercode = unidecode(ridername).replace("'", " ").replace(' ', '-').lower()
            rider = Rider(ridername, ridercode)
            riders.append(rider)

        return riders

    def update_rider_data(self):
        """
        Updates all riders with their UCI points, race days, age, etc.
        """
        for rider in self.riders:
            rider.get_rider_data()

    def get_team_uci_points(self):
        """
        Returns the UCI points breakdown of the team as a DataFrame.
        """
        data = []
        for rider in self.riders:
            if rider.uci_points is None:
                rider.get_uci_points()
            data.append({"Rider": rider.ridername, "UCI Pts": rider.uci_points or 0})
        df = pd.DataFrame(data).fillna(0)
        return df.sort_values(by="UCI Pts", ascending=False).reset_index(drop=True)

    def plot_uci(self):
        """
        Plots the UCI points for the team.
        """
        df = self.get_team_uci_points().head(20).sort_values(by="UCI Pts", ascending=True)
        plt.figure(figsize=(10, 7))
        bars = plt.barh(df["Rider"], df["UCI Pts"], color="mediumblue")
        for bar in bars:
            width = bar.get_width()
            if width >= 30:
                plt.text(width, bar.get_y() + bar.get_height() / 2, f'{width:.0f} pts', ha='right', va='center', c="white", fontsize=8, fontweight='bold')
        plt.xlabel("UCI Pts")
        plt.title(f"UCI Breakdown for {self.teamname} - {datetime.now().strftime('%d-%m-%Y')}", fontweight='bold')
        plt.grid(axis="x", linestyle=':')
        plt.show()

    def team_info_table(self):
        """
        Returns a detailed DataFrame with all riders' information such as UCI points, racedays, age, weight, and height.
        """
        data = []
        for rider in self.riders:
            rider.get_rider_data()
            data.append({
                "Rider": rider.ridername,
                "UCI Pts": rider.uci_points or 0,
                "Racedays": rider.racedays or 0,
                "Age": rider.age or 0,
                "Weight": rider.weight or 0,
                "Height": rider.height or 0
            })
        df = pd.DataFrame(data).fillna(0)
        df = df.sort_values(by="UCI Pts", ascending=False).reset_index(drop=True)
        return df

# Example usage:
team = Team('alpecin-deceuninck')
team.update_rider_data()
print(team.get_team_uci_points())
team.plot_uci()
display(team.team_info_table())
