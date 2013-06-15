from gameurls import *
from bs4 import BeautifulSoup
from gamedata import item_map
from init import log

import re
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

    Returns: The market information.
    """

    response = char.visit(market_url)
    page = response.read()    
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
        raise ValueError("Item is not in database - " + str(item))
    item_code = item_map[item]

    for i in range(len(market_data)):
        if market_data[i][0] == item_code:
            start = i
            while i < len(market_data) and market_data[i][0] == item_code:
                i+=1
            end = i
            return market_data[start:end]
    return []




def snooze_till_market_reset(char):
    """
    Puts the caller to sleep till the market resets (all pending
    transactions are done). The markets reset at every 10th minute
    Arguments: - `char`:
    """

    page = char.visit(market_url).read()
    s1 = "textePage[1]['Texte'] = '"
    s2 = "Sale"
    start = page.find(s1) + len(s1)
    end = page.find(s2, start)
    text = page[start:end].lower()
    if "each" in text:
        current_time = char.get_current_time()
        minutes_to_sleep = 10 - (current_time[4]%10) +  0.25 #to incorporate some delay for market reset
        char.logger.write(log() + " Waiting for items purchased from the market (" + str(minutes_to_sleep * 60) + " seconds)" + '\n')
        char.logout()
        time.sleep(minutes_to_sleep * 60)
        char.logger.write(log() + " Market transanctions done. Continuing.." + '\n')
        char.login()
        char.refresh()




def apply_price_filter(sales, price=None):
    """Returns a list of items from the sales that match the price criteria

    Arguments:
    - `sales`:
    - `price`:
    """
    buy_window = []

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
            raise ValueError("Invalid price. Change must be a multiple of 5 - " + str(price))
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
    - `quantity`: Set to -1 to buy the all quantity on the market
    - `block`: Set to False if you do not want this function to block

    Returns: 
    - The number of items purchased. When used in non-blocking mode the return
    value is meaningless (should be ignored)

    """

    if item not in item_map:
        raise ValueError("Item is not in the db - " + str(item))

    item_code = item_map[item]
    submit_url = game_url + "Action.php?action=11"
    basket_url = game_url + "Action.php?action=29"
    poster = char.get_browser()

    char.update_inventory()
    prev_count = char.inventory[item_code]

    bought = 0
    got_money = True
    block_test = True

    if quantity == -1: #buy all that is available on market
        quantity = 0
        sales = get_market_sales(char,item)
        buy_window = apply_price_filter(sales,price)
        for sales in buy_window:
            quantity += sales[2]
        if len(buy_window) == 0:
            char.logger.write(log() + " Item not available in price range\n" +
                              "Bought " + str(bought) + " " + str(item) + "\n")


    char.logger.write(log() + " Buying item: " + str(item) + " from the market\n" )
    char.logger.write(log() + " Quantity: " +  str(quantity) + '\n')
    #char.logger.write(log() + " prev_count: " + str(prev_count) + '\n') #debug. should be removed


    while bought != quantity and got_money and block_test:
        to_buy = quantity - bought
        sales = get_market_sales(char, item)
        if len(sales) == 0:
            char.logger.write(log() + " Item not available on the market\n" + 
                              "Bought " + str(bought) + " " + str(item) + "\n")
            return  bought

        buy_window = apply_price_filter(sales, price)
        if len(buy_window) == 0:
            char.logger.write(log() + " Item not available in price range\n" +
                              "Bought " + str(bought) + " " + str(item) + "\n")
            return bought

        char.update_inventory()
        money = int(round(char.money * 100,1))
    
        #char.visit(market_url)
        ordered = 0 #the number of items in our basket

        for sales in buy_window:
            prix = sales[1]
            quantite = min(to_buy, sales[2])
            char.logger.write(log() + " Price:" + str(prix) + " Quantity:" + str(quantite) + " Money:" + str(money) + '\n')
            if (prix*quantite) > money:
                got_money = False
                quantite = int(money/prix)

            money -= (prix * quantite)
            poster.open(basket_url, urllib.urlencode({'IDParametre':'0', 'prix':str(prix),
                                                      'quantite':str(quantite), 'typeObjet':str(sales[0]) #bd
                                                      })) 
            to_buy -= quantite
            ordered += quantite
            if to_buy == 0 or got_money == False:
                break
        
        poster.open(submit_url, urllib.urlencode({}))
        char.logger.write(log() + " Ordered: " + str(ordered) + '\n')
        if block:
            snooze_till_market_reset(char)

        char.update_inventory()
        recent_purchase = char.inventory[item_code] - prev_count - bought

        if not got_money and ordered and ordered > recent_purchase: #for the case where we ran out of money and we did not get item from the market(someone else bought it) 
            got_money = True                                        #so we must retry again with what amount we have left

        bought = char.inventory[item_code] - prev_count 
        char.logger.write(log() + " Bought: " + str(bought) + '\n')
        block_test = block
        #char.logger.write( str(bought!= quantity) + " " + str(got_money) + " " + str(block_test) + '\n')

    char.logger.write(log() + " Bought " + str(bought) + " " + str(item) + "\n")
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
    if len(sales) == 0:
        return -1

    cost = 0
    for sale in sales:
        cost += (sale[1]* min(quantity, sale[2]))
        quantity -= min(quantity, sale[2])
        if quantity == 0:
            break

    if quantity != 0: #if all items cannot be purchased
        return -1

    return cost
