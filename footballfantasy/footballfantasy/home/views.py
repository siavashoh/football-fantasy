import json
from django.contrib import messages
import pytz
import jdatetime
from datetime import datetime, timedelta


from django.http import request
from django.shortcuts import render, redirect
from django.http.response import JsonResponse
from django.contrib.auth.tokens import default_token_generator

from createteam.models import League_Player_Change_Dates
from accounts.models import User_Team
from createteam.models import Player, Team, Team_Player, League,User_Team_Change
from home.models import Log


def log(title, message, data, is_what):
    if is_what == "is_info":
        log = Log.objects.create(title=title, message=message, data=data, is_info=True)
    elif is_what == "is_warning":
        log = Log.objects.create(title=title, message=message, data=data, is_warning=True)
    elif is_what == "is_error":
        log = Log.objects.create(title=title, message=message, data=data, is_error=True)
    log.save()


def fetch_all_player(league_id):
    # * this function fetch all players in choosen league pass as param id

    # fetch league from db
    league = League.objects.get(pk=league_id)

    # fetch all teams in this league
    teams = Team.objects.filter(league=league)

    # initiate players dic
    players = {'goalkeeper': [], 'defender': [], 'forward': [], 'attacker': []}

    for team in teams:
        # fetch all players in every team
        _players = Team_Player.objects.filter(team=team)

        for p in _players:
            # fetch player info
            p_info = Player.objects.get(pk=p.player_id)

            # fetch team info for team_name
            p_team_info = Team.objects.get(pk=p.team_id)

            # chech players posts and put theme in _players by post seperated
            if p.post == 'دروازبان':
                players['goalkeeper'].append({'id': p_info.id, 'player_name': p_info.firstname + ' ' +
                                             p_info.lastname, 'player_post': p.post, 'player_team': p_team_info.team_name, 'player_score': p_info.score, 'player_value': p_info.value, 'selected': 0})
            if p.post == 'دفاع':
                players['defender'].append({'id': p_info.id, 'player_name': p_info.firstname +
                                           ' ' + p_info.lastname, 'player_post': p.post, 'player_team': p_team_info.team_name, 'player_score': p_info.score, 'player_value': p_info.value, 'selected': 0})
            if p.post == 'هافبک':
                players['forward'].append({'id': p_info.id, 'player_name': p_info.firstname + ' ' +
                                          p_info.lastname, 'player_post': p.post, 'player_team': p_team_info.team_name, 'player_score': p_info.score, 'player_value': p_info.value, 'selected': 0})
            if p.post == 'حمله':
                players['attacker'].append({'id': p_info.id, 'player_name': p_info.firstname +
                                           ' ' + p_info.lastname, 'player_post': p.post, 'player_team': p_team_info.team_name, 'player_score': p_info.score, 'player_value': p_info.value, 'selected': 0})
    return players


def fetch_user_player(all_players, user_player_list):

    user_players = {'goalkeeper': [], 'defender': [],
                    'forward': [], 'attacker': []}
    user_value = float(0)
    for post in user_player_list:
        for i in range(len(user_player_list[post])):
            for p in all_players[post]:
                if user_player_list[post][i] == p['id']:
                    user_players[post].append(p)
                    user_value += p['player_value']
    return [user_players, round(user_value, 2)]


# this function is return now datetime league 
def exp_date(league_id):
    change_dates = League_Player_Change_Dates.objects.get(league_id=league_id)
    # get now datetime utc time zoon
    now = datetime.utcnow().replace(tzinfo=pytz.UTC)  
    # var holled change expire date
    expire_date = 0
    # start date of changes
    start_date = 0
    # number of changes user allows to change
    num_of_changes = 0
    # set expire_date and num_of_changes
    if change_dates.start_ch_15 < now < change_dates.end_ch_15:
        # this means user allows to change 15 players
        expire_date = change_dates.end_ch_15
        start_date = change_dates.start_ch_15
        num_of_changes = 15
    elif change_dates.start_ch_5 < now < change_dates.end_ch_5:
        # this means user allows to change 5 players
        expire_date = change_dates.end_ch_5
        start_date = change_dates.start_ch_5
        num_of_changes = 5
    else:
        # this means no changes is allowed
        expire_date = now - timedelta(days=1)
        start_date = now - timedelta(days=1)
        num_of_changes = 0
    return {'expire_date':expire_date, 'start_date':start_date,'num_of_changes':num_of_changes, 'now':now}


def date_convertor(date):
    jd = jdatetime.date.fromgregorian(day=date.day, month=date.month, year=date.year)
    return jd


def home(request, league_id):
    if not User_Team.objects.filter(league_id=league_id, user_id=request.user.id).exists():
        return redirect("createteam:chooseleague", hello=0)
    now = datetime.utcnow().replace(tzinfo=pytz.UTC)
    end = now + timedelta(days=2000)
    if not League.objects.filter(id=league_id, end_date__range=[now, end], is_ended=False).exists():
        messages.info(request, 'لیگ وجود ندارد یا به پایان رسیده است.')
        return redirect("createteam:chooseleague", hello=0)
    if request.method == 'GET':
        try:
            # get users team in choosen league
            user_team = User_Team.objects.get(
                user=request.user.id, league=league_id)
            # user score 
            user_score = user_team.user_score

            # fetch al players in league
            league_players = fetch_all_player(league_id)

            # convert user players id json to list of players
            user_player = fetch_user_player(league_players, json.loads(user_team.players))
            user_selected_all_players = user_player[0]
            user_team_value = user_player[1]

            # convert user main player id json to list  of players
            user_selected_main_players = fetch_user_player(league_players, json.loads(user_team.main_players))[0]

            # create user token
            token = default_token_generator.make_token(request.user)

            # get expire_date and num_of_change
            exp = exp_date(league_id)

            # get user team changes
            # and check if user has changes his team in this time
            user_team_change = User_Team_Change.objects.filter(
                user_id=request.user.id,
                league_id=league_id,
                number_of_changes_allowed= exp['num_of_changes'])
            num_of_changes = exp['num_of_changes']
            changed = False
            if user_team_change:
                for u_t_c in user_team_change:
                    if exp['start_date']< u_t_c.date and u_t_c.date < exp['expire_date']:
                        num_of_changes=0
                        changed = True
                        break

            # fetch league image and league expire date 
            league = League.objects.get(id=league_id)
            # image
            league_image = league.league_big_image
            league_reward_image = league.league_reward
            # description
            league_description = league.description
            # league next date for change team format
            league_next_change_format_date = date_convertor(league.next_change_format_date)
            # expire date
            league_end_date = league.end_date
            # check if change format date is passed and allow_to_change_foramt is true
            if league.allow_to_change_format_date < now:
                league_allow_to_change_format = False
            else:
                # user allow to change his format or not
                league_allow_to_change_format = True 
            # team format change date
            team_format_date = league.allow_to_change_format_date
            

            # fetch league change dates (15 and 5 players)
            change_dates = League_Player_Change_Dates.objects.get(league_id=league_id)
            league_start_ch_15 = date_convertor(change_dates.start_ch_15)
            league_end_ch_15 = date_convertor(change_dates.end_ch_15)
            league_start_ch_5 = date_convertor(change_dates.start_ch_5)
            league_end_ch_5 = date_convertor(change_dates.end_ch_5)
            

            # context to pass to template
            context = {
                'user_selected_all_players': user_selected_all_players,
                'user_selected_main_players': user_selected_main_players,
                'user_score':user_score,
                'players_data': league_players,
                'league_id': league_id,
                'league_image': league_image,
                'league_reward_image': league_reward_image,
                'league_start_ch_15': league_start_ch_15,
                'league_end_ch_15': league_end_ch_15,
                'league_start_ch_5': league_start_ch_5,
                'league_end_ch_5': league_end_ch_5,
                'league_description': league_description,
                'league_end_date': date_convertor(league_end_date),
                'league_allowed_to_change_format': league_allow_to_change_format,
                'league_next_change_format_date': league_next_change_format_date,
                'user_team_value': user_team_value,
                'hash': token,
                'expire_date' : exp['expire_date'],
                'team_format_date': team_format_date,
                'num_of_changes':num_of_changes,
                'team_is_changed':changed,
                'page': 'home'
            }

            return render(request, "home/home.html", context)
        except Exception as e:
            data = json.dumps({ "user":request.user.id, "where":{"app": "home","view":"home", "part":"get"}, "exception_message":str(e), "in_league": league_id})
            log("exception", "exception while fetching data in home", data, "is_error")
            return redirect("createteam:chooseleague", hello=0)
    elif request.method == "POST":
        """ if request is post its mean user change his team format 
            and player that he picked in createteam part and want to
            save and continue.

            in this part first we check if changes are allow in league or 
            user want to do archness
        """
        # check if changes team format are allow in league
        league = League.objects.get(id=league_id)
        if league.allow_to_create_team_date < now:
            message = 'شما مجاز به تغییر ترکیب و بازیکن نیستید. تاریخ ترکیب '
            return JsonResponse({'status':'false','message':message}, status=500)

        try :
            # get selected_player json
            s_p = json.loads(request.body)
            _selected_players = {'goalkeeper': s_p["goalkeeper"], 'defender': s_p["defender"], 'forward': s_p["forward"], 'attacker': s_p["attacker"]}
            main_players = {'goalkeeper': [], 'defender': [], 'forward': [], 'attacker': []}
            for key,value in s_p.items():
                for i in range(len(value)):
                    main_players[key].append(value[i]['id'])
            
            # get user id
            user_id = request.user.id

            # set default format JSON for user
            team_format = json.dumps({'defender': len(main_players['defender']), 'forward': len(main_players['forward']), 'attacker': len(main_players['attacker'])})

            # update user_team field
            user_team = User_Team.objects.get(league_id=league_id, user_id= user_id)
            user_team.main_players=json.dumps(main_players)
            user_team.team_format=team_format
            user_team.save()

            data = json.dumps({ "user":request.user.id, "where":{"app": "home","view":"home", "part":"post"}, "exception_message":"no exp", "in_league": league_id})
            log("success", "format successfully saved", data, "is_info")
            return JsonResponse({'status':'true'}, status=200)
        except Exception as e:
            data = json.dumps({ "user":request.user.id, "where":{"app": "home","view":"home", "part":"get"}, "exception_message":str(e), "in_league": league_id})
            log("exception", "exception while fetching data in home", data, "is_error")
            message = 'در هنگام ذخیره ترکیب مشکل پیش آمده است، لطفا دوباره امتحان کنید.'
            return JsonResponse({'status':'false','message':message}, status=500)
