import os
import json
import datetime
import csv
import time
from datetime import datetime
from time import gmtime, strftime
import glob,xlwt
import openpyxl
import smtplib # Import smtplib for the actual sending function
from email.mime.text import MIMEText # Import the email modules we'll need
from openpyxl import Workbook
try:
    from urllib.request import urlopen, Request
except ImportError:
    from urllib2 import urlopen, Request

# mettre a jour le format date pour ne garder que xx:xx:xx
# integrer un buffer de calcul derive pour detecter les grosses variations
# charger un graphique js en localhost pour chaque iteration avec deux echelles (prix, tendance)

# 1 Telecharger les dernières crypto de crypto compare.
# 2 Pour Les crypto ayant des marketcap compris entre 5M et 10M
# 3 Toutes les 8h
# Donner les valeurs de variation de volume
# Variation de nombre de post per_hour reddit a propos de la coin




# input date formatted as YYYY-MM-DD
since_date = ""
until_date = ""

_prevTime = 0
_count = 0
_prevPoints = 0


favorites_crypto = ["BTC","ETH","EOS","RDN","IOT","MOD"]


# download the last data.csv at this url:https://www.cryptocompare.com/api/data/coinlist/

print strftime("%Y-%m-%d %H:%M:%S", gmtime())
# open once the csv
print "Load the data.csv file..."
f = open("data.csv", "r")
csvDatalines = f.read().split("\r") # "\r\n" if needed
if csvDatalines != '' :
    print("data.csv loaded correctly")
    #print formated_time


def send_email(user, pwd, recipient, subject, body):
    import smtplib

    gmail_user = user
    gmail_pwd = pwd
    FROM = user
    TO = recipient if type(recipient) is list else [recipient]
    SUBJECT = subject
    TEXT = body

    # Prepare actual message
    message = """From: %s\nTo: %s\nSubject: %s\n\n%s
    """ % (FROM, ", ".join(TO), SUBJECT, TEXT)
    try:
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.ehlo()
        server.starttls()
        server.login(gmail_user, gmail_pwd)
        server.sendmail(FROM, TO, message)
        server.close()
        print 'successfully sent the mail'
    except:
        print "failed to send mail"


#Group all the csv files into one xls.
def xlsmaker():
    wb = xlwt.Workbook()
    for filename in glob.glob("*.csv"):
        (f_path, f_name) = os.path.split(filename)
        (f_short_name, f_extension) = os.path.splitext(f_name)
        ws = wb.add_sheet(f_short_name)
        spamReader = csv.reader(open(filename, 'rb'))
        for rowx, row in enumerate(spamReader):
            for colx, value in enumerate(row):
                ws.write(rowx, colx, value)
    print("saving workbook")
    wb.save('output.xls')


# send mail if the value goes to high
#def detect_affluence(val):
    #if val > 3:
        #send_mail()


#request verification
def request_until_succeed(url):
    req = Request(url)
    success = False
    while success is False:
        try:
            response = urlopen(req)
            if response.getcode() == 200:
                success = True
        except Exception as e:
            print(e)
            time.sleep(5)

            print("Error for URL {}: {}".format(url, datetime.now()))
            print("Retrying.")

    return response.read()


# Needed to write tricky unicode correctly to csv
def unicode_decode(text):
    try:
        return text.encode('utf-8').decode()
    except UnicodeDecodeError:
        return text.encode('utf-8')


def to_integer(dt_time):
    return 10000*dt_time.year + 100*dt_time.month + dt_time.day + dt_time.hour + dt_time.minute + dt_time.second

def set_prevTime(x):
    global _prevTime    # Needed to modify global copy of globvar
    _prevTime = x

def set_prevPoints(x):
    global _prevPoints
    _prevPoints = x

def set_prevCounts(count):
    global _count
    _count = count

def get_deltaTime():
    return time.time() - _prevTime

#Collect in a 2x2 table informations from data.csv
#and retrieve their id
def getId(CoinName):

    for line in csvDatalines:
        if line != "": # add other needed checks to skip titles
            cols = line.split(";")
            if cols[0] == CoinName:
			    #print (cols)
			    return cols[1]

def get_coef(x):
    Points = 'X' if 'Points' not in x['Data']['General'] else \
        x['Data']['General']['Points']

    prevPoints = _prevPoints
    nextPoints = Points

    try:
        coef = float( (nextPoints - prevPoints) / get_deltaTime() )
    except ZeroDivisionError:
        coef = 0

    #print _count

    #print time.time() - prevTime
    return coef


#getting all the parameters for each coin
def getQuicklyParams(x):
    #print (x)
    CoinName = unicode_decode(x['Data']['General']['CoinName'])

    Points = 'X' if 'Points' not in x['Data']['General'] else \
        x['Data']['General']['Points']

    #time = datetime.datetime.now()
    time = strftime("%Y-%m-%d %H:%M:%S", gmtime())
    set_prevPoints(Points)
    set_prevCounts(_count+1)

    return (CoinName,Points,get_coef(x),get_deltaTime(),time )



# Scrap crypto coin depending on those which are
# placed in the global variable "favorites_crypto"
def quickScrapeCryptoPageFeedStatus(favorites_crypto):
	# Pour 1000 prises par jour durant 20h, intervale de 72s
	# 500 fichiers de 56ko = taille 26Mo a stocker chaque jour
    # 1000 coin = 1000 * 6ko
	# /!\ endomagement precoce du disque dur

    set_prevCounts(0)

    # INITIALISATION
    for crypto in favorites_crypto:
        print (crypto)
        print (getId(crypto))

        if crypto != "": # add other needed checks to skip titles

            coin_name = crypto

            with open('{}.csv'.format(coin_name), 'wb') as file:
                w = csv.writer(file)
                w.writerow(["CoinName","Points","Time"])

                has_next_page = True
                num_processed = 0
                scrape_starttime = datetime.now()
                after = ''

    print("File creation with title columns is done !")


    # SCRAPING LOOP
    while True:

        scrape_starttime = datetime.now()
        for crypto in favorites_crypto:

            if crypto != "": # add other needed checks to skip titles

                coin_name = crypto

                #creating url
                base = "https://www.cryptocompare.com/api/data/socialstats/?id="
                node = "{}".format(getId(coin_name))
                base_url = base + node
                print("Scraping:{} with id:{} with: {}".format(coin_name, node, scrape_starttime))

                with open('{}.csv'.format(coin_name), 'ab') as file:
                    w = csv.writer(file)

                    after = '' if after is '' else "&after={}".format(after)

                    # geting json file
                    # converting into csv file
                    # writing the row
                    statuses = json.loads(request_until_succeed(base_url))

                    status_data = getQuicklyParams(statuses)
                    #set_prevTime(int(time.mktime(datetime.now().timetuple())))
                    #set_prevTime(int (strftime("%Y%m%d%H%M%S.%f", gmtime() ) ) )
                    set_prevTime(time.time())

                    w.writerow(status_data)

                    after = ''

        print("all the csv got new values, time to restart the loop")


        print("Done!{} Statuses Processed in {}".format(
              num_processed, datetime.now() - scrape_starttime))





#############
# METHODE 2 #
#############
#getting all the parameters for each coin
def getParams(x):
    #print (x)
    CoinName = unicode_decode(x['Data']['General']['CoinName'])

    Points = 'X' if 'Points' not in x['Data']['General'] else \
        x['Data']['General']['Points']
    CryptoComparePageViews = 'X' if 'PageViews' not in x['Data']['CryptoCompare'] else \
        x['Data']['CryptoCompare']['PageViews']
    TwitterFollowers = 'X' if 'followers' not in x['Data']['Twitter'] else \
        x['Data']['Twitter']['followers']
    TwitterStatuses = 'X' if 'statuses' not in x['Data']['Twitter'] else \
        x['Data']['Twitter']['statuses']
    RedditSubscribers = 'X' if 'subscribers' not in x['Data']['Reddit'] else \
        x['Data']['Reddit']['subscribers']
    RedditCommentPerDay = 'X' if 'comments_per_day' not in x['Data']['Reddit'] else \
        x['Data']['Reddit']['comments_per_day']
    FacebookLikes = 'X' if 'likes' not in x['Data']['Facebook'] else \
        x['Data']['Facebook']['likes']
    FacebookTalkingAbout = 'X' if 'talking_about' not in x['Data']['Facebook'] else \
        x['Data']['Facebook']['talking_about']

    #time = datetime.datetime.now()
    time = strftime("%Y-%m-%d %H:%M:%S", gmtime())

    return (CoinName,Points,CryptoComparePageViews,TwitterFollowers,RedditSubscribers,RedditCommentPerDay,FacebookLikes,FacebookTalkingAbout,time)

# Succesively scrap crypto coin depending on the
# number the user want
def scrapeCryptoPageFeedStatus(number_of_crypto):
	# Pour 1000 prises par jour durant 20h, intervale de 72s
	# 500 fichiers de 56ko = taille 26Mo a stocker chaque jour
    # 1000 coin = 1000 * 6ko
	# /!\ endomagement precoce du disque ssd


    # INITIALISATION
    num_crypto = 0
    for crypto in csvDatalines:
        if num_crypto < number_of_crypto:
            if crypto != "": # add other needed checks to skip titles
                cols = crypto.split(";")
                num_crypto=num_crypto+1
                coin_name = cols[0]
                print str(coin_name)

                with open('{}.csv'.format(coin_name), 'wb') as file:
                    w = csv.writer(file)
                    w.writerow(["CoinName","Points","Crypto_Compare_PageViews",
                                "Twitter_Followers","Reddit_Subscribers","Reddit_CommentPerDay",
                                "Facebook_Likes","Facebook_Talking_About","Time"])

                    has_next_page = True
                    num_processed = 0
                    scrape_starttime = datetime.now()
                    after = ''

        else:
            print("File creation with title columns is done !")
            break


    # SCRAPING LOOP
    while True:
        num_crypto = 0
        scrape_starttime = datetime.now()
        for crypto in csvDatalines:
            if num_crypto < number_of_crypto:
                if crypto != "": # add other needed checks to skip titles
                    cols = crypto.split(";")
                    coin_name = cols[0]

                    #creating url
                    base = "https://www.cryptocompare.com/api/data/socialstats/?id="
                    node = "{}".format(getId(coin_name))
                    base_url = base + node
                    print("Scraping:{} with id:{} with: {}".format(coin_name, node, scrape_starttime))

                    with open('{}.csv'.format(coin_name), 'ab') as file:
                        w = csv.writer(file)

                        after = '' if after is '' else "&after={}".format(after)

                        # geting json file
                        # converting into csv file
                        # writing the row
                        statuses = json.loads(request_until_succeed(base_url))
                        status_data = getParams(statuses)
                        w.writerow(status_data)

                        num_crypto = num_crypto + 1
                        after = ''
            else:
                print("all the csv got new values, time to restart the loop")
                break

        print("Done!{} Statuses Processed in {}".format(
              num_processed, datetime.now() - scrape_starttime))





if __name__ == '__main__':
    #param = nombre de crypto a traiter
    #scrapeCryptoPageFeedStatus(15)
    quickScrapeCryptoPageFeedStatus(favorites_crypto)

    #creation du fichier xls avec tous les csv
    #xlsmaker()
