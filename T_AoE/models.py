from . import db
from flask_user import UserMixin
from flask_wtf import FlaskForm
from wtforms import SelectField, SubmitField, validators


class User(db.Model, UserMixin):
    __tablename__ = 'users'
    id = db.Column(db.Integer(), primary_key=True)
    email = db.Column(db.Unicode(255), nullable=False,
                      server_default=u'', unique=True)
    username = db.Column(db.Unicode(50), nullable=False,
                         server_default=u'', unique=True)
    steam_id = db.Column(db.Integer(), nullable=True)
    email_confirmed_at = db.Column(db.DateTime())
    password = db.Column(db.String(255), nullable=False, server_default='')
    active = db.Column('is_active', db.Boolean(),
                       nullable=False, server_default='0')
    icon = db.Column(db.Integer(), nullable=False, server_default='1')
    roles = db.relationship('Role', secondary='users_roles',
                            backref=db.backref('users', lazy='dynamic'))
    tournaments = db.relationship(
        'Tournament', secondary='users_tournaments', backref=db.backref('users', lazy='dynamic'))


class Role(db.Model):
    __tablename__ = 'roles'
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(50), nullable=False,
                     server_default=u'', unique=True)
    label = db.Column(db.Unicode(255), server_default=u'')


class UsersRoles(db.Model):
    __tablename__ = 'users_roles'
    id = db.Column(db.Integer(), primary_key=True)
    user_id = db.Column(db.Integer(), db.ForeignKey(
        'users.id', ondelete='CASCADE'))
    role_id = db.Column(db.Integer(), db.ForeignKey(
        'roles.id', ondelete='CASCADE'))


class Tournament(db.Model):
    __tablename__ = 'tournaments'
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.Unicode(50), nullable=False,
                     server_default=u'', unique=True)
    created_at = db.Column(db.DateTime())
    published_at = db.Column(db.DateTime())
    password = db.Column(db.String(255), nullable=True)
    is_public = db.Column(db.Boolean(), nullable=False, server_default='0')
    is_open = db.Column(db.Boolean(), nullable=False, server_default='1')
    last_update = db.Column(db.DateTime())
    players_admited = db.Column(
        db.Integer(), nullable=False, server_default='4')
    elo_limit_high = db.Column(db.Integer())
    elo_limit_low = db.Column(db.Integer())
    start_date = db.Column(db.DateTime())
    end_date = db.Column(db.DateTime())
    discord_server_id = db.Column(db.Integer(), nullable=True)
    rounds = db.relationship(
        'Round', secondary='tournaments_rounds', backref=db.backref('tournaments', lazy='dynamic'))
    matches = db.relationship(
        'Match', secondary='tournaments_matches', backref=db.backref('tournaments', lazy='dynamic'))


class UsersTournaments(db.Model):
    __tablename__ = 'users_tournaments'
    id = db.Column(db.Integer(), primary_key=True)
    user_id = db.Column(db.Integer(), db.ForeignKey(
        'users.id', ondelete='CASCADE'))
    tournament_id = db.Column(db.Integer(), db.ForeignKey(
        'tournaments.id', ondelete='CASCADE'))
    result = db.Column(db.Unicode(50), server_default=u'Host')


class Round(db.Model):
    __tablename__ = 'rounds'
    id = db.Column(db.Integer(), primary_key=True)
    round_number = db.Column(db.Integer(), nullable=False)
    round_type = db.Column(db.Unicode(50), nullable=False,
                           server_default=u'')


class TournamentsRounds(db.Model):
    __tablename__ = 'tournaments_rounds'
    id = db.Column(db.Integer(), primary_key=True)
    tournament_id = db.Column(db.Integer(), db.ForeignKey(
        'tournaments.id', ondelete='CASCADE'))
    round_id = db.Column(db.Integer(), db.ForeignKey(
        'rounds.id', ondelete='CASCADE'))


class Match(db.Model):
    __tablename__ = 'matches'
    id = db.Column(db.Integer(), primary_key=True)
    match_number = db.Column(db.Integer(), nullable=False)
    users = db.relationship(
        'User', secondary='users_matches', backref=db.backref('matches', lazy='dynamic'))


class UsersMatches(db.Model):
    __tablename__ = 'users_matches'
    id = db.Column(db.Integer(), primary_key=True)
    user_id = db.Column(db.Integer(), db.ForeignKey(
        'users.id', ondelete='CASCADE'), nullable=True)
    match_id = db.Column(db.Integer(), db.ForeignKey(
        'matches.id', ondelete='CASCADE'), nullable=True)
    points = db.Column(db.Integer(), nullable=False, server_default='0')


class TournamentMatches(db.Model):
    __tablename__ = 'tournaments_matches'
    id = db.Column(db.Integer(), primary_key=True)
    tournament_id = db.Column(db.Integer(), db.ForeignKey(
        'tournaments.id', ondelete='CASCADE'))
    match_id = db.Column(db.Integer(), db.ForeignKey(
        'matches.id', ondelete='CASCADE'))
