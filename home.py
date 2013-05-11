from bs4 import BeautifulSoup
from gameurls import *
from gamedata import item_map

import urllib
import mechanize
import re

class Home():
    """ 
    Represent the character's home.
    Has an inventory and an attribute representing money
    ~ Need to add support for fields
    """
    
    def __init__(self, username, password, br, opener, login_data, logger):
        """
        """
        
        self.poster = opener
        self.login_data = login_data
        self.br = br
        self.username = username
        self.password = password
        self.logger = logger

        self.inventory = [0] * 390
        self.money = None
        self.update_inventory()


    def logout(self):
        """
        Arguments:
        - `self`:
        """
        self.br.open(game_url+"Deconnexion.php")


    def login(self):
        self.br.open(game_url)
        self.br.select_form(nr=0)
        self.br['login'] = self.username
        self.br['password'] = self.password
        self.br.submit()


    def update_inventory(self):
        """
        Builds an inventory which is in the form of a dictionary where keys are item names
        and values are the number of them
        
        Internals:
        The game keeps the inventory info within a javascript so we must extract it first and then
        give it to BeautifulSoup for parsing.
        """

        self.logout()
        self.login()

        s1 = "textePage[1]['Texte'] = '"
        s2 = "textePage[2] = new"

        br = self.br
        br.open(myhome_url)
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



    def transfer_to_char(self, item, quantity=1):
        """Transfers an item or money from the character's home
        to the character
        
        Arguments:
        - `br`:
        - `poster`:
        - `login_data`:
        - `item`:
        - `quantity`:
        """

        self.update_inventory()
        if item not in item_map: 
            raise ValueError("Item not in db")
        item_code = item_map[item]

        if  (item_code and self.inventory[item_code] < quantity) or (~item_code and self.money < quantity):
            raise ValueError("Item not available in sufficient quantity")

        if quantity == -1:
            quantity = self.inventory[item_code] if item_code else self.money

        poster = self.poster
        login_data = self.login_data

        poster.open(loginform_url, login_data)
        poster.open(myhome_url)
        transfer_url = game_url + "Action.php?action=69&c=1&type=" + str(item_code)+ "&IDParametre=0"

        if item_code == 0: #if its money we are transfering
            self.money -= quantity
            post =  urllib.urlencode({'destination':'transfererPropriete', 'submit':'OK', 'quantite':'100'})
            while quantity > 100:
                poster.open(transfer_url, post)
                quantity-=100

        poster.open(transfer_url, urllib.urlencode({'destination':'transfererPropriete', 'submit':'OK', 
                                                    'quantite':str(quantity) }))
        if item_code:
            self.inventory[item_code] -= quantity
