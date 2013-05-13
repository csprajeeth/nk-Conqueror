import market
import activity
import travel
from diet import *
from gamedata import *
from gameurls import *
from bs4 import BeautifulSoup
import sys
import thread

def L0to1(char, home):

    #TUTORIAL
    if char.level == 0:
        if market.get_cost(char, "flour") == 0: 
            market.buy(char, "flour", block=False) #buy that free flour
        char.visit(tutorial_url) #visit mentor to get free stuff

    #EAT in 1-2-1 fashion
    myhunger = 0
    if char.health < 6:
        myhunger = char.hunger
    elif char.health == 6 and char.hunger > 1:
        myhunger = 1
    diet = MinCostDiet(char, hunger = myhunger)
    diet.eat()

    #WORK
    if char.level == 1:
        dst = travel.get_next_hop(char, "itzohcan")
        if dst == None:
            thread.exit()
        else:
            activity.travel(char, dst)

    elif char.money > 90 and char.reputation < 5:
        if activity.work_at_church(char):
            char.visit(donate_to_church_url)
    elif activity.work_in_mine(char, duration=1) or activity.apply_for_job(char) or activity.apply_for_imw(char, duration=1):
       pass
    

    #LEVEL UP
    if char.reputation >=5 and char.money > 120 and char.level == 0:
        br = char.visit(town_url)
        soup = BeautifulSoup(br.response().read())
        level_up_url = townhall_url if soup.title.text.find("ville") != -1 else province_url
        br = char.visit(level_up_url)
        for form in br.forms():
            if form.action.find("action=16") != -1:
                if level_up_url == province_url:
                    form["usage"] = [str(2),]
                else:
                    form["usage"] = str(2)
                br.form = form
                br.submit()
                break
            


def itzo_mining(char, home):

    #EAT
    myhunger = 0
    if char.health < 6:
        myhunger = char.hunger
    elif char.health == 6 and char.hunger > 1:
        myhunger = 1
    diet = MinCostDiet(char, hunger = myhunger)
    diet.eat()

  #WORK
    activity.work_in_mine(char, duration=1)
            
    if char.money > 550:
        char.post(donate_to_town_url, urllib.urlencode({'somme':'500'}))

