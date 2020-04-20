from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField, BooleanField, SelectField
from wtforms.validators import DataRequired, NumberRange, Optional
from wtforms_components import DateField, TimeField, IntegerField, validators
from datetime import datetime, date


class NewTournament(FlaskForm):
    name = StringField('Name', validators=[
        DataRequired('A tournament name is requiered')])
    password = PasswordField('Pasword', validators=[Optional()])
    players_admited = SelectField('Number of players', validators=[
                                  Optional()], choices=[('2', 2), ('4', 4), ('8', 8), ('16', 16)], default=2)
    discord_server_id = IntegerField(
        'Discord Server ID', validators=[Optional()])
    elo_limit_low = IntegerField('Lowest ELO Limit', validators=[DataRequired(
        'ELO limit is requiered'), NumberRange(min=1, max=3000)])
    elo_limit_high = IntegerField('Highest ELO Limit', validators=[DataRequired(
        'ELO limit is requiered'), NumberRange(min=1, max=3000)])
    start_date = DateField('Start Date', format='%Y-%m-%d', validators=[DataRequired(
        'Start date is requiered'), validators.DateRange(min=date.today())])
    start_time = TimeField('Start Time', format='%H:%M', validators=[
                           DataRequired('Start time is requiered')])
    end_date = DateField('End Date', format='%Y-%m-%d', validators=[DataRequired(
        'End date is requiered'), validators.DateRange(min=date.today())])
    end_time = TimeField('End Time', format='%H:%M', validators=[
                         DataRequired('End time is requiered')])


class JoinTournament(FlaskForm):
    password = PasswordField('Pasword', validators=[Optional()])
    join = SubmitField('Join!')


