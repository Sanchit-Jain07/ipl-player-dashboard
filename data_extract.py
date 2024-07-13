from sqlalchemy import create_engine, desc
from sqlalchemy.orm import sessionmaker
from models import Players, Teams, Venues, Base, PlayerTeams, Matches, PlayerMatches, Deliveries
import pandas as pd
import requests
from bs4 import BeautifulSoup
import streamlit as st

DATABASE_URL = f"postgresql://{st.secrets['DATABASE_USER']}"\
               f":{st.secrets['DATABASE_PASSWORD']}"\
               f"@{st.secrets['DATABASE_HOST']}"\
               f"/{st.secrets['DATABASE_NAME']}"

engine = create_engine(DATABASE_URL)
Session = sessionmaker(bind=engine)
session = Session()

def get_all_players():
    players = session.query(Players).all()
    player_names = [player.name for player in players]
    return player_names

def season_wise_batting_stats(player_matches, player):
    stats = {}
    deliveries = session.query(Deliveries).filter_by(batter_id=player.id)
    deliveries_df = pd.read_sql(deliveries.statement, deliveries.session.bind)
    for match in player_matches:
        if match.season not in stats:
            stats[match.season] = {
                "runs": 0,
                "balls": 0,
                "fours": 0,
                "sixes": 0,
                "dismissals": 0,
                "fifties": 0,
                "hundreds": 0
            }
        player_runs = deliveries_df[deliveries_df["match_id"]==match.match_id]["runs"].sum()
        player_balls = deliveries_df[(deliveries_df["extras_type"] != "wides") & (deliveries_df["match_id"]==match.match_id)].shape[0]
        player_fours = deliveries_df[(deliveries_df["runs"]==4) & (deliveries_df["match_id"]==match.match_id)].shape[0]
        player_sixes = deliveries_df[(deliveries_df["runs"]==6) & (deliveries_df["match_id"]==match.match_id)].shape[0]
        player_outs = deliveries_df[(deliveries_df["player_out_id"]==player.id) & (deliveries_df["match_id"]==match.match_id)].shape[0]
        if player_runs >= 50 and player_runs < 100:
            stats[match.season]["fifties"] += 1
        if player_runs >= 100:
            stats[match.season]["hundreds"] += 1
        stats[match.season]["runs"] += player_runs
        stats[match.season]["balls"] += player_balls
        stats[match.season]["fours"] += player_fours
        stats[match.season]["sixes"] += player_sixes
        stats[match.season]["dismissals"] += player_outs
    return stats



def season_wise_bowling_stats(player_matches, player):
    stats = {}
    wicket_types = ["bowled", "caught", "lbw", "stumped", "caught and bowled", "hit wicket"]
    deliveries = session.query(Deliveries).filter_by(bowler_id=player.id)
    deliveries_df = pd.read_sql(deliveries.statement, deliveries.session.bind)
    for match in player_matches:
        if match.season not in stats:
            stats[match.season] = {
                "balls": 0,
                "runs": 0,
                "wickets": 0
            }
        player_runs = deliveries_df[deliveries_df["match_id"]==match.match_id]["runs"].sum()
        player_runs += deliveries_df[(deliveries_df["extras_type"] != "byes") & (deliveries_df["extras_type"] != "legbyes") & (deliveries_df["match_id"] == match.match_id)]["extras"].sum()
        player_balls = deliveries_df[(deliveries_df["extras_type"] != "wides") & (deliveries_df["extras_type"] != "noballs") & (deliveries_df["match_id"] == match.match_id)].shape[0]
        player_wickets = deliveries_df[(deliveries_df["wicket"].isin(wicket_types)) & (deliveries_df["match_id"] == match.match_id)].shape[0]
        stats[match.season]["runs"] += player_runs
        stats[match.season]["balls"] += player_balls
        stats[match.season]["wickets"] += player_wickets
    return stats

def get_bowling_stats(player_name):
    player = session.query(Players).filter_by(name=player_name).first()
    player_matches = session.query(PlayerMatches).filter_by(player_id=player.id).order_by(desc(PlayerMatches.date)).all()
    season_stats = season_wise_bowling_stats(player_matches, player)
    overall_stats = {
        "runs": 0,
        "balls": 0,
        "wickets": 0,
        
    }
    for season, stats in season_stats.items():
        overall_stats["runs"] += stats["runs"]
        overall_stats["balls"] += stats["balls"]
        overall_stats["wickets"] += stats["wickets"]
    return overall_stats, season_stats

def get_batting_stats(player_name):
    player = session.query(Players).filter_by(name=player_name).first()
    player_matches = session.query(PlayerMatches).filter_by(player_id=player.id).order_by(desc(PlayerMatches.date)).all()
    season_stats = season_wise_batting_stats(player_matches, player)
    overall_stats = {
        "runs": 0,
        "balls": 0,
        "fours": 0,
        "sixes": 0,
        "dismissals": 0,
        "fifties": 0,
        "hundreds": 0
    }
    for season, stats in season_stats.items():
        overall_stats["runs"] += stats["runs"]
        overall_stats["balls"] += stats["balls"]
        overall_stats["fours"] += stats["fours"]
        overall_stats["sixes"] += stats["sixes"]
        overall_stats["dismissals"] += stats["dismissals"]
        overall_stats["fifties"] += stats["fifties"]
        overall_stats["hundreds"] += stats["hundreds"]
    return overall_stats, season_stats

def match_number(player):
    player = session.query(Players).filter_by(name=player).first()
    player_matches = session.query(PlayerMatches).filter_by(player_id=player.id).all()
    return len(player_matches)

def get_player_espn_id(player_name):
    player = session.query(Players).filter_by(name=player_name).first()
    with open("people.csv") as file:
        player_df = pd.read_csv(file)
        player_row = player_df[player_df["name"] == player_name]
        if player_row.empty:
            return None
        return int(player_row["key_cricinfo"].values[0])
    
def get_player_meta(player_espn_id):
    data = requests.get(f"https://www.espncricinfo.com/*/content/player/{player_espn_id}.html")
    soup = BeautifulSoup(data.content, "html5lib")
    h1 = soup.find("h1", attrs={"class": "ds-text-title-l ds-font-bold"})
    player_meta_data = {
        "player_full_name": None,
        "playing_role": None,
        "batting_style": None,
        "bowling_style": None
    }
    player_full_name = h1.text
    main_div = soup.find("div", attrs={"class": "ds-grid lg:ds-grid-cols-3 ds-grid-cols-2 ds-gap-4 ds-mb-8"})
    divs = main_div.find_all("div")
    for div in divs:
        if "Playing Role" in div.text:
            player_meta_data["playing_role"] = div.find("span").text
        if "Batting Style" in div.text:
            player_meta_data["batting_style"] = div.find("span").text
        if "Bowling Style" in div.text:
            player_meta_data["bowling_style"] = div.find("span").text

    player_meta_data["player_full_name"] = player_full_name

    player_img = soup.find("img", attrs={"alt": player_full_name})
    player_meta_data["player_img"] = player_img["src"]
    return player_meta_data

def get_player_teams(player_name):
    player = session.query(Players).filter_by(name=player_name).first()
    player_teams = session.query(PlayerTeams).filter_by(player_id=player.id).all()
    team_names = {}
    for player_team in player_teams:
        team_id = player_team.team_id
        team = session.query(Teams).filter_by(id=team_id).first()
        team_names[player_team.season] = team.name
    return team_names
