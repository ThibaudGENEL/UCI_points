from functions_UCI import get_riders, tableau_UCI, plot_uci  #temporary functions
from functions_UCI import main_uci, plot_compare_uci, classement_UCI_equipes  # my functions
import matplotlib.pyplot as plt
import pandas as pd
import datetime
from IPython.display import display
import warnings
warnings.filterwarnings("ignore")
import fastapi
import numpy as np
plt.rcParams["font.family"] = "Garamond"
plt.style.use('seaborn-pastel')


# main_uci("groupama-fdj", "Groupama-FDJ")
# main_uci("decathlon-ag2r-la-mondiale", "Decathlon AG2R")
# classement_UCI_equipes()
# plot_compare_uci("groupama-fdj", "decathlon-ag2r-la-mondiale")

app = fastapi.FastAPI()
@app.get("/BreakdownUCI")
async def main_uci(teamcode, teamname = None, to_plot = True):
    '''
    UCI Points Breakdown for the selected team.
    
    Parameters:
    ----------
    teamcode : str
        String to use in the URL (e.g., "alpecin-deceuninck").
    
    teamname : str, optional
        Name of the team to display in the outputs. If not provided, defaults to the `teamcode`.
    
    to_plot : bool, optional
        If True, a plot will be displayed. Otherwise, a table will be shown. Defaults to True.
    
    Available team codes:
    ---------------------
    - 'alpecin-deceuninck': 'Alpecin-Deceuninck'
    - 'arkea-b-b-hotels': 'Arkéa - B&B Hôtels'
    - 'astana-qazaqstan-team': 'Astana Qazaqstan'
    - 'bahrain-victorious': 'Bahrain-Victorious'
    - 'bora-hansgrohe': 'Bora-Hansgrohe'
    - 'cofidis': 'Cofidis'
    - 'decathlon-ag2r-la-mondiale': 'Décathlon-AG2R'
    - 'ef-education-easypost': 'EF Education-Easypost'
    - 'groupama-fdj': 'Groupama-FDJ'
    - 'ineos-grenadiers': 'Ineos Grenadiers'
    - 'intermarche-wanty': 'Intermarché-Wanty'
    - 'lidl-trek': 'Lidl-Trek'
    - 'movistar-team': 'Movistar'
    - 'soudal-quick-step': 'Soudal-QuickStep'
    - 'team-dsm-firmenich-postnl': 'Team DSM'
    - 'team-jayco-alula': 'Team Jayco-AlUla'
    - 'team-visma-lease-a-bike': 'Visma Lease-a-Bike'
    - 'uae-team-emirates': 'UAE Team Emirates'
    - 'lotto-dstny': 'Lotto-Dstny'
    - 'israel-premier-tech': 'Israel-Premier Tech'
    - 'uno-x-mobility': 'Uno-X'
    - 'totalenergies': 'TotalEnergies'
    '''
    if teamname is None:
        teamname = teamcode
    coureurs = get_riders(teamcode)
    # Dictionnaire des remplacements
    remplacements = {
        "romain-gregoire": "romain-gregoire1",
        "mattias-skjelmose": "mattias-skjelmose-jensen",
        "igor-arrieta": "igor-arrieta-lizarraga",
        "juan-ayuso": "juan-ayuso-pesquera",
        "OßSCHARTNER Felix GR": "GROSSSCHARTNER Felix",
        "ossschartner-felix-gr": "felix-grossschartner",
        "magnus-cort": "magnus-cort-nielsen",
        "carlos-rodriguez": "carlos-rodriguez-cano",
        "brandon-smith-rivera": "brandon-smith-rivera-vargas",
        "santiago-buitrago": "santiago-buitrago-sanchez",
        "fred-wright": "alfred-wright",
        "jesus-herrada": "jesus-herrada-lopez"
    }
    for ancien, nouveau in remplacements.items():
        coureurs.replace(ancien, nouveau, inplace=True)

    df = tableau_UCI(coureurs)
    if teamcode == "groupama-fdj":
        df.loc[df["Rider"] == "Thibaud GRUEL", "UCI Pts"] -= 25
        df.sort_values(by = "UCI Pts", ascending=False)
        df["#"] = np.arange(df.shape[0]) + 1
    if to_plot:
        plot_uci(df, teamname)
    return fastapi.Response(content=df.to_json(), media_type='application/json', status_code=200)


@app.get("/Ranking")
async def classement_UCI_equipes():
    '''
    Calculates and displays the UCI Ranking by teams, including the 22 best teams
    '''
    team_mapping = {
        'alpecin-deceuninck': 'Alpecin-Deceuninck',
        'arkea-b-b-hotels': 'Arkéa - B&B Hôtels',
        'astana-qazaqstan-team': 'Astana Qazaqstan',
        'bahrain-victorious': 'Bahrain-Victorious',
        'bora-hansgrohe': 'Bora-Hansgrohe',
        'cofidis': 'Cofidis',
        'decathlon-ag2r-la-mondiale': 'Décathlon-AG2R',
        'ef-education-easypost': 'EF Education-Easypost',
        'groupama-fdj': 'Groupama-FDJ',
        'ineos-grenadiers': 'Ineos Grenadiers',
        'intermarche-wanty': 'Intermarché-Wanty',
        'lidl-trek': 'Lidl-Trek',
        'movistar-team': 'Movistar',
        'soudal-quick-step': 'Soudal-QuickStep',
        'team-dsm-firmenich-postnl': 'Team DSM',
        'team-jayco-alula': 'Team Jayco-AlUla',
        'team-visma-lease-a-bike': 'Visma Lease-a-Bike',
        'uae-team-emirates': 'UAE Team Emirates',
        'lotto-dstny': 'Lotto-Dstny',
        'israel-premier-tech': 'Israel-Premier Tech',
        'uno-x-mobility': 'Uno-X',
        'totalenergies': 'TotalEnergies'
    }
    final_df = pd.DataFrame({"Team": [team_mapping[team] for team in team_mapping]})
    teams_totals = []
    for team in team_mapping:  # boucle equipes
        team_df = main_uci(team, to_plot=False)
        # display(team_df)
        team_df = team_df[0:20]
        team_total = np.sum(team_df["UCI Pts"])
        teams_totals.append(team_total)
    final_df["UCI Pts"] = pd.Series(teams_totals)  
    final_df = final_df.sort_values(by = "UCI Pts", ascending=False).reset_index(drop=False)
    final_df["index"] = np.arange(final_df.shape[0]) + 1
    final_df.rename(columns={"index":"#"}, inplace=True)
    display(final_df)
    data = final_df.sort_values(by = "UCI Pts", ascending=True)
    today = datetime.now().strftime("%d-%m-%Y")
    # PLOT
    plt.figure(figsize=(10, 7))
    bars = plt.barh(data["Team"], data["UCI Pts"], color = "teal")
    for bar in bars:        #ajout des % en etiquette
        width = bar.get_width()
        if (width >= 20):
            plt.text(width,
                bar.get_y() + bar.get_height() / 2,
                f'{width:.0f} pts',
                ha='right', 
                va='center',
                c="white",
                fontsize = 8,
                fontweight = 'bold')
    plt.xlabel("UCI Pts")
    plt.yticks(fontsize=9)
    plt.grid(axis="x", linestyle=':')
    plt.title(f"UCI Ranking 2024 - {today}", fontweight = 'bold')
    plt.show()
