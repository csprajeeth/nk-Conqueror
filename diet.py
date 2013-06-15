from gamedata import *
from init import log
import math
import market

class MinCostDiet():
    """
        Eating minimum cost food consists of 2 steps. 

        1. Eat whatever is there in your inventory first optimally without
        wasting food (eating 4 HP food when you got 3 HP food to satisfy your hunger of 3HP is a no-no)
        -- This is done by consume_inventory_food() method
        
        2. If you do not have enough food in your inventory then buy the minimal cost food
        from the market.
        -- The actual algorithm that determines the min cost food that must be bought from the market
        is in make_optimal_buy_decision

        The eat() method puts them both together.
        
        Note::
        This diet class is highly configurable.
        The items that can be included in the diet can be passed as a second parameter when instantiating.
        The max price for purchase of items from the market for diet purpose can also be specified. In that
        case the element of the list must be a tuple where the first element is the name of the food and the
        second element is the max price to consider buying for.
        
        Ex: MinCostDiet(char, ["beans", "tortilla", ("meat",20), ("fish",17), ("vegetables",10)])
        ---specifies to eat beans, tortilla at any price and meat, fish and veggies at max 20, 17 and 10
        respectively. The diet object then makes the character eat the min cost food after examining the market
        prices and quantities.
    """
    
    def __init__(self, char, food=["beans", "tortilla", "meat", "fish", "fruit", "vegetable", "egg"], hunger=None):
        """
        """
        self.char = char
        self.food = list(set(food))
        self.hunger = hunger
        





    def consume_inventory_food(self, food, hunger):
        """
        Consumes food from the inventory optimally to satisfy `hunger`.
        If `hunger` hunger points cannot be satisfied then it consumes as much
        as it can.
        Arguments:
        - `self`:
        - `hunger`: The amount of hunger points to satisfy
        P.S. This can be reduced to subset sum but i don't wanna do that.
        Lets keep it simple since the hunger bounds are very less.
        Returns:
        The amount of HP satisfied by consuming food from the inventory
        """
        self.char.update_inventory()
        total_hp = 0
        arr = []
        for i in range(0,3):
            arr.append([])

        for item in food:
            qty = self.char.inventory[item_map[item]]
            if qty:
                total_hp += hp_info[item] * qty
                while qty:
                    arr[hp_info[item]].append(item)
                    qty-=1
                
        if total_hp < hunger: #if we don't have enough food
            for i in [1,2]:
                for j in range(0, len(arr[i])):
                    self.char.use(arr[i][j],1)
            return total_hp
        else:
            #make optimal use
            if hunger == 1:
                for i in [1,2]:
                    if len(arr[i]):
                        self.char.use(arr[i][0], 1)
                        break
            elif hunger == 2:
                if len(arr[2]):
                    self.char.use(arr[2][0], 1)
                else:
                    self.char.use(arr[1][0],1)
                    self.char.use(arr[1][1],1)
            elif hunger == 3:
                if len(arr[2]) and len(arr[1]):
                    self.char.use(arr[1][0], 1)
                    self.char.use(arr[2][0], 1)
                elif len(arr[1]) == 3:
                    self.char.use(arr[1][0],1)
                    self.char.use(arr[1][1],1)
                    self.char.use(arr[1][2],1)
                else:
                    self.char.use(arr[2][0], 1)
                    self.char.use(arr[2][1], 1)
                          
            return hunger


        

    def make_optimal_buy_decision(self, items, cost, weight, quantity, W):
        """
        Makes an optimal buy decision.
        
        The problem here is :
        We have N food items each available in Qi quantity, Ci cost, Wi weight (hunger points satisfied)
        We must buy items such that the combined weight is ATLEAST W (char.hunger) and cost is 
        minimized.

        This can be reduced to the Bounded Knapsack problem. Consider 2 bags. 
        TOT = W1 + W2 + .. + Wn. Let 1 bag have all the items. Now we must fill the other bag
        which has a capacity of TOT-W with items from the first bag such that the value is highest
        possible value. This is now the same as the usual Bounded Knapsack problem with the same 
        item list and capacity TOT-W.
 
        However since the quantity of the items is actually controlled by the hunger of the character
        (1,2,3), i will just duplicate the items and use the classic 0-1 knapsack dp algorithm.
        The worst case number of items (n) will be 3*7 = 21 which is quite low. Worst case
        capacity of the knapsack is 3

        Complexity: O(no_of_items*Capacity)
        Arguments:
        - `self`:
        - `items`:
        - `cost`:
        - `weight`:
        - `quantity`: 
        - `W`: The total amount of hunger points of food we need to buy

        Returns:
        The list of items which must be bought and their quantities.
        The cost of the proposed diet.
        """
        
        #duplicate items
        
        for i in range(0, len(quantity)):
            while quantity[i] > 1:
                items.append(items[i])
                cost.append(cost[i])
                weight.append(weight[i])
                quantity[i] -=1
        #print
        #for i in range(0, len(items)):
        #    print items[i], cost[i], weight[i]

        TOT = 0
        for w in weight:
            TOT += w
        capacity = TOT - W

        if capacity < 0: #if there is not enough food on the market
            return items  #then buy all that is available

        N = len(items)

        #make the 2D array of dimensions N+1, capacity+1.
        arr = []
        for i in range(0, N+1):
            arr.append([-1] * int(capacity+1))

        #solve
        for x in range(0, capacity+1):
            arr[0][x] = 0

        for i in range(1, N+1):
            for x in range(0, capacity+1):
                if weight[i-1] > x: #weight[i-1] because [1..N] correspond to [0...N-1] in the lists
                    arr[i][x] = arr[i-1][x]
                else:
                    arr[i][x] = max(arr[i-1][x],
                                    arr[i-1][x-weight[i-1]] + cost[i-1])
    
        #solution reconstruction
        value = arr[N][capacity]
        avoid_list = list()
        i = N
        x = capacity
        while i > 0 and value > 0:
            if arr[i][x] != arr[i-1][x] :
                avoid_list.append(items[i-1])
                value -= cost[i-1]
                x -= weight[i-1]
            i-=1

        for item in avoid_list:
            index = items.index(item)
            items.pop(index)
            cost.pop(index)
            
        value = 0 #cost of the meal
        for i in range(0, len(cost)):
            value += cost[i]

        return items, value





    def eat(self):
        """
        Makes the character eat the minimum cost food.

        Returns the amount of leftover HP points that have not been eaten
        """

        hunger = self.char.hunger if self.hunger == None else self.hunger

        if len(self.food) == 0 or hunger == 0:
            return hunger

        food = list()
        for item in self.food:
            if type(item) is tuple:
                food.append(item[0])
            elif type(item) is str:
                food.append(item)
            else:
                raise TypeError("Invalid item specified in MinCostDiet.food Allowed types are str or tuple")

        for item in food:
            if item not in item_map:
                raise ValueError("Item not in db - " + str(item))

        consumed = self.consume_inventory_food(food, hunger)
        leftover = hunger - consumed
        
        self.char.logger.write(log() + " Consumed " + str(consumed) + " hp worth food from inventory. Need to eat " + str(leftover) + " hp points more."+ "\n")

        while leftover > 0: # we must buy some food from the market
            costs = [] 
            weight = []
            quantity = []
            khana = []

            for item in self.food:
                if type(item) is tuple:
                    sales_info = market.apply_price_filter(market.get_market_sales(self.char, item[0]),(0, item[1]))
                else:
                    sales_info = market.get_market_sales(self.char, item)
                if sales_info == None or len(sales_info) == 0:
                    continue

                food_name = r_food_map[sales_info[0][0]] 
                qty_to_buy = int(math.ceil(float(leftover)/hp_info[food_name]))
                for sale in sales_info:

                    khana.append(food_name)
                    costs.append(sale[1])
                    weight.append(hp_info[food_name])
                    quantity.append(min(qty_to_buy, sale[2]))
                    qty_to_buy -= min(qty_to_buy, sale[2])
                    if(qty_to_buy == 0):
                        break


            self.char.logger.write("leftover: " + str(leftover) + "\n")
            for i in range(0, len(khana)):
                self.char.logger.write(str(khana[i]) + " " + str(costs[i])  + " " + str(quantity[i]) + " " + str(weight[i])+"\n")

            if len(khana) == 0: #when there is no food available to buy on the market (ex: when on the roads)
                return leftover

            buy_list, meal_cost = self.make_optimal_buy_decision(khana, costs, weight, quantity, leftover)
            self.char.logger.write(str(buy_list) + "\n" + "Cost: " + str(meal_cost) + "\n")
            
            khana = list(set(buy_list))
            quantity = []
            prev_counts = []
            for var in khana:
                quantity.append(buy_list.count(var))
            self.char.update_inventory()
            
            money = int(round(self.char.money*100,1))

            for i in range(0, len(khana)):
                prev_counts.append(self.char.inventory[item_map[khana[i]]])
                market.buy(self.char, khana[i], quantity=quantity[i], block=False)

            market.snooze_till_market_reset(self.char)
            
            for i in range(0, len(khana)):
                 leftover -= (hp_info[khana[i]] *  self.char.inventory[item_map[khana[i]]] - prev_counts[i])
                 self.char.use(khana[i], self.char.inventory[item_map[khana[i]]] - prev_counts[i])
                
            if money < meal_cost: # we don't have enough money to buy even the min cost meal, then break out
                self.char.logger.write(log()+ " We don't have enough money to buy food! (money: " + str(money) + ") (cost: " + str(meal_cost) + ")\n")
                break

        return leftover
            # I have not checked for the case where we do not have enough money and the meal that we tried
            # buy (with what we had) was not purchased because someone else bought it.
            # In that case i am leaving it to the game loop to make more iterations and at a later point to try
            # invoking the eat() again, until such a time when there exists a functionality in market.buy()
            # which tells why exaclty the purchasing failed...not gonna code that now
                             



class PriorityDiet():
    """
    To be used if you want to prioritize eating certain food items (for raising stats)

    Pass the food items to be prioritized as a list to the `priority` argument.
    Price options can be specified just like in MinCostDiet.
    If the diet consumption fails, then it falls back to a secondary `fallback` diet.
    `fallback` diet can be configured too.

    Both types of food items (prioritized and fallback) are consumed in such a way that costs
    are minimized
    """
    
    def __init__(self, char, priority=[], hunger=None, fallback=["beans", "tortilla", "meat", "fish", "egg", "vegetable", "fruit"]):
        """
        
        Arguments:
        - `char`:
        - `priority`:
        - `fallback`:
        """
        self.char = char
        self.priority = priority
        self.hunger = hunger
        self.fallback = fallback



    def eat(self):
        """
        
        Arguments:
        - `self`:
        """
        
        hunger = self.char.hunger if self.hunger == None else self.hunger
        leftover = MinCostDiet(self.char, self.priority, hunger).eat()
        if leftover:
            MinCostDiet(self.char, self.fallback, leftover).eat()
