import bs4 as bs
import urllib.request
import mysql.connector
from unidecode import unidecode


def db_updater(dict_of_players, league_id):
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
            for p in list_of_players:
                mycursor.execute("SELECT * FROM createteam_player WHERE firstname = '%s' AND lastname='%s' AND team_name = '%s'" % (p[0][0], p[0][1],team_name))
                if mycursor.rowcount == 1:
                    # fetch palyer_id from player table
                    player_id = mycursor.fetchone()[0]
                    # update player score in player table 
                    update_score_sql = "UPDATE createteam_player SET score = %s WHERE firstname = '%s' AND lastname = '%s' AND team_name = '%s'" % (p[1], p[0][0], p[0][1], team_name)
                    mycursor.execute(update_score_sql)
                    mydb.commit()
                    
                    insert_new_score_sql = "INSERT INTO createteam_league_player_score (player_id, league_id, score) VALUES (%s, %s, %s)" % (player_id, league_id, p[1])
                    mycursor.execute(insert_new_score_sql)
                    mydb.commit()
                    print("# update : %s -- %s -- %s -- %s" %(p[0][0], p[0][1], p[1], team_name))
                else:
                    print("no player found or more than one player found \n", mycursor.fetchall()) 
        except Exception as e:
            print(e)
    mycursor.close()
    mydb.close


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
            players_score_dict = []
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
                            print(firstname, lastname)
                            player_name = [firstname, lastname]
                        else:
                            player_name = list(filter(None, name_and_post[0].split(' ')))
                        player_fullname = ''.join(player_name).replace(' ', '')
                        player_score = unidecode(tr.find('td', {'class': 'score'}).text.replace(",", "."))
                        # if  ther is '-' char or Negative number replace it wiht zero
                        if '-' in player_score:
                            player_score ='0'                        
                        # add player info to list
                        players_score_dict.append([player_name, float(player_score), player_fullname])
                        print("%s -- %s" % (player_name, str(player_score), player_fullname))
                    except Exception as e:
                        print(e)
                        return
            # add info list to dict
            dict_of_players[team_name] = players_score_dict

    print(dict_of_players)
    # pass players dict to db_updater to update scores of players
    db_updater(dict_of_players, 10)
    

def main():
    get_names_and_scores()


if __name__ == "__main__":
    main()