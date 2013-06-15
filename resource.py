import re
import random

from init import log
from gameurls import *
from bs4 import BeautifulSoup
from gamedata import *

resource_list = ["lake", "orchard", "forest"]


def get_resource_type(char):
    """
    Returns the resource that character can harvest (lake/orchard/forest)
    None if no resource is available
    Arguments:
    - `char`: The character object
    """

    soup = BeautifulSoup(char.visit(town_url).read())
    tag = soup.find("a",{"class":"lieu_village01 lieu_village"})
    resource = (tag.text.split("\n"))[0].lower() if tag != None else None
    return resource



def has_equipped_tool(char, resource):
    """
    Returns True of False depending on whether
    the character has equipped the tool 
    associated with the resource.
    Arguments:
    - `char`: The character object
    - `resource`: The resource to harvest
    """

    if resource == "lake":
        return char.tools[71] 
    if resource == "orchard":
        return char.tools[66] or char.tools[67]
    if resource == "forest":
        text = BeautifulSoup(get_resource_text(char)).text
        can_lend = False if re.search("no\s*more.*to\s*lend", text, re.IGNORECASE) else True
        return can_lend or char.tools[73]



def use_tool(char, resource):
    """
    Makes the character to use the 
    tool in the inventory related to the resource.
    Arguments:
    - `char`: The character object
    - `resource`: The resource to harvest
    """
 
    if resource == "lake":
        char.use("canoe")
    if resource == "forest":
        char.equip("axe")
    if resource == "orchard":
        char.use("large ladder")
        char.use("small ladder")
  


def buy_tool(char, resource):
    """
    Buys the tool required to harvest 'resource'
    at the cheapest price from the market.
    Arguments:
    - `char`: The character object
    - `resource`: The resource to harvest
    """
    bought = 0
    if resource == "lake" and char.strength > 6:
        bought = market.buy(char, "canoe")
    if resource == "orchard":
        if char.strength >= 20:
            bought = market.buy(char, "large ladder")
        if not bought and char.strength >= 10:
            bought = market.buy(char, "small ladder")
    if resource == "forest":
        bought = market.buy(char, "axe")

    return bought



def get_resource_text(char):
    """
    Returns the text describing the resource in the 
    resource page
    Arguments:
    - `char`: The character object
    """
    
    page = char.visit(resource_url).read()
    s1 = "textePage[0]['Texte'] = '"
    s2 = "';"
    start = page.find(s1) + len(s1)
    end = page.find(s2, start)
    return page[start:end]



def get_resource_string(resource):
    """
    Returns the activity string associated
    with harvesting a resource
    Arguments:
    - `resource`: The resource to harvest
    """

    return game_strings.activity[resource]



def get_max_Y_coordinate(resource):
    """
    Returns the maxmimum Y coordinate in a resource
    Arguments:
    - `resource`: The resource to harvest
    """
    coordinate = {"lake":19, "orchard":4, "forest":3}
    return coordinate[resource]



def get_max_moves(char, resource):
    """
    Returns the maximum number of moves a character can make
    in a resource
    Arguments:
    - `char`: The character object
    - `resource`: The resource to harvest
    """

    divisor = {"lake":5, "orchard":3, "forest":10} 
    addend = {"lake":2, "orchard":2, "forest":1}
    m = re.search("(\d+)(/)(\d+)", get_resource_text(char))
    chances = char.intelligence/divisor[resource] + addend[resource] if m == None else int(m.group(3)) - int(m.group(1))
    chances = min(3,chances) if resource == "forest" else chances
    return chances



def set_Y_coordinate(char, resource):
    """
    Sets the maximum y coordinate for a resource
    Arguments:
    - `char`: The character object
    - `resource`: The resource to harvest
    """

    char.update_tools_and_wardrobe()
    if resource == "lake":
        y = min(19, char.strength)
        y = min(6, y) if not char.tools[71] else y
    elif resource == "orchard":
        y = min(4, char.strength/5)
        y = min(2,y) if not char.tools[67] else y
        y = min(0,y) if not char.tools[66] and not char.tools[67] else y
    else:
        y = min(3, char.strength/5)
    return y



def get_yield(text, resource):
    """
    Returns the percentage yield of a resource spot
    Arguments:
    - `text`: The resource text
    - `resource`: The resource being harvested
    """
    if resource in ["lake", "orchard"]:
        m = re.search("(\d+)(\s*%)", text)
        return int(m.group(1))
    else:
        m = re.search("(<br>\s*)(\d+)(.*wood)", text, re.IGNORECASE)
        return int(m.group(2))



def update_X_coordinate(x, y, resource):
    """
    Arguments:
    - `x`: The current x coordinate of the character in thr resource
    - `resource`: The resouce being harvested
    """

    if resource == "lake":
        return (x+1)%20
    elif resource == "orchard":
    #COORDINATES:
        # X = 0 - 71  Y = 0
        # X = 0 - 84  Y = 1
        # X = 0 - 95  Y = 2
        # X = 0 - 39  Y = 3
        # X = 0 - 4   Y = 4
        limit_X = [72, 85, 96, 40, 5]
        return (x+1) % limit_X[y]
    else:
        # X = 0 - 9   Y = 0
        # X = 0 - 11  Y = 1
        # X = 0 - 9   Y = 2
        # X = 0 - 10  Y = 3
        limit_X = [10, 12, 10, 11]
        return (x+1) % limit_X[y]
        
