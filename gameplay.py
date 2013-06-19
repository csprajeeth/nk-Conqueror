import urllib


import market
import activity
import travel

from diet import *
from gamedata import *
from gameurls import *
from bs4 import BeautifulSoup


def L0to1(char, field):

    #TUTORIAL
    if char.level == 0:
        if market.get_cost(char, "flour") == 0: 
            market.buy(char, "flour", block=False) #buy that free flour
        char.visit(tutorial_url) #visit mentor to get free stuff

    #EAT
    diet = MinCostDiet(char)
    min_eat(char, diet)

    #WORK
    if char.level != 0:
        pass
    elif char.money > 70 and char.reputation < 5:
        if activity.work_at_church(char):
            char.donate_to_church()
    elif activity.work_in_mine(char, duration=1) or activity.apply_for_job(char) or activity.apply_for_imw(char, duration=1):
       pass
    

    #LEVEL UP
    if char.reputation >=5 and char.money > 110 and char.level == 0:
        char.level_up_1(field) 





def min_eat(char, diet):
    """
    EAT in 1-2-1 fashion
    """
    myhunger = 0
    if char.health < 6:
        myhunger = char.hunger
    elif char.health == 6 and char.hunger > 1:
        myhunger = 1
    diet.hunger = myhunger
    diet.eat()



