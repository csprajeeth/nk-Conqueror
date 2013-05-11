from gameurls import *
from bs4 import BeautifulSoup
from gamedata import item_map
from init import log
import re
import mechanize
import urllib
import time


def get_market_sales(char, item=None):
    """
    Returns the market information which is a list containing tuples of form
    (item_code, price, quantity).
    The list is sorted according to item codes and for each item code group,
    it is sorted according that item's price
    Arguments:
    - `char`:
    - `item`: The item whose information is desired. If None then the whole market
    information is returned
    """

    br = char.visit(market_url)
    page = br.response().read()    
    m = re.search("textePage\[0\]\[\'Texte\'\] = '",  page, re.IGNORECASE)
    start = m.end(0)
    end = page.find("';",start)
    soup = BeautifulSoup(page[start:end])

    data = soup.find_all("td") 
    market_data = []
    for i in range(1,int(len(data)/6)):
        inplist = data[6*i+5].form.find_all("input")
        market_item = int(inplist[2]["value"])
        market_price = int(inplist[1]["value"])
        market_quantity = int(data[6*i+3].text)
        market_data.append((market_item, market_price, market_quantity))

    if item == None:
        return market_data 
    if item not in item_map:
        raise ValueError("Item is not in database")
    item_code = item_map[item]

    for i in range(0, len(market_data)):
        if market_data[i][0] == item_code:
            start = i
            while market_data[i][0] == item_code:
                i+=1
            end = i
            return market_data[start:end]
    return None




def snooze_till_market_reset(char):
    """
    Puts the caller to sleep till the market resets (all pending transactions are done)
    ::
    The markets reset at every 10th minute
    Arguments:
    - `char`:
    """
    current_time = char.get_current_time()
    minutes_to_sleep = 10 - (current_time[4]%10) +  0.5 #+0.5 to incorporate some delay for market reset
    char.logger.write(log() + "sleeping for " + str(minutes_to_sleep * 60) + " sec" + '\n')
    char.logout()
    time.sleep(minutes_to_sleep * 60)
    char.logger.write(log() + "woke up...refreshing" + '\n')
    char.login()
    char.refresh()


def apply_price_filter(sales, price):
    """Returns a list of items from the sales that match the price criteria

    Arguments:
    - `sales`:
    - `price`:
    """
    buy_window = []
    if sales == None:
        return []

    if type(price) is tuple or type(price) is list:
        if len(price) != 2:
            raise ValueError("Invalid price specification. Must be a tuple/list with 2 element")
        lprice = int(round(price[0]*100,1))
        hprice = int(round(price[1]*100,1))
        for sale in sales:
            if sale[1] >=lprice and sale[1] <= hprice:  
                buy_window.append(sale)

    elif type(price) is int or type(price) is float:
        if int(round(price*100,1))%10 not in [0,5]:
            raise ValueError("Invalid price. Change must be a multiple of 5")
        tprice = int(round(price*100,1))
        for sale in sales:
            if sale[1] == tprice: 
                buy_window.append(sale)
                break
    elif price == None:
        buy_window = sales

    else :
        raise TypeError("Invalid price specification")

    return buy_window



def buy(char, item, price = None, quantity=1, block=True):
    """Buy's an item from the market
    Default behaviour is to block the caller till the item to be bought
    is in the inventory.
    Arguments:
    - `char`:
    - `item`:
    - `price: There are 3 ways to give a price
    -- Specify a particular price in which case the item is bought from the market
    at that price
    -- Specify a range of the item price (2 element tuple/list) in which case the item is 
    bought from the market in that range if its available
    -- Specify nothing in which case the item is bought for the lowest price available
    on the market
    - `quantity`:
    - `block`: Set to False if you do not want this function to block

    Returns: 
    - The number of items purchased. When used in non-blocking mode the return
    value is meaningless (should be ignored)

    --NOTE OF WARNING--
    THIS FUNCTION STRICTLY SPEAKING SENDS ILLEGAL DATA TO THE GAME WHICH DOESN'T 
    HAPPEN WHEN THE GAME IS PLAYED IN THE BROWSER. SPECIFIALLY THE QUANTITY VARIABLE
    IN THE POST DATA IS RESTRICTED TO A VALUE OF 10 BY THE BROWSER, BUT THIS FUNCTION
    DOESN'T CARE ABOUT THOSE RULES.  #bot_detection
    """

    if item not in item_map:
        raise ValueError("Item is not in the db")

    item_code = item_map[item]

    submit_url = game_url + "Action.php?action=11"
    basket_url = game_url + "Action.php?action=29"
    poster = char.get_poster()
    login_data = char.get_login_data()

    char.update_inventory()
    prev_count = char.inventory[item_code]
    char.logger.write(log() + " prev_count: " + str(prev_count) + '\n')
    bought = 0
    got_money = True
    block_test = True

    if quantity == -1: #buy all that is available on market
        quantity = 0
        sales = get_market_sales(char,item)
        buy_window = apply_price_filter(sales,price)
        for sales in buy_window:
            quantity += sales[2]
        char.logger.write(log() + " Quantity: " +  str(quantity) + '\n')


    while bought != quantity and got_money and block_test:
        to_buy = quantity - bought
        sales = get_market_sales(char, item)
        if sales == None:
            return  bought

        buy_window = apply_price_filter(sales, price)
        if len(buy_window) == 0:
            return bought

        char.update_inventory()
        money = int(round(char.money * 100,1))
    
        poster.open(loginform_url, login_data)
        poster.open(market_url)
        applied = 0 #the number of items in our basket

        for sales in buy_window:
            prix = sales[1]
            quantite = min(to_buy, sales[2])
            char.logger.write(log() + " " + str(prix) + " " + str(quantite) + " " + str(money) + '\n')
            if (prix*quantite) > money:
                got_money = False
                quantite = int(money/prix)

            money -= (prix * quantite)
            poster.open(basket_url, urllib.urlencode({'IDParametre':'0', 'prix':str(prix),
                                                      'quantite':str(quantite), 'typeObjet':str(sales[0])
                                                      }))
            to_buy -= quantite
            applied += quantite
            if to_buy == 0 or got_money == False:
                break
        
        poster.open(submit_url, urllib.urlencode({}))
        char.logger.write(log() + " Applied: " + str(applied) + '\n')
        if block:
            snooze_till_market_reset(char)

        char.update_inventory()
        if applied <= (char.inventory[item_code] - prev_count - bought): 
            got_money = True #for the case where we ran out of money and we did not get item from the market(someone else bought it) 
            #so we must retry again with what amount we have left
        bought = char.inventory[item_code] - prev_count 
        char.logger.write(log() + " Bought: " + str(bought) + '\n')
        block_test = block
        char.logger.write( str(bought!= quantity) + " " + str(got_money) + " " + str(block_test) + '\n')

    return bought



def get_cost(char, item, quantity=1):
    """
    Return the cost (min) of purchasing an item from the market
    Arguments:
    - `char`:
    - `item`:
    - `quantity`:
    """
    if quantity == 0:
        return 0

    sales = get_market_sales(char,item)    
    if sales == None:
        return None

    cost = 0
    for sale in sales:
        cost += (sale[1]* min(quantity, sale[2]))
        quantity -= min(quantity, sale[2])
        if quantity == 0:
            break

    if quantity != 0: #if all items cannot be purchased
        return None
    return cost
