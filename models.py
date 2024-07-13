from sqlalchemy import Column, Integer, String, UniqueConstraint, ForeignKey
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

# Team model
class Teams(Base):
    __tablename__ = 'teams'
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False, unique=True)

    def __init__(self, name):
        self.name = name

    def __repr__(self):
        return f'<Team(name={self.name})>'
    
# Player model
class Players(Base):
    __tablename__ = 'players'
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False, unique=True)

    def __init__(self, name):
        self.name = name

    def __repr__(self):
        return f'<Player(name={self.name})>'
    
# Venue model
class Venues(Base):
    __tablename__ = 'venues'
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False, unique=True)

    def __repr__(self):
        return f'<Venue(name={self.name})>'
    
# PlayerTeam model
class PlayerTeams(Base):
    __tablename__ = 'player_teams'
    id = Column(Integer, primary_key=True)
    player_id = Column(Integer, nullable=False)
    team_id = Column(Integer, nullable=False)
    season = Column(Integer, nullable=False)

    def __init__(self, player_id, team_id, season):
        self.player_id = player_id
        self.team_id = team_id
        self.season = season

    def __repr__(self):
        return f'<PlayerTeam(player_id={self.player_id}, team_id={self.team_id})>'
    
# Match model
class Matches(Base):
    __tablename__ = 'matches'
    id = Column(Integer, primary_key=True)
    season = Column(Integer, nullable=False)
    date = Column(String, nullable=False)
    team1_id = Column(Integer, ForeignKey('teams.id'), nullable=False)
    team2_id = Column(Integer, ForeignKey('teams.id'), nullable=False)
    venue_id = Column(Integer, ForeignKey('venues.id'), nullable=False)
    winner_id = Column(Integer, ForeignKey('teams.id'))

    def __init__(self, season, date, team1_id, team2_id, venue_id, winner_id):
        self.season = season
        self.date = date
        self.team1_id = team1_id
        self.team2_id = team2_id
        self.venue_id = venue_id
        self.winner_id = winner_id

    def __repr__(self):
        return f'<Match(date={self.date}, team1_id={self.team1_id}, team2_id={self.team2_id})>'
    
# PlayerMatch model
class PlayerMatches(Base):
    __tablename__ = 'player_matches'
    id = Column(Integer, primary_key=True)
    player_id = Column(Integer, ForeignKey('players.id'), nullable=False)
    match_id = Column(Integer, ForeignKey('matches.id'), nullable=False)
    season = Column(Integer, nullable=False)
    date = Column(String, nullable=False)

    def __init__(self, player_id, match_id, season, date):
        self.player_id = player_id
        self.match_id = match_id
        self.season = season
        self.date = date

    def __repr__(self):
        return f'<PlayerMatch(player_id={self.player_id}, match_id={self.match_id})>'
    

# Delivery model
class Deliveries(Base):
    __tablename__ = 'deliveries'
    id = Column(Integer, primary_key=True)
    match_id = Column(Integer, ForeignKey('matches.id'), nullable=False)
    inning = Column(Integer, nullable=False)
    batting_team_id = Column(Integer, ForeignKey('teams.id'), nullable=False)
    bowling_team_id = Column(Integer, ForeignKey('teams.id'), nullable=False)
    over = Column(Integer, nullable=False)
    ball = Column(Integer, nullable=False)
    batter_id = Column(Integer, ForeignKey('players.id'), nullable=False)
    bowler_id = Column(Integer, ForeignKey('players.id'), nullable=False)
    runs = Column(Integer, nullable=False)
    extras = Column(Integer, nullable=False)
    extras_type = Column(String)
    wicket = Column(String)
    player_out_id = Column(Integer, ForeignKey('players.id'))

    def __init__(self, match_id, inning, batting_team_id, bowling_team_id, over, ball, batter_id, bowler_id, runs, extras, extras_type, wicket, player_out_id):
        self.match_id = match_id
        self.inning = inning
        self.batting_team_id = batting_team_id
        self.bowling_team_id = bowling_team_id
        self.over = over
        self.ball = ball
        self.batter_id = batter_id
        self.bowler_id = bowler_id
        self.runs = runs
        self.extras = extras
        self.extras_type = extras_type
        self.wicket = wicket
        self.player_out_id = player_out_id

    def __repr__(self):
        return f'<Delivery(match_id={self.match_id}, inning={self.inning}, over={self.over}, ball={self.ball})>'

    