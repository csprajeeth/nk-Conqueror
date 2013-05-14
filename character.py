from gameurls import *
from bs4 import BeautifulSoup
from gamedata import *
from datetime import datetime
from init import log

import urllib
import re
import time
import random
import traceback
import sys
import urllib2

class Character():
    """
    Represent the character and his various attributes
    """
    
    def __init__(self, name, password, br, logger):
        """
        """
        self.br = br
        self.name = name
        self.password = password
        self.logger = logger

        self.hunger = None
        self.health = None
        self.money = None
        self.activity = None
        self.activity_remaining = None

        self.inventory = [0] * 390
        
        self.level = None
        self.strength = None
        self.intelligence = None
        self.charisma = None
        self.reputation = None
        self.mood = None

        self.login()
        self.refresh()


    def get_browser(self):
        """Returns the browser object related to the character
        """
        return self.br



    def get_login_data(self):
        """Returns the login data related to the character
        
        Arguments:
        - `self`:
        """
        return self.login_data



    def login(self):

        while self.is_server_under_maint():
            time.sleep(60)

        logged_in = False
        while logged_in == False:
            try:
                self.br.open(game_url, timeout=35)
                self.br.select_form(nr=0)
                self.br['login'] = self.name
                self.br['password'] = self.password
                self.br.submit()
                if self.br.geturl() == game_url+"?o=6":
                    char.logger.write(log() + "Wrong password")
                    sys.exit()
                elif self.br.geturl() == game_url: #server under maint?
                    time.sleep(60)
                else:
                    logged_in = True
            except:
                self.logger.write(log())
                traceback.print_exc(file = self.logger)


    def visit(self, url, mydata=None):
        """
        A new interface to open any of the game urls
        This method takes care of network issues,
        server maintainance and makes sure that the url
        is visited.

        Arguments:
        - `url`: The url to open
        - `mydata`: The post data
        Returns:
        The browser after we visit that url
        """
        if self.is_server_under_maint():
            self.login()

        loaded = False
        while loaded == False:
            try:
                self.br.open(url, data=mydata, timeout=35)
                loaded = True
            except:
                self.logger.write(log())
                traceback.print_exc(file = self.logger)
                time.sleep(5)
        return self.br



    def logout(self):
        """
        Arguments:
        - `self`:
        """
        self.visit(game_url+"Deconnexion.php")




    def is_working(self):
        """
        Arguments:
        - `self`:
        """
        self.update_characteristics()
        return self.activity != 'none'


    def get_current_time(self):
        """
        Return the current game time (GMT)
        Arguments:
        - `self`:
        """
        return time.gmtime()



    def is_server_under_maint(self):
        """
        Server maintainance interval : 8:59:00 - 9:20:00
        """
        t1 = self.get_current_time()
        if (t1[3] == 8 and t1[4] == 59) or (t1[3] == 9 and t1[4] < 20):
            return True
        else:
            return False


    def sleep_till_next_event(self):
        """
        Makes the character sleep till next event i.e. job complete
        Arguments:
        - `self`:
        """

        self.logout()
        sleep_time = (self.activity_remaining + 2) * 60
        self.logger.write(log() + " sleeping for " + str(sleep_time) + " sec" + '\n')
        time.sleep(sleep_time)
        self.logger.write(log() + " woke up...refreshing" + '\n')
        self.login()
        self.refresh()


    def get_time_till_reset(self):
        """
        Returns the number of seconds left
        till the next reset
        """
        s1 = "9:20:00" #reset time in GMT
        t1 = self.get_current_time()
        s2 = str(t1[3]) + ":" + str(t1[4]) + ":" + str(t1[5])
        diff = datetime.strptime(s1,'%H:%M:%S') - datetime.strptime(s2,'%H:%M:%S')
        return diff.seconds


    def update_characteristics(self):
        """
        Updates the basic status info of the character
        - `health`: 0-dead, 1-dying, 2-bony, 3-skinny, 4-weak, 5-exhausted, 6-fit
        - `hunger`: How many hunger points you can eat
        - `activity`: The activity you are performing
        - `activity_remaining`: minutes remaining for the activity. -1 if not applicable
        """

        br = self.visit(town_url)
        soup = BeautifulSoup(br.response().read())

        temp2 = soup.find('div', {'class' : 'zone_caracteristiques'}).findAll('div', {'class' : 'caracteristique01 caracteristique03'})#for health and hunger information
        temp1 = soup.find('div', {'class' : 'caracteristique01 caracteristiqueActivite'}) #for activity information

        self.activity = temp1.find('div', {'class' : 'elementActivite'}).get_text().strip()
        self.activity = re.sub('Activity:', '', self.activity).strip().lower()

        self.health = healthTable[temp2[0].get_text().strip()]
        self.hunger = hungerTable[temp2[1].get_text().strip()]

        if self.activity != 'none' and self.activity != 'traveling':
            self.activity_remaining = temp1.find('div', {'class' : 'tempsRestant'}).get_text().strip()
            m = re.search('\d+:\d+', self.activity_remaining)
            arr =  m.group(0).split(':')
            self.activity_remaining = int(arr[0])*60 + int(arr[1])
        elif self.activity == 'none':
            self.activity_remaining = 0
        else: #Traveling
            self.activity_remaining = self.get_time_till_reset()


    def update_inventory(self):
        """
        Builds an inventory which is in the form of an count array.
        
        Internals:
        The game keeps the inventory info within a javascript so we must extract it first and then
        give it to BeautifulSoup for parsing.
        """
        
        self.logout()
        self.login()
        
        self.inventory = [0] * 390
        s1 = "textePage[1]['Texte'] = '"
        s2 = "textePage[2] = new"

        br = self.visit(my_url)
        page = br.response().read()

        start = page.find(s1)
        end = page.find(s2)
        end = page.rfind("'",start,end)
        start+=len(s1)
        soup = BeautifulSoup(page[start:end])

        self.money = soup.find('div', {'id' : 'Item10'}).text
        m = re.search('\d+.\d+', self.money)
        self.money = float(re.sub(",",".",m.group(0)))

        no_of_items = soup.find_all('div', {'class' : 'inventaire_contenu_01_nbre'})
        item_description = soup.find_all( 'div', {'class' : 'inventaire_contenu_01_descriptif'})

        for i in range(1,len(no_of_items)):
            item_code = item_map[item_description[i+1].text.lower()]
            self.inventory[item_code] = int(no_of_items[i].text)
            


    def update_stats(self):
        """
        Updates the str, int, charisma, rep and mood
        of the character.
        """


        br = self.visit(my_url)
        page = br.response().read()
        soup = BeautifulSoup(page)
        rows = soup.find_all('tr', {'class' : 'tr_perso'})

        arr = rows[0].td.text.split(" ")
        self.level = int(arr[1])

        self.mood = rows[1].td.text
        stats = dict()
        for i in range(3, 7):
            tds = rows[i].find_all('td')
            stats[tds[1].text.lower()] = int(tds[2].text)
            
        self.strength = stats["strength"]
        self.intelligence = stats["intelligence"]
        self.charisma = stats["charisma"]
        self.reputation = stats["reputation points"]

    

    def refresh(self):
        self.update_characteristics()
        self.update_inventory()
        self.update_stats()



    def use(self, item, times=1):
        """
        Uses an item in the inventory 
        Arguments:
        - `br`: Browser
        - `item`: Name of the item to use
        - `times`: number of times to use. -1 to use all
        """

        self.update_inventory()
        
        if item not in item_map:
            raise ValueError("Item not in db")
        if self.inventory[item_map[item]] < times:
            raise ValueError("Item not available in sufficient quantity")
        if times == -1:
            times = self.inventory[item_map[item]]


        url = game_url + "Action.php?action=6&type=" + str(item_map[item]) + "&IDParametre=0"
        while times > 0:
            #print url #for debug
            self.logger.write(log() + " Using item: " + item + "\n")
            self.br.open(url)
            times-=1
        self.refresh()

        



    def sell(self, item, price, quantity=1):
        """
        Sells an item in the inventory on the market
        Arguments:
        - `self`:
        - `br`: 
        - `item`: 
        - `price`: 
        - `quantity`:
        """
        if item not in item_map:
            raise ValueError("Item not in db")

        self.update_inventory()
        if self.inventory[item_map[item]] < quantity:
            raise ValueError("Item not available in sufficient quantity")
        if quantity == -1:
            quantity = self.inventory[item_map[item]]

        integer = int(price)
        change = int(round(price*100,1))%100

        if change % 10 not in [0,5]:
            raise ValueError("Invalid price. Change must be a multiple of 5")

        sale_url = game_url+"Action.php?action=10&type=" + str(item_map[item]) + "&IDParametre=0"
        self.br.open(sale_url, urllib.urlencode({'centimes':str(change), 'submit':'OK', 'prix':str(integer), 
                                                'quantite':str(quantity), 'destination':'vendreMarche' }))
        self.inventory[item_map[item]] -= quantity



    def transfer_to_home(self, item, quantity=1):
        """Transfers a specified item to the character's home
        Arguments:
        - `self`:
        - `item`:
        - `quantity`:
        """

        if item not in item_map: 
            raise ValueError("Item not in db")
        item_code = item_map[item]
        quantity = int(quantity)

        self.update_inventory()
        if  (item_code and self.inventory[item_code] < quantity) or (~item_code and self.money < quantity):
            raise ValueError("Item not available in sufficient quantity")

        if quantity == -1:
            quantity = self.inventory[item_code] if item_code else self.money


        transfer_url = game_url + "Action.php?action=69&type=" + str(item_code)+ "&IDParametre=0"
        if item_code == 0: #if its money we are transfering
            self.money -= quantity
            post =  urllib.urlencode({'destination':'transfererPropriete', 'submit':'OK', 'quantite':'100'})
            while quantity > 100:
                self.br.open(transfer_url, post)
                quantity-=100

        self.br.open(transfer_url, urllib.urlencode({'destination':'transfererPropriete', 'submit':'OK', 
                                                    'quantite':str(quantity) }))
        if item_code:
            self.inventory[item_code] -= quantity
