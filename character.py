from gameurls import *
from bs4 import BeautifulSoup
from gamedata import *
from datetime import datetime
from home import Home
from init import log

import urllib
import re
import time
import traceback
import sys
import urllib2
import thread

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
        self.load = None
        self.maxload = None

        self.level = None
        self.strength = None
        self.intelligence = None
        self.charisma = None
        self.reputation = None
        self.mood = None
        self.tools = {66:False, 67:False, 71:False, 73:False, 105:False, 106:False}

        self.login()
        self.home = Home(self)
        self.refresh()




    def get_browser(self):
        """Returns the browser object related to the character
        """
        return self.br



    def login(self):

        while self.is_server_under_maint():
            time.sleep(60)

        logged_in = False
        while logged_in == False:
            try:
                response = self.br.open(loginform_url, data=urllib.urlencode({'login':self.name, 'password':self.password}), timeout=35)
                if response.geturl() == game_url+"?o=6":
                    self.logger.write(log() + "Wrong password\n")
                    thread.exit()
                elif response.geturl() == game_url: #server under maint?
                    self.logger.write(log() + "Server maybe under maintainance\n")
                    time.sleep(60)
                else:
                    logged_in = True

            except SystemExit ,e:
                thread.exit()
            except:
                self.logger.write(log())
                time.sleep(15)
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
        The response after we visit that url
        """
        if self.is_server_under_maint():
            self.login()

        loaded = False
        while loaded == False:
            try:
                response = self.br.open(url, data=mydata, timeout=35)
                loaded = True
            except:
                self.logger.write(log() + " -ERROR OPENING URL: " + url + "\n")
                traceback.print_exc(file = self.logger)
                time.sleep(15)
        return response



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
        return self.activity != game_strings.activity['none']



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




    def get_seconds_till_reset(self):
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
        Updates the basic status info of the character. Also resurrects the character
        if it is dead.
        - `health`: 0-dead, 1-dying, 2-bony, 3-skinny, 4-weak, 5-exhausted, 6-fit
        - `hunger`: How many hunger points you can eat
        - `activity`: The activity you are performing
        - `activity_remaining`: minutes remaining for the activity. -1 if not applicable
        """

        page = self.visit(my_url).read()
        s1 = "textePage[0]['Texte'] = '"
        start = page.find(s1) + len(s1)
        end = page.find("';", start)
        soup = BeautifulSoup(page[start:end])
        tags = soup.find_all('li')

        self.hunger = hungerTable[re.sub(game_strings.scrape['hunger'], '', tags[1].text.lower().strip())]
        self.health = healthTable[re.sub(game_strings.scrape['health'], '', tags[2].text.lower().strip())]

        if self.health == 0: #you are dead
            self.visit(game_url+"Action.php?action=36") #Resurrect 
            return self.update_characteristics() #do everything again

        soup = BeautifulSoup(page)
        self.activity = soup.find('div', {'class':'elementActivite'}).text.lower().strip()
        self.activity = re.sub(game_strings.scrape['activity'], '', self.activity)

        if self.activity != game_strings.activity['none'] and self.activity != game_strings.activity['travel']:
            self.activity_remaining = soup.find('div', {'class' : 'tempsRestant'}).text.strip()
            m = re.search('\d+:\d+', self.activity_remaining)
            arr =  m.group(0).split(':')
            self.activity_remaining = int(arr[0])*60 + int(arr[1])
        elif self.activity == game_strings.activity['none']:
            self.activity_remaining = 0
        else: #Traveling
            self.activity_remaining = int(self.get_seconds_till_reset()/60)



    def update_inventory(self):
        """
        Builds an inventory which is in the form of an count array.
        """
        
        s1 = "textePage[1]['Texte'] = '"
        s2 = "textePage[2] = new"

        page = self.visit(my_url).read()

        start = page.find(s1)
        end = page.find(s2)
        end = page.rfind("'",start,end)
        start+=len(s1)
        soup = BeautifulSoup(page[start:end])

        m = re.search("(\d+)(\s*/\s*)(\d+)", soup.text)
        self.load = int(m.group(1))
        self.maxload = int(m.group(3))

        self.inventory = [0] * 390
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
        Updates the level, str, int, charisma, rep and mood
        of the character.
        """

        response = self.visit(my_url)
        page = response.read()
        soup = BeautifulSoup(page)
        rows = soup.find_all('tr', {'class' : 'tr_perso'})

        arr = rows[0].td.text.split(" ")
        self.level = 99 if 'Vagrant' in arr[1] else int(arr[1]) 

        self.mood = rows[1].td.text
        stats = dict()
        for i in range(3, 7):
            tds = rows[i].find_all('td')
            stats[tds[1].text.lower()] = int(tds[2].text)
            
        self.strength = stats[game_strings.stats['str']]
        self.intelligence = stats[game_strings.stats['int']]
        self.charisma = stats[game_strings.stats['charisma']]
        self.reputation = stats[game_strings.stats['rep']]


        
    def update_tools_and_wardrobe(self):
        """
        Updates the wardrobe and tools that the character
        uses.
        Arguments:
        - `self`:
        """
        for key in self.tools.keys():
            self.tools[key] = False

        page = self.visit(my_url).read()
        s1 = "textePage[0]['Texte'] = '"
        start = page.find(s1) + len(s1)
        end = page.find("';", start)
        text = page[start:end]
        
        if "action=55&type=Barque" in text: #canoe
            self.tools[71] = True        
        if "action=55&type=Echelle" in text: #ladder
            if "small ladder" in text:
                self.tools[66] = True
            else:
                self.tools[67] = True
        if "action=154&r=1" in text: #axe
            self.tools[73] = True
        if "action=154&r=1&t=1" in text: #shield
            self.tools[106] = True



    def refresh(self):
        self.update_characteristics()
        self.update_inventory()
        self.update_stats()
        self.update_tools_and_wardrobe()



    def equip(self, item):
        """
        Equips a weapon. These items can be unquipped.
        Arguments:
        - `self`: 
        - `item`: The weapon to be equipped
        """
        
        name = item
        self.update_inventory()
        if type(item) is str:
            if item not in item_map:
                char.logger.write(log() + " Item not in db - " + str(item) + "\n")
                return None
            item = item_map[item]
        if self.inventory[item]:
            self.visit(game_url + "Action.php?action=154&o=" + str(item))
            self.logger.write(log() + " Equipped: " + str(name) + "\n")
        else:
            self.logger.write(log() + " Unable to equip item: " + str(name) + " - not in inventory\n")
        self.update_tools_and_wardrobe()



    def use(self, item, times=1):
        """
        Uses an item in the inventory 
        Arguments:
        - `br`: Browser
        - `item`: Name of the item to use
        - `times`: number of times to use. -1 to use all
        """
        name = item
        self.update_inventory()
        if type(item) is str:
            if item not in item_map:
                char.logger.write(log() + " Item not in db - " + str(item) + "\n")
                return None
            item = item_map[item]

        if self.inventory[item] < times:
            char.logger.write(log() + " Item not available in sufficient quantity. item: " + str(item) + " quantity: " + str(quantity) + "\n")
            return None
            
        if times == -1:
            times = self.inventory[item]


        url = game_url + "Action.php?action=6&type=" + str(item) + "&IDParametre=0"
        while times > 0:
            #print url #for debug
            self.logger.write(log() + " Using item: " + str(name) + "\n")
            self.br.open(url, timeout=35)
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
            raise ValueError("Item not in db - " + str(item))

        self.update_inventory()
        if self.inventory[item_map[item]] < quantity:
            raise ValueError("Item not available in sufficient quantity. item: " + str(item) + " quantity: " + str(quantity))
        if quantity == -1:
            quantity = self.inventory[item_map[item]]

        integer = int(price)
        change = int(round(price*100,1))%100

        if change % 10 not in [0,5]:
            raise ValueError("Invalid price. Change must be a multiple of 5 " + str(price))

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

        if type(item) is str:
            if item not in item_map: 
                raise ValueError("Item not in db - " + str(item))
            item = item_map[item]

        self.update_inventory()
        if  (item and self.inventory[item] < quantity) or (~item and self.money < quantity):
            raise ValueError("Item not available in sufficient quantity. item: " + str(item) + " quantity: " + str(quantity))

        if quantity == -1:
            quantity = self.inventory[item] if item else self.money

        transfer_url = game_url + "Action.php?action=69&type=" + str(item)+ "&IDParametre=0"
        if item == 0: #if its money we are transfering
            self.money -= quantity
            post =  urllib.urlencode({'destination':'transfererPropriete', 'submit':'OK', 'quantite':'100'})
            while quantity > 100:
                self.br.open(transfer_url, post)
                quantity-=100

        self.br.open(transfer_url, urllib.urlencode({'destination':'transfererPropriete', 'submit':'OK', 
                                                    'quantite':str(quantity) }))
        self.update_inventory()
        self.home.update_inventory()



    def level_up_1(self, field=None):
        """
        Levels up the character to level 1
        Arguments:
        - `self`:
        - `field`: The field you want. None if you want to be a vagrant
        """

        soup = BeautifulSoup(self.visit(town_url).read())
        level_up_url  = town_url if "ville" in soup.title.text.lower() else province_url
        page = char.visit(level_up_url).read()
        if type(field) is str:
            field = field_map[field]
        if "?action=16" in page:
            if field == None:
                char.visit(game_url+"Action.php?action=16", urllib.urlencode({'niveau':'1', 'passage':'become a vagrant', 'usage':'99'}))
            else:
                char.visit(game_url+"Action.php?action=16", urllib.urlencode({'niveau':'1', 'passage':'Level up 1', 'usage':str(field)}))

