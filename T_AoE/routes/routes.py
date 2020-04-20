from flask import Blueprint, redirect, render_template, request, url_for, jsonify
from urllib.parse import urlencode
from urllib.request import urlopen
import urllib.request
import json
import datetime
from T_AoE.models import *
from T_AoE import db
from flask_user import current_user, roles_required, login_required
from T_AoE.forms import *
from datetime import datetime
import sqlalchemy
import webbrowser

main = Blueprint('main', __name__, template_folder='templates')


@main.route('/')
def home():
    if current_user.is_authenticated and current_user.roles == []:
        return render_template('main/roles.html')
    else:
        past_tournaments = db.session.query(Tournament).join(User.tournaments).with_entities(Tournament.id, Tournament.name, Tournament.start_date, Tournament.end_date, Tournament.players_admited, Tournament.elo_limit_low, Tournament.elo_limit_high, Tournament.published_at, User.username).filter(
            Tournament.is_public == 1, Tournament.start_date <= datetime.now(), UsersTournaments.result == 'Host').order_by(Tournament.start_date).limit(5).all()
        upcoming_tournaments = db.session.query(Tournament).join(User.tournaments).join(UsersTournaments, UsersTournaments.user_id == User.id).with_entities(Tournament.id,  Tournament.name, Tournament.start_date, Tournament.end_date, Tournament.players_admited, Tournament.elo_limit_low, Tournament.elo_limit_high, Tournament.published_at, User.username).filter(
            Tournament.is_public == 1, Tournament.start_date >= datetime.now(), UsersTournaments.result == 'Host').order_by(Tournament.start_date).limit(5).all()
    return render_template('main/home.html', upcoming_tournaments=upcoming_tournaments, past_tournaments=past_tournaments)


@main.route('/steam_login')
@login_required
def steam_login():
    params = {
        'openid.ns': 'http://specs.openid.net/auth/2.0',
        'openid.identity': 'http://specs.openid.net/auth/2.0/identifier_select',
        'openid.claimed_id': 'http://specs.openid.net/auth/2.0/identifier_select',
        'openid.mode': 'checkid_setup',
        'openid.return_to': 'http://127.0.0.1:5000/authorize',
        'openid.realm': 'http://127.0.0.1:5000'
    }
    query_string = urlencode(params)
    auth_url = 'https://steamcommunity.com/openid/login?'+query_string
    return redirect(auth_url)


@main.route('/authorize')
@login_required
def authorize():
    response = json.dumps(request.args['openid.identity'])
    response_id = response.split('/')[-1].strip('"')
    db.session.query(User).filter(
        User.id == current_user.id).update({"steam_id": response_id})
    user = db.session.query(User).filter(User.id == current_user.id).first()
    participant_role = Role.query.filter(Role.name == 'Participant').first()
    user.roles.append(participant_role)
    db.session.commit()
    return redirect(url_for('main.home'))


@main.route('/admin_setup')
def admin_setup():
    user = db.session.query(User).filter(User.id == current_user.id).first()
    admin_role = Role.query.filter(Role.name == 'Admin').first()
    user.roles.append(admin_role)
    db.session.commit()
    return redirect(url_for('main.home'))


@main.route('/change_icon', methods=['POST', 'GET'])
def change_icon():
    if request.method == 'GET':
        return render_template('main/change_icon.html')
    elif request.method == 'POST':
        db.session.query(User).filter(
            User.id == current_user.id).update({"icon": request.form['icon_select']})
        db.session.commit()
    return redirect(url_for('main.home'))


@main.route('/profile/<int:id>')
def view_profile(id):
    if current_user.has_roles('Admin') and id == current_user.id:
        user_tournaments = db.session.query(Tournament).join(
            User.tournaments).filter(User.id == id).all()
        return render_template('admin/profile.html', user_tournaments=user_tournaments)
    else:
        user_tournaments = db.session.query(Tournament).join(User.tournaments).join(UsersTournaments, UsersTournaments.user_id == User.id).with_entities(Tournament.id,  Tournament.name, Tournament.start_date,
                                                                                                                                                         Tournament.end_date, Tournament.players_admited, Tournament.elo_limit_low, Tournament.elo_limit_high, UsersTournaments.result).filter(User.id == id).order_by(Tournament.start_date).all()
        user_data = db.session.query(User).filter(User.id == id).first()
        with urlopen(f"https://aoe2.net/api/leaderboard?game=aoe2de&leaderboard_id=3&start=1&count=1&steam_id={user_data.steam_id}") as response:
            source = response.read()
        data_1 = json.loads(source)
        with urlopen(f"https://aoe2.net/api/player/matches?game=aoe2de&count=5&steam_id={user_data.steam_id}") as response:
            source = response.read()
        data_2 = json.loads(source)
        return render_template('participant/profile.html', user_tournaments=user_tournaments, user_data=user_data, aoe_data=data_1['leaderboard'], matches_data=data_2)


@main.route('/create_tournament', methods=['POST', 'GET'])
@roles_required('Admin')
def new_tournament():
    form = NewTournament()
    if request.method == 'GET':
        return render_template('admin/new_tournament.html', form=form)
    elif request.method == 'POST' and form.validate_on_submit():
        if request.form['submit_button'] == 'Save & Publish':
            new_tournament = Tournament(name=form.name.data, password=form.password.data, players_admited=form.players_admited.data, discord_server_id=form.discord_server_id.data, elo_limit_low=form.elo_limit_low.data, elo_limit_high=form.elo_limit_high.data, start_date=datetime.combine(
                form.start_date.data, form.start_time.data), end_date=datetime.combine(form.end_date.data, form.end_time.data), created_at=datetime.now(), last_update=datetime.now(), is_public=1, published_at=datetime.now())
        else:
            new_tournament = Tournament(name=form.name.data, password=form.password.data, players_admited=form.players_admited.data, discord_server_id=form.discord_server_id.data, elo_limit_low=form.elo_limit_low.data, elo_limit_high=form.elo_limit_high.data, start_date=datetime.combine(
                form.start_date.data, form.start_time.data), end_date=datetime.combine(form.end_date.data, form.end_time.data), created_at=datetime.now(), last_update=datetime.now())
        db.session.add(new_tournament)
        number_rounds = 0
        if form.players_admited.data == '16':
            number_rounds = 4
        elif form.players_admited.data == '8':
            number_rounds = 3
        elif form.players_admited.data == '4':
            number_rounds = 2
        elif form.players_admited.data == '2':
            number_rounds = 1
        for n in range(0, number_rounds):
            new_round = Round(
                round_number=n+1, round_type=request.form[f'round_{n+1}'])
            new_tournament.rounds.append(new_round)
        for n in range(1, int(form.players_admited.data)):
            new_match = Match(match_number=n)
            new_tournament.matches.append(new_match)
        current_user.tournaments.append(new_tournament)
        db.session.commit()
        return redirect(url_for('main.view_profile', id=current_user.id))
    else:
        return render_template('admin/new_tournament.html', form=form)


@main.route('/edit_tournament/<int:id>', methods=['POST', 'GET'])
@roles_required('Admin')
def edit_tournament(id):
    form = NewTournament()
    if request.method == 'GET':
        return render_template('admin/new_tournament.html', form=form, id=id)
    elif request.method == 'POST' and form.validate_on_submit() and db.session.query(User.tournaments).join(UsersTournaments, UsersTournaments.user_id == User.id).filter(Tournament.id == id, User.id == current_user.id, UsersTournaments.result == 'Host'):
        db.session.query(Tournament).filter(Tournament.id == id).update({Tournament.name: form.name.data, Tournament.password: form.password.data, Tournament.players_admited: form.players_admited.data, Tournament.discord_server_id: form.discord_server_id.data, Tournament.elo_limit_low: form.elo_limit_low.data,
                                                                         Tournament.elo_limit_high: form.elo_limit_high.data, Tournament.start_date: datetime.combine(form.start_date.data, form.start_time.data), Tournament.end_date: datetime.combine(form.end_date.data, form.end_time.data), Tournament.last_update: datetime.now()})
        tournament_rounds = db.session.query(
            Round).join(Tournament.rounds).filter(Tournament.id == id).all()
        for idx, result in enumerate(tournament_rounds):
            db.session.query(Round).filter(
                Round.id == result.id).update({Round.round_type: request.form[f'round_{idx+1}']})
        if request.form['submit_button'] == 'Save & Publish' and not db.session.query(Tournament).filter(Tournament.id == id).with_entities(Tournament.is_public).first()[0]:
            db.session.query(Tournament).filter(
                Tournament.id == id).update({Tournament.is_public: 1, Tournament.published_at: datetime.now()})
        db.session.commit()
        return redirect(url_for('main.view_profile', id=current_user.id))
    else:
        return render_template('admin/new_tournament.html', form=form, id=id)


@main.route('/delete_tournament/<int:id>', methods=['POST', 'GET'])
@roles_required('Admin')
def delete_tournament(id):
    if db.session.query(User.tournaments).join(UsersTournaments, UsersTournaments.user_id == User.id).filter(Tournament.id == id, User.id == current_user.id, UsersTournaments.result == 'Host'):
        tournament = Tournament.query.filter_by(id=id).first()
        db.session.delete(tournament)
        db.session.commit()
    return redirect(url_for('main.view_profile', id=current_user.id))


@main.route('/tournament/<int:id>/get_info')
@roles_required('Admin')
def get_tournament_info(id):
    tournament = Tournament.query.filter_by(id=id).all()
    rounds_data = {}
    for data in tournament:
        tournament_data = {'name': data.name, 'password': data.password, 'players_admited': data.players_admited, 'elo_limit_high': data.elo_limit_high, 'elo_limit_low': data.elo_limit_low, 'start_date': data.start_date.strftime(
            '%Y-%m-%d'), 'start_time': data.start_date.strftime('%H:%M'), 'end_date': data.end_date.strftime('%Y-%m-%d'), 'end_time': data.end_date.strftime('%H:%M'), 'discord_server_id': data.discord_server_id}
        for d in data.rounds:
            rounds_data[f'round_{d.round_number}'] = d.round_type
        tournament_data['rounds'] = rounds_data
    return jsonify({'data': tournament_data})


@main.route('/tournament/<int:id>', methods=['POST', 'GET'])
@login_required
def view_tournament(id):
    form = JoinTournament()
    is_open = db.session.query(Tournament.is_open).filter(
        Tournament.id == id).first()[0]
    if db.session.query(Tournament).join(User.tournaments).filter(Tournament.id == id, User.id == current_user.id).first():
        enrolled = True
    else:
        enrolled = False
    tournament = db.session.query(
        Tournament).filter(Tournament.id == id).first()
    host = db.session.query(User.username).join(User.tournaments).join(UsersTournaments, UsersTournaments.user_id == User.id).filter(
        Tournament.id == id, UsersTournaments.result == 'Host').first()
    rounds = db.session.query(Round).join(Tournament.rounds).filter(
        Tournament.id == id).order_by(Round.round_number).all()
    matches = db.session.query(Match).join(
        Tournament.matches).filter(Tournament.id == id).order_by(Match.id).all()
    user_elo = 0
    if current_user.has_roles('Participant'):
        with urlopen(f"https://aoe2.net/api/leaderboard?game=aoe2de&leaderboard_id=3&start=1&count=1&steam_id={current_user.steam_id}") as response:
            source = response.read()
        aoe_data = json.loads(source)
        for data in aoe_data['leaderboard']:
            user_elo = data['rating']
    else:
        user_elo = 0
    if request.method == 'POST' and form.validate_on_submit():
        if form.password.data == db.session.query(Tournament.password).filter(Tournament.id == id).first()[0]:
            current_tournament = db.session.query(
                Tournament).filter(Tournament.id == id).first()
            matches = db.session.query(
                Match).join(Tournament.matches).filter(Tournament.id == id).order_by(Match.id).all()
            next_available = None
            for match in matches:
                if len(match.users) < 2:
                    next_available = match
                    break
            user_tournament = UsersTournaments(
                user_id=current_user.id, tournament_id=id, result='Pending Results')
            db.session.add(user_tournament)
            current_user.matches.append(next_available)
            db.session.commit()
            if db.session.query(Tournament.discord_server_id).filter(Tournament.id == id).first() != 0:
                user_agent = 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US; rv:1.9.0.7) Gecko/2009021910 Firefox/3.0.7'
                url = f"https://discordapp.com/api/guilds/{current_tournament.discord_server_id}/widget.json"
                headers = {'User-Agent': user_agent, }
                api_request = urllib.request.Request(
                    url, None, headers)
                response = urllib.request.urlopen(api_request)
                source = response.read()
                data = json.loads(source)
                return redirect(data['instant_invite'])
    return render_template('main/bracket.html', enrolled=enrolled, is_open=is_open, tournament=tournament, host=host, rounds=rounds, matches=matches, form=form, user_elo=user_elo)


@main.route('/tournament/<int:id>/bracket', methods=['POST', 'GET'])
@roles_required('Admin')
def edit_bracket(id):
    tournament = db.session.query(Tournament).filter(
        Tournament.id == id).first()
    participants = db.session.query(User).join(User.tournaments).join(UsersTournaments, UsersTournaments.user_id == User.id).filter(
        Tournament.id == id, UsersTournaments.result != "Host").all()
    rounds = db.session.query(Round).join(Tournament.rounds).filter(
        Tournament.id == id).order_by(Round.round_number).all()
    matches = db.session.query(Match).join(
        Tournament.matches).filter(Tournament.id == id).all()
    return render_template('admin/tournament_bracket.html', tournament=tournament, rounds=rounds, matches=matches, participants=participants)
