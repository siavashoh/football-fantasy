import json
import pytz
from datetime import datetime, timedelta

from django.http.response import JsonResponse
from django.contrib.auth.tokens import default_token_generator
from django.shortcuts import redirect, render
from django.contrib import messages

from createteam.models import League, Player, Team, Team_Player, User_Team_Change
from accounts.models import UserProfile, User_Team
from .models import League_Player_Change_Dates
from home.models import Log

def log(title, message, data, is_what):
    if is_what == "is_info":
        log = Log.objects.create(title=title, message=message, data=data, is_info=True)
    elif is_what == "is_warning":
        log = Log.objects.create(title=title, message=message, data=data, is_warning=True)
    elif is_what == "is_error":
        log = Log.objects.create(title=title, message=message, data=data, is_error=True)
    log.save()


def fetch_user_player(all_players, user_player_list):

    user_players = {'goalkeeper': [], 'defender': [],
                    'forward': [], 'attacker': []}

    for post in user_player_list:
        for i in range(len(user_player_list[post])):
            for p in all_players[post]:
                if user_player_list[post][i] == p['id']:
                    user_players[post].append(p)
    return user_players


def fetch_player(id):
    # * this function fetch all players in choosen league pass as param id

    # fetch league from db
    league = League.objects.get(pk=id)

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
                                             p_info.lastname, 'player_post': p.post, 'player_team': p_team_info.team_name, 'player_value': p_info.value,'selected': 0})
            if p.post == 'دفاع':
                players['defender'].append({'id': p_info.id, 'player_name': p_info.firstname +
                                           ' ' + p_info.lastname, 'player_post': p.post, 'player_team': p_team_info.team_name, 'player_value': p_info.value,'selected': 0})
            if p.post == 'هافبک':
                players['forward'].append({'id': p_info.id, 'player_name': p_info.firstname + ' ' +
                                          p_info.lastname, 'player_post': p.post, 'player_team': p_team_info.team_name, 'player_value': p_info.value,'selected': 0})
            if p.post == 'حمله':
                players['attacker'].append({'id': p_info.id, 'player_name': p_info.firstname +
                                           ' ' + p_info.lastname, 'player_post': p.post, 'player_team': p_team_info.team_name, 'player_value': p_info.value,'selected': 0})
    return players


# this function is fetch all players that user selected
def fetch_users_players(all_players, user_player_list):

    users_players = {'goalkeeper': [], 'defender': [],
                     'forward': [], 'attacker': []}

    for post in user_player_list:
        for i in range(len(user_player_list[post])):
            for p in all_players[post]:
                if user_player_list[post][i] == p['id']:
                    users_players[post].append(p)
    return users_players


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


def create_team(request, task, league_id, hash):
    if request.method == 'GET':
        # check if user not verified route to verificationemail page
        user_is_verified = UserProfile.objects.get(user_id=request.user.id)
        user_is_verified = user_is_verified.is_email_verified
        if not user_is_verified:
            return redirect('accounts:verificationemail')
        
        # chack if url hash is user hash or changed
        if not default_token_generator.check_token(request.user, hash):
            # if hashs not matched redirect to chooseleague page
            messages.info(request, 'لطفا لیگ را دوباره انتخاب کنید')
            return redirect("createteam:chooseleague", hello=0)
        elif task == 'create':            
            # check if user was created team in this league
            if User_Team.objects.filter(user_id=request.user.id, league_id=league_id):
                return redirect("home:home", league_id=league_id)
            
            # if league not ended
            now = datetime.utcnow().replace(tzinfo=pytz.UTC)
            # end = now + timedelta(days=2000)
            league = League.objects.get(id=league_id)
            if league.is_ended:
                messages.info(request, "لیگ به پایان رسیده است.")
                return redirect("createteam:chooseleague", hello='0')
            
            # if league end date not pass but league create team datetime are passed
            # ceateteam datetime not ended it means user allowed to createteam 
            # else return to chooseleague page with an alert
            if league.allow_to_create_team_date < now:
                return redirect('createteam:chooseleague', hello='1')
            

            # if everything are ok do things in below 

            # if hashs matched fetch all players in this league and pass it to tamplate
            players = fetch_player(id=league_id)
            
            # get leagues changes dates 
            exp = exp_date(league_id)

            # fetch league image
            league_image = league.league_big_image

            context = {'players_data': players,
                        'task': 'create',
                        'expire_date': exp['expire_date'],
                        'num_of_changes': exp['num_of_changes'],
                        'league_id': league_id,
                        'league_image': league_image,
                        'hash': hash,
                        'user_selected_all_players': '{"player":[]}',
                        'page': 'createteam'}
            return render(request, 'createteam/createteam.html', context)
        elif task == 'change':
            # if task is change its meaning we want to change our team if time is not expired
            # get leagues changes dates 
            exp = exp_date(league_id)
            if exp['num_of_changes']>0:
                # fetch all players in league
                all_players = fetch_player(id=league_id)

                # fetch user team in this league from db
                user_team = User_Team.objects.get(user=request.user.id, league=league_id)
                

                # make user team players readible for js
                users_players = fetch_user_player(all_players, json.loads(user_team.players))

                # get expire_date and num_of_change
                exp = exp_date(league_id)

                # get user team changes
                # and check if user has changes his 
                user_team_change = User_Team_Change.objects.filter(
                    user_id=request.user.id,
                    league_id=league_id,
                    number_of_changes_allowed= exp['num_of_changes'])
                num_of_changes = exp['num_of_changes']
                changed = False
                for u_t_c in user_team_change:
                    if exp['start_date']<u_t_c.date<exp['expire_date']:
                        num_of_changes=0
                        changed = True
                        break
                
                # fetch league image
                league_image = League.objects.get(id=league_id).league_big_image

                # context of html request 
                context = {'user_selected_all_players': users_players,
                        'players_data': all_players,
                        'league_id': league_id,
                        'league_image': league_image,
                        'hash': hash,
                        'expire_date': exp['expire_date'],
                        'num_of_changes': num_of_changes,
                        'team_is_changed': changed,
                        'page': 'createteam',
                        'task': 'change'}
                return render(request, 'createteam/createteam.html', context)
            else:
                # this means we shoulden be hear beacuse change datetime was expired
                # return to home page
                return redirect('home:home', league_id=league_id)
    elif request.method == 'POST':
        if task == 'create':
            # if request is post its mean user create his team and want to save and continue
            
            # if user push save button twice or more do not save others and route it to home page 
            if User_Team.objects.filter(user_id=request.user.id, league_id=league_id):
                return redirect("home:home", league_id=league_id)  

            # get selected_player json
            s_p = json.loads(request.body)
            # _selected_players = {'goalkeeper': s_p["goalkeeper"], 'defender': s_p["defender"], 'forward': s_p["forward"], 'attacker': s_p["attacker"]}
            selected_players = {'goalkeeper': [],
                                'defender': [], 'forward': [], 'attacker': []}

            selected_players_count = 0
            selected_players_value = 0
            for key, value in s_p.items():
                for i in range(len(value)):
                    selected_players[key].append(value[i]['id'])
                    selected_players_count += 1
                    selected_players_value += value[i]['player_value']
            
            # check if user want to select more than 15 players raise an error 
            if selected_players_count > 15:
                message = 'شما بیشتر از 15 بازیکن انتخاب کرده‌اید. لطفا دوباره انتخاب کنید'
                return JsonResponse({'status':'false','message':message}, status=500)
            elif selected_players_value > 100:
                message = 'کاربر گرامی حداکثر بودجه برای انتخاب بازیکن 100 میلیون تومان است و ارزش تیم شما بیشتر از این مقدار است. لطفا دوباره انتخاب کنید.'
                return JsonResponse({'status':'false','message':message}, status=500)
                    

            # get user id
            user_id = request.user.id

            # set default format JSON for user
            team_format = json.dumps(
                {'defender': 4, 'forward': 4, 'attacker': 2})

            # set default main player JSON for user
            main_players = {'goalkeeper': [], 'defender': [],
                            'forward': [], 'attacker': []}
            for key, value in selected_players.items():
                for i in range(len(value)-1):
                    main_players[key].append(value[i])


            # finali create user_team field
            try:
                # cnvert selected_players to json
                selected_players = json.dumps(selected_players)

                # convert main_player to json
                main_players = json.dumps(main_players)

                # create user_team model object
                user_team = User_Team.objects.create(
                    user_id=user_id, league_id=league_id, players=selected_players,
                    team_format=team_format, main_players=main_players)
                # create user_team_change object
                user_team_change = User_Team_Change.objects.create(user_id=user_id, league_id=league_id,
                    first_team=json.dumps({}), second_team=selected_players, date=datetime.now())
                
                # save user_team to db
                user_team.save()
                # save user_team_change to db
                user_team_change.save()

                # after create the user_team redirect it to home page
                return JsonResponse({'status':'true'}, status=200)
            except Exception as e:
                data = json.dumps({"user":request.user.id, "where":{"app": "createteam", "view":"createteam", "part":"post->create"}, "exception_message":str(e), "in_league":league_id})
                log("exception", "exception while creating team for user", data, "is_error")
                message = 'مشکلی در هنگام ساخت تیم به وجود آمده است. لطفا دوباره امتحان کنید.'
                return JsonResponse({'status':'false','message':message}, status=500)
        elif task == 'change':
            # if change_expire_date not expired its mean we have time to change our team
            # first we should get change_expire_date from change_date table
            # get leagues changes dates 

            exp = exp_date(league_id)

            # get user team changes
            # and check if user has changes his 
            user_team_change = User_Team_Change.objects.filter(
                user_id=request.user.id,
                league_id=league_id,
                number_of_changes_allowed= exp['num_of_changes'])
            num_of_changes = exp['num_of_changes']
            for u_t_c in user_team_change:
                if exp['start_date']<u_t_c.date<exp['expire_date']:
                    num_of_changes=0
                    break

            if exp['start_date'] < exp['now'] < exp['expire_date'] and num_of_changes!=0:
                try:
                    # fetch user selected team from user_team db
                    user_team = User_Team.objects.get(
                        league_id=league_id, user_id=request.user)
                    # parse user_team players json to get saved team in formation
                    old_selected_players = json.loads(user_team.players)
                    # get request body and parse it to get new team players
                    s_p = json.loads(request.body)
                    # initial selected players with empty lists
                    new_selected_players = {
                        'goalkeeper': [], 'defender': [], 'forward': [], 'attacker': []}
                    # get all players id
                    for key, value in s_p.items():
                        for i in range(len(value)):
                            new_selected_players[key].append(value[i]['id'])

                    # value that hold number of changes in new_selected_players
                    num_of_changes = exp['num_of_changes']
                    # now we should check if changes is not more than 5 player
                    for key,value in old_selected_players.items():
                        for player in value:
                            if player not in new_selected_players[key]:
                                num_of_changes -= 1

                    # fetch all players in league
                    all_players = fetch_player(id=league_id)

                    # make user team players readible for js
                    users_players = fetch_user_player(all_players, json.loads(user_team.players))
                    
                    # if num_of_changes more than 5 send a error message to createteam(change)
                    if num_of_changes < 0:
                        # and we respond to ajax request with 500 
                        message = 'کاربر گرامی شما بیشتر از %s بازیکن را تغییر داده‌اید!!' % exp['num_of_changes'] +"\n شما حد اکثر %s بازیکن میتوانید تغییر دهید" % exp['num_of_changes']
                        return JsonResponse({'status':'false','message':message}, status=500)
                    else:
                        # change old selected players to new in db
                        user_team.players = json.dumps(new_selected_players)
                        
                        # create new main player json
                        main_players = {'goalkeeper': [], 'defender': [],
                            'forward': [], 'attacker': []}
                        for key, value in new_selected_players.items():
                            for i in range(len(value)-1):
                                main_players[key].append(value[i])
                        
                        # change old main players to new in db
                        user_team.main_players = json.dumps(main_players)
                        # make is_changed to true its mean user changed his team
                        user_team.is_changed = True
                        # create new user team change object

                        # if user push save button twice or more do not save others and route it to home page 
                        if not User_Team_Change.objects.filter(user_id=request.user.id, league_id=league_id, first_team=json.dumps(old_selected_players), second_team=json.dumps(new_selected_players)):
                            user_team_change=User_Team_Change.objects.create(
                                user_id=request.user.id,
                                league_id=league_id, 
                                first_team=json.dumps(old_selected_players), 
                                second_team=json.dumps(new_selected_players), 
                                date=datetime.now(),
                                number_of_changes_allowed=exp['num_of_changes'])
                            # save user team changes 
                            user_team.save()
                        # after save the changes redirect to home
                        return JsonResponse({'status':'true'}, status=200)
                except Exception as e:
                    data = json.dumps({ "user":request.user.id, "where":{"app": "createteam","view":"createteam", "part":"post->change"}, "exception_message":str(e), "in_league": league_id})
                    log("exception", "exception while changing team for user", data, "is_error")
                    message = 'مشکلی در هنگام ویرایش تیم به وجود آمده است. لطفا دوباره امتحان کنید.'
                    return JsonResponse({'status':'false','message':message}, status=500)
            else:
                return redirect("home:home", league_id=league_id)


def choose_league(request, hello):
    try:
        # check if user not verified route to verificationemail page 
        user_is_verified = UserProfile.objects.get(user_id=request.user.id).is_email_verified
        print(user_is_verified)
        if not user_is_verified:
            return redirect('accounts:verificationemail')
        
        now = datetime.utcnow().replace(tzinfo=pytz.UTC)
        end = now + timedelta(days=2000)
        leaques = League.objects.filter(end_date__range=[now, end], is_ended=False)
        token = default_token_generator.make_token(request.user)
        return render(request, 'createteam/chooseleague.html', {'leagues': leaques, 'hash': token, 'msg': hello})
    except Exception as e:
        data = json.dumps({ "user":request.user.id, "where":{"app": "createteam", "view":"chooseleague", "part":"first part"}, "exception_message":str(e),})
        log("exception", "exception while choosing league", data, "is_error")
        return render(request, 'createteam/chooseleague.html', {'leagues': leaques, 'hash': token, 'msg': hello})
