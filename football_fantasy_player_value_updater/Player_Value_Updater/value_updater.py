import bs4 as bs
import urllib.request
from bs4.element import SoupStrainer
import mysql.connector
from unidecode import unidecode
import requests
import json


teams = {
    "پرسپولیس":"پرسپولیس",
    "استقلال":"استقلال",
    "سپاهان":"سپاهان",
    "تراکتور":"تراکتور",
    "گلگهرسیرجان":"گل گهر",
    "فولادخوزستان":"فولاد",
    "پیکان":"پیکان",
    "مسرفسنجان":"مس رفسنجان",
    "پدیده":"پدیده",
    "صنعتنفتآبادان":"صنعت نفت",
    "آلومینیوماراک":"آلومینیوم اراک",
    "نساجی":"نساجی",
    "نفتمسجدسلیمان":"نفت مسجدسلیمان",
    "ذوبآهن":"ذوب آهن",
    "سایپا":"سایپا",
    "ماشینسازی":"ماشین سازی",
}


def db_updater(players_list):
    mydb = mysql.connector.connect(
        host="localhost",
        user="root",
        password="siavash0h",
        port='3306',
        database="football_fantasy_DB"
    )
    mycursor = mydb.cursor(buffered=True)
    shitty_data = {} 
    for pl in players_list:
        try:
            mycursor.execute("SELECT * FROM createteam_player WHERE fullname = '%s' AND team_name = '%s'" % (pl[0] ,teams[pl[2]]))
            if mycursor.rowcount == 1:
                sql = "UPDATE createteam_player SET value = %s WHERE fullname = '%s' AND team_name = '%s'" % (pl[1], pl[0], teams[pl[2]])
                mycursor.execute(sql)
                mydb.commit()
                print("# update : name : %s -- value : %s -- team : %s" %(pl[0], pl[1], pl[2]))
            else:
                shitty_data[len(shitty_data)] = pl # [pl[0].encode('utf-8'), pl[1], pl[2].encode('utf-8')]
                print("no player found or more than one player found \n", pl)
        except Exception as e:
            print(e)

    if len(shitty_data):
        # save to json file
        with open('unmerged_player.txt', 'w', encoding='utf-8') as f:
            for key, value in shitty_data.items():
                s = str(key) + " -- " + value[0] + " - " + str(value[1]) + " - " + value[2] + "\n"
                f.write(s)
            # json.dump({"unmerged_data":shitty_data.encode('utf-8')}, of)
            f.close()
    mycursor.close()
    mydb.close



def get_names_and_value():
    # get link of all teams saved in .urls.txt file
    links = open('./urls.txt').read().splitlines()
    # dict for team_name and player info
    players_list = []

    for link in links:
        # open the lint
        page = urllib.request.urlopen(link).read()
        if page:
            # get link html
            soup = bs.BeautifulSoup(page, 'lxml')
            # get the team name
            team_name = soup.find("div", {"class": "h1-con"}).text.replace("\n", "").replace(" ", "").replace('ي','ی')
            # get players profile link
            player_container = soup.find_all("div", {"class": "player-container"})
            # link list
            p_list = []
            # get links
            for player in player_container:
                a = player.find('a')
                if player.find('a', href=True):
                    p_list.append(player.find('a')['href'])

            for p_link in p_list:
                # l = p_link.encode("utf-8")
                # p = urllib.request.urlopen(l).read()
                p = requests.get(p_link)
                soup = bs.BeautifulSoup(p.content, 'lxml')
                v=soup.find("span", {"class": "p-r-5"})
                if v:
                    player_value = float(str(v.previousSibling).strip())
                    player_name = soup.find('div', {"class":"h1-con"}).text.replace("\n","").replace("\xad", "").replace('ي','ی')
                    player_name = player_name.replace('\u200c', ' ')
                    full_name = player_name.replace(' ', '')
                    players_list.append([full_name, player_value, team_name])
                    print(full_name, player_value, team_name)
    db_updater(players_list)
    

def main():
    get_names_and_value()


if __name__ == "__main__":
    main()