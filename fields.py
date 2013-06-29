import re
import time
import sys
import market
import gameplay
import urllib
import townhall

from gamedata import *
from gameurls import *
from bs4 import BeautifulSoup
from init import log




def get_field_object(char, number):
    """
    Constructs the appropriate field/ranch object
    by checking the character's land usage.
    Arguments:
    - `char`: The character object
    - `number`: 1 or 2 - indicating the 1st or the 2nd land
    """

    if char.level == 0:
        return None

    page = char.visit(myhome_url).read()
    s1 = "textePage["+str(number+1)+"]['Texte'] = '"
    s2 = "';"
    start = page.find(s1) + len(s1)
    end = page.find(s2, start)
    text = page[start:end]

    if "Action.php?action=17" in text: #we don't have the land
        return None

    m = re.search("(champ)(\d+)(.*gif)", text, re.IGNORECASE)
    if m != None: #Its a field
        field_code = int(m.group(2))
        if field_code == 0: #No field. (Needs reset)
            return Land(char, number)
        if field_code == 1:
            return Wheat(char, number)
        if field_code == 2:
            return Corn(char, number)
        if field_code == 5:
            print "PIGS RANCH!!"
            return None
        if field_code == 6:
            return Vegetable(char, number)
        if field_code == 7:
            return Agave(char, number)

    return None
        


class Land(object):
    """
    
    """
    
    def __init__(self, char, number):
        self.char = char
        self.number = number
        
    def sell(text = "", price = 500.0):
        """
        Puts the land on sale.
        """
        pass

    def cancel_sale(self, ):
        """
        Cancels the sale.
        """
        pass


    def reset(self, field):
        """
        Resets the usage of the current land
        to supplied argument (field).
        """
        field_code = field_map[field]
        self.char.visit(game_url + "Action.php?action=12&champ="+str(self.number-1), urllib.urlencode({"reinit":"Reset", "usage":"0"}))
        self.char.visit(game_url + "Action.php?action=12&champ="+str(self.number-1), urllib.urlencode({"usage":str(field_code)}))
        



class Field(Land):
    """
    """
    
    def __init__(self, char, number):
        """
        """
        super(Field, self).__init__(char, number)


        self.day = None
        self.quality = None
        self.hiring = None
        self.harvesting = None
        self.refresh()


    def refresh(self):
        """
        Refreshes all the attributes.
        TEST - self.harvesting when we are harvesting are own field
        """

        page = self.char.visit(myhome_url).read()
        s1 = "textePage["+str(self.number+1)+"]['Texte'] = '"
        s2 = "';"
        start = page.find(s1) + len(s1)
        end = page.find(s2, start)
        text = page[start:end]


        m = re.search("(\d+)(\s*/\s*)(\d+)", text)
        self.day = int(m.group(1))

        m = re.search("(Quality\s*:\s*)(\d+)%", text, re.IGNORECASE)
        self.quality = int(m.group(2))

        m = re.search("your\s*job\s*offer", text, re.IGNORECASE)
        self.hiring = True if m != None else False

        self.harvesting = True if "FichePersonnage.php?login=" in text else False

        if self.hiring and self.harvesting:
            self.char.logger.write(log() + " Interesting...we are hiring and also harvesting at the same time....ERROR\n")
            self.type = None 
        



    def hire(self, stat=None, wage=None, autobuy=True):
        """
        Posts an advertisement at the townhall/calpulli.
        """
        if self.can_hire():
            if not self.prep_home_inventory(autobuy):
                self.char.logger.write(log() + " Don't have the necessary materials for hiring worker..QUIT HIRING\n")
                return False

            page = self.char.visit(myhome_url).read()
            s1 = "textePage["+str(self.number+1)+"]['Texte'] = '"
            s2 = "';"
            start = page.find(s1) + len(s1)
            end = page.find(s2, start)
            text = page[start:end]        
            soup = BeautifulSoup(text)
            
            carac =  soup.find("input", attrs={"name": "carac"})['value']
            actionChamp = soup.find("input", attrs={"name": "actionChamp"})['value']
            embauche = soup.find("input", attrs={"name": "embauche"})['value']

            wage = self.wage_recommender() if (type(wage) is not int or not 12<=wage<=50) else wage
            stat = self.stat_recommender() if (type(stat) is not int or not 0<=stat<=19) else stat

            if wage > int(self.char.money):
                self.char.logger.write(log() + " Don't have enough money to hire...QUIT HIRING\n")
                return False 


            url = game_url + "Action.php?action=18&champ=" + str(self.number-1) 
            self.char.visit(url, urllib.urlencode({'actionChamp':str(actionChamp), 'carac':str(carac),
                                              'embauche':str(embauche), 'salaire':str(wage),
                                              'qualification':str(stat)}))
            self.char.logger.write(log() + " Posted a job for hiring a worker to work on field " + str(self.number) + "\n")







class Corn(Field):
    """
    This class represents a corn field.
    """
    def __init__(self, char, number):
        self.type = r_field_map[2]
        super(Corn, self).__init__(char, number)        
        
    def can_hire(self,):
        """
        States whether someone can be hired to work on your
        field.
        """
        self.refresh()
        return (self.day == 1 or self.day == 7) and not self.hiring and not self.harvesting

    def prep_home_inventory(self, autobuy=True):
        """
        Prepares the home inventory        
        """
        self.char.update_inventory()
        self.char.home.update_inventory()
        if self.day == 1:
            if self.char.home.inventory[52] == 0 and self.char.inventory[52] == 0 and autobuy:
                market.buy(self.char, "corn")
            if self.char.home.inventory[52] == 0 and self.char.inventory[52]:
                self.char.transfer_to_home(52)
            if self.char.home.inventory[52]:
                return True
            return False
        return True
        
    def wage_recommender(self,):
        """
        Recommends a wage.
        """
        return 19

    def stat_recommender(self,):
        """
        Recommends a stat value for hiring
        """
        return 19

    def manage(self, stat=None, wage=None, autobuy=True):
        self.char.home.transfer_to_char(52, quantity=-1)
        self.hire(stat, wage, autobuy)



class Wheat(Field):
    """
    This class represents a wheat field.
    """
    
    def __init__(self, char, number):
        self.type = r_field_map[1]
        super(Wheat, self).__init__(char, number)        

    def can_hire(self,):
        """
        States whether someone can be hired to work on your
        field.
        """
        self.refresh()
        return (self.day == 1 or self.day == 2 or self.day == 10) and not self.hiring and not self.harvesting

    def prep_home_inventory(self, autobuy=True):
        """
        Prepares the home inventory        
        """
        self.char.update_inventory()
        self.char.home.update_inventory()
        if self.day == 2:
            if self.char.home.inventory[56] == 0 and self.char.inventory[56] == 0 and autobuy:
                market.buy(self.char, "wheat")
            if self.char.home.inventory[56] == 0 and self.char.inventory[56]:
                self.char.transfer_to_home(56)
            if self.char.home.inventory[56]:
                return True
            return False
        return True

    def wage_recommender(self,):
        """
        Recommends a wage.
        """
        return 19

    def stat_recommender(self,):
        """
        Recommends a stat value for hiring
        """
        return 19

    def manage(self, stat=None, wage=None, autobuy=True):
        self.char.home.transfer_to_char(56, quantity=-1)
        self.hire(stat, wage, autobuy)



class Vegetable(Field):
    """
    This classs represents a vegetable field.
    """
    
    def __init__(self, char, number):
        self.type = r_field_map[6]
        super(Vegetable, self).__init__(char, number)        

    def can_hire(self,):
        """
        States whether someone can be hired to work on your
        field.
        """
        self.refresh()
        return (self.day == 5) and not self.hiring and not self.harvesting

    def prep_home_inventory(self, autobuy=True):
        """
        Prepares the home inventory        
        """
        return True

    def wage_recommender(self, ):
        """
        Recommends a wage.
        """
        return 17

    def stat_recommender(self, ):
        """
        Recommends a stat value for hiring
        """
        return 0

    def manage(self, stat=None, wage=None, autobuy=True):
        self.char.home.transfer_to_char(64, quantity=-1)
        self.hire(stat, wage, autobuy)



class Agave(Field):
    """
    This class represents an agave field.
    """
    
    def __init__(self, char, number):
        self.type = "agave"
        super(Agave, self).__init__(char, number)
        
    def can_hire(self,):
        self.refresh()
        return (self.day in [1,4,5,6]) and not self.harvesting and not self.hiring
        

    def prep_home_inventroy(self, autobuy=True):
        return True

    def wage_recommender(self, ):
        return 19

    def stat_recommender(self, ):
        return 19

    def manage(self, stat=None, wage=None, autobuy=True):
        #self.char.home.transfer_to_char(64, quantity=-1)
        self.hire(stat, wage, autobuy)



class Hibiscus(Field):
    """
    This class represents a Hibiscus field.
    """
    
    def __init__(self, char, number):
        self.type = hibiscus
        super(Hibiscus, self).__init__(char, number)
        
    def can_hire(self):
        self.refresh()
        return (self.day in [5]) and not self.harvesting  and not self.hiring

    def prep_inventory(self):
        return True

    def recommend_wage(self):
        return 19

    def recommend_stat(self):
        return 19

    def manage(self, stat=None, wage=None, autobuy=True):
        self.hire(stat, wage, autobuy)
        

        


class Ranch(Land):
    """
    """

    class Animal(object):
        """
        This class represents the animals of a ranch
        Attributes shared by all ranch animals:
        1. Age (in days)
        2. Health (yield depends on this)
        3. Hungry (True/False)
        """

        def __init__(self, ):
            self.age = None
            self.health = None #(0-8) -- (Dying-American Style)
            self.hungry = None

    

    def __init__(self, char, number):

        super(Ranch, self).__init__(char, number)
        self.quality = None
        self.hiring = None
        self.slaughtering = None
        self.animals = [Animal()] * 4
        self.refresh()


    def refresh(self,):
        """
        Refreshes the attributes of the ranch.
        """
        
