import mysql.connector
import bs4 as bs
import urllib.request

def db_updater(dict_of_players):
    mydb = mysql.connector.connect(
        host="localhost",
        user="root",
        password="siavash0h",
        port='3306',
        database="football_fantasy_DB"
    )
    mycursor = mydb.cursor(buffered=True)
    for team_name, list_of_players in dict_of_players.items():
        try:
            # insert team to team table if not exist
            mycursor.execute("SELECT * FROM createteam_team WHERE team_name = '%s'" % (team_name))
            if mycursor.rowcount == 0:
                try:
                    sql = "INSERT INTO createteam_team (team_name, team_fullname) VALUES ('%s', '%s')" % (team_name, team_name.replace(' ', ''))
                    mycursor.execute(sql)
                    mydb.commit()
                    print("# add to team        -->    ",team_name)
                except Exception as e:
                    print("error in inserting team : \n", e)
            else:
                print(mycursor.fetchall())
            
            for p in list_of_players:
                # check if player not exist
                mycursor.execute("SELECT * FROM createteam_player WHERE firstname ='%s' AND lastname ='%s' AND fullname = '%s' AND team_name = '%s'" % (p[0][0], p[0][1], p[2], team_name))
                if mycursor.rowcount == 0:
                    try:
                        # insert player to player table if not exist
                        mycursor.execute("INSERT INTO createteam_player (firstname, lastname, score, value, team_name, fullname) VALUES ('%s', '%s', 0, 0,'%s', '%s')" % (p[0][0],p[0][1],team_name, p[2]))
                        mydb.commit()
                        print("# add to player      -->  %s,  %s, %s" % (p[0][0], p[0][1], p[2]))
                    except Exception as e:
                        print("error in inserting player : \n", e)
                else:
                    print('this player exist -> : %s,  %s, %s' % (p[0][0], p[0][1], p[2]))
                
                # insert player id and team id and post to team_player table
                # select team id
                mycursor.execute("SELECT id FROM createteam_team WHERE team_name='%s'" % team_name)
                team_id = mycursor.fetchall()[0][0]

                # select player id
                mycursor.execute("SELECT id FROM createteam_player WHERE firstname='%s' AND lastname='%s' AND team_name='%s' AND fullname='%s'" % (p[0][0],p[0][1], team_name, p[2]))
                
                if mycursor.rowcount == 1:
                    player_id = mycursor.fetchall()[0][0]
                    # check if player not exist
                    mycursor.execute("SELECT * FROM createteam_team_player WHERE player_id ='%s' AND team_id ='%s' AND post = '%s'" % (player_id, team_id, p[1]))
                    if mycursor.rowcount == 0:
                        try:
                            sql = "INSERT INTO createteam_team_player (player_id, team_id, post) VALUES ('%s', '%s', '%s')" % (player_id, team_id, p[1])
                            mycursor.execute(sql)
                            mydb.commit()
                            print("# add to team_player -->  %s  ,  %s  ,  %s  " % (player_id, team_name, p[1]))
                        except Exception as e:
                            print("error in inserting team_player : \n", e)
                    else:
                        print('this player exist in team_player -> : %s,  %s, %s' % (p[0][0], p[0][1], p[2]))
                else:
                    print("insert duplicate to team_player table --> player_ids : %s   ---  team_name = %s" % (mycursor.fetchall(), team_name))
        except Exception as e:
            print(e)
    mycursor.close()
    mydb.close()


def get_player_name(player_link):
    # open player profile link
    player = urllib.request.urlopen('https://www.metrica.ir/'+player_link).read()
    # get and return player name
    soup = bs.BeautifulSoup(player, 'lxml')
    _posts = {'دروازبان':'دروازبان', 'مدافع':'دفاع', 'مهاجم':'حمله', 'هافبک':'هافبک'}
    name = soup.find('div', {'class': 'name'}).text
    post = soup.find('div', {'class': 'description mt-3 d-block'}).text
    for key, value in _posts.items():
        if key in post:
            post = value
            break
    return [name, post]


def get_names_and_scores():
    # get link of all teams saved in .urls.txt file
    links = open('./urls.txt').read().splitlines()
    # dict for team_name and player info
    dict_of_players = {}

    for link in links:
        # open the lint
        page = urllib.request.urlopen(link).read()
        if page:
            # get link html
            soup = bs.BeautifulSoup(page, 'lxml')
            # get the team name
            team_name = ' '.join(list(filter(None, soup.find('div', {'class': 'name'}).text.split(" "))))
            # this gets players
            players = soup.find("div", {"id": "yw8"})
            # this gets goalkeepers
            goalkeeper = soup.find("div", {"id": "yw6"})
            # get table body of players
            tbp = players.find("tbody")
            # get table body of goalkeepers
            tbg = goalkeeper.find('tbody')
            # get table rows of palyers
            trp = tbp.find_all("tr")
            # get table rows of goalkeepers
            trg = tbg.find_all("tr")
            # this list is keep players and goalkeepers names and scores
            players_score_list = []
            for tb in [trp, trg]:
                for tr in tb:
                    try:
                        # get link to player profile to get full name
                        a = tr.find('a').attrs['href']
                        # pass this link to get_player_name func to fetch full name
                        name_and_post = get_player_name(a)
                        player_name = []
                        if '\u200c' in name_and_post[0]:
                            name_and_post[0] = name_and_post[0].replace('\u200c', ' ')
                            pp = list(filter(None, name_and_post[0].split(' ')))

                            firstname = pp[0].replace(' ', '')
                            pp.pop(0)
                            lastname = ' '.join(pp)
                            player_name = [firstname, lastname]
                        else:
                            player_name = list(filter(None, name_and_post[0].split(' ')))
                        post = name_and_post[1]
                        # add player info to list
                        player_fullname = ''.join(player_name).replace(' ', '')
                        players_score_list.append([player_name, post, player_fullname])
                        print(player_name , player_fullname, post)
                    except Exception as e:
                        print(e)
            # add info list to dict
            dict_of_players[team_name] = players_score_list
    print(dict_of_players)
    # pass players dict to db_updater to update scores of players
    db_updater(dict_of_players)
    


def main():
    get_names_and_scores()


if __name__ == "__main__":
    main()
