from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import json
from models import Teams, Players, Venues, Base, PlayerTeams, Matches, PlayerMatches, Deliveries
from utils import VENUE_MAP
import os

engine = create_engine('YOUR_DATABASE_URL')

def create_tables():
    Base.metadata.create_all(engine, checkfirst=True)

Session = sessionmaker(bind=engine)
session = Session()

json_files = []
directory = './match_data' # Path to the directory containing the cricsheet JSON files

TEAM_MAP = {
    'Delhi Daredevils': 'Delhi Capitals',
    'Kings XI Punjab': 'Punjab Kings',
    'Rising Pune Supergiants': 'Rising Pune Supergiant',
    'Royal Challengers Bangalore': 'Royal Challengers Bengaluru',
    'Pune Warriors': 'Pune Warriors India'
}

for filename in os.listdir(directory):
    if filename.endswith('.json'):
        json_files.append(filename)

def insert_teams():
    with open('team_list.txt') as file:
        teams = file.read().splitlines()
        for team in teams:
            session.add(Teams(name=team))
        session.commit()

create_tables()

def insert_players():
    for filename in json_files:
        with open(f'{'./match_data'}/{filename}') as file:
            data = json.load(file)
            for team in data['info']['players']:
                for player in data['info']['players'][team]:
                    season = data['info']['dates'][0].split('-')[0]
                    check_player = session.query(Players).filter_by(name=player).first()
                    if team in TEAM_MAP:
                        team = TEAM_MAP[team]
                    try:
                        team_id = session.query(Teams).filter_by(name=team).first().id
                    except:
                        print(team)
                        exit()
                    if not check_player:
                        new_player = Players(name=player)
                        session.add(new_player)
                        session.flush()
                        player_id = new_player.id
                        session.add(PlayerTeams(player_id=player_id, team_id=team_id, season=season))
                    else:
                        check_player_team = session.query(PlayerTeams).filter_by(player_id=check_player.id, team_id=team_id, season=season).first()
                        player_id = check_player.id
                        if not check_player_team:
                            session.add(PlayerTeams(player_id=player_id, team_id=team_id, season=season))
                    session.commit()

def insert_venues():
    with open('unique_venues.txt') as file:
        venues = file.read().splitlines()
        for venue in venues:
            if(venue in VENUE_MAP):
                venue = VENUE_MAP[venue]
            check_venue = session.query(Venues).filter_by(name=venue).first()
            if not check_venue:
                session.add(Venues(name=venue))
        session.commit()

def insert_matches():
    for filename in json_files:
        with open(f'./match_data/{filename}') as file:
            data = json.load(file)
            season = data['info']['dates'][0].split('-')[0]
            team1 = data['info']['teams'][0]
            date=data['info']['dates'][0]
            team2 = data['info']['teams'][1]
            if team1 in TEAM_MAP:
                team1 = TEAM_MAP[team1]
            if team2 in TEAM_MAP:
                team2 = TEAM_MAP[team2]
            team1_id = session.query(Teams).filter_by(name=team1).first().id
            team2_id = session.query(Teams).filter_by(name=team2).first().id
            venue = data['info']['venue']
            if venue in VENUE_MAP:
                venue = VENUE_MAP[venue]
            venue_id = session.query(Venues).filter_by(name=venue).first().id
            try:
                winner = data['info']['outcome']['winner']
                if winner in TEAM_MAP:
                    winner = TEAM_MAP[winner]
            except:
                winner = None
            winner_id = session.query(Teams).filter_by(name=winner).first().id if winner else None
            new_match = Matches(season=season, date=date, team1_id=team1_id, team2_id=team2_id, venue_id=venue_id, winner_id=winner_id)
            session.add(new_match)
            session.flush()
            match_id = new_match.id
            for team in data['info']['players']:
                for player in data['info']['players'][team]:
                    if team in TEAM_MAP:
                        team = TEAM_MAP[team]
                    player_id = session.query(Players).filter_by(name=player).first().id
                    session.add(PlayerMatches(player_id=player_id, match_id=match_id, season=season, date=date))
        session.commit()

def insert_deliveries():
    for filename in json_files:
        with open(f'./match_data/{filename}') as file:
            data = json.load(file)
            innings = min(2, len(data['innings']))
            team1 = data['info']['teams'][0]
            team2 = data['info']['teams'][1]
            date = data['info']['dates'][0]
            if team1 in TEAM_MAP:
                team1 = TEAM_MAP[team1]
            if team2 in TEAM_MAP:
                team2 = TEAM_MAP[team2]
            matches = session.query(Matches).filter_by(date=date).all()
            match_id = None
            for match in matches:
                if match.team1_id == session.query(Teams).filter_by(name=team1).first().id and match.team2_id == session.query(Teams).filter_by(name=team2).first().id:
                    match_id = match.id
            for inning in range(innings):
                batting_team = data['innings'][inning]['team']
                if batting_team in TEAM_MAP:
                    batting_team = TEAM_MAP[batting_team]
                batting_team_id = session.query(Teams).filter_by(name=batting_team).first().id
                bowling_team = team1 if batting_team == team2 else team2
                bowling_team_id = session.query(Teams).filter_by(name=bowling_team).first().id
                inning_data = data['innings'][inning]
                for overs in inning_data['overs']:
                    over = overs['over']
                    for delivery in range(len(overs['deliveries'])):
                        ball_data = overs['deliveries'][delivery]
                        ball = delivery + 1
                        extras_type = None
                        if 'extras' in ball_data:
                            if 'wides' in ball_data['extras']:
                                extras_type = 'wides'
                            elif 'noballs' in ball_data['extras']:
                                extras_type = 'noballs'
                            else:
                                extras_type = list(ball_data['extras'].keys())[0]
                        runs = ball_data['runs']['batter']
                        extras = ball_data['runs']['extras']
                        batter = ball_data['batter']
                        bowler = ball_data['bowler']
                        batter_id = session.query(Players).filter_by(name=batter).first().id
                        bowler_id = session.query(Players).filter_by(name=bowler).first().id
                        wicket = ball_data.get('wickets', None)
                        player_out_id = None
                        wicket_type = None
                        if wicket:
                            player_out = wicket[0]['player_out']
                            player_out_id = session.query(Players).filter_by(name=player_out).first().id
                            wicket_type = wicket[0]['kind']
                        new_delivery = Deliveries(match_id=match_id, inning=inning+1, batting_team_id=batting_team_id, bowling_team_id=bowling_team_id, over=over, ball=ball, batter_id=batter_id, bowler_id=bowler_id, runs=runs, extras=extras, wicket=wicket_type, player_out_id=player_out_id, extras_type=extras_type)
                        session.add(new_delivery)
            session.commit()

insert_teams()
insert_players()
insert_venues()
insert_matches()
insert_deliveries()


                

