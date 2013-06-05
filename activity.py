import urllib
import time
import re
import townhall
import resource

from townhall import Job
from init import log
from gameurls import *
from bs4 import BeautifulSoup



def sample_job_evaluator(jobs):
    """Returns a job from the list of jobs to perform or returns None
    if none of the job matches the criteria    
    Arguments:
    - `jobs`: A list of player posted jobs (each of which is a home.Job object)
    """
    choice = None
    wage  = 14.0
    for job in jobs:
            if (job.stat_required == True and job.wage > 16.0) or (job.stat_required == False):
                if job.wage  > wage:
                    choice = job
                    wage = job.wage
            
    return choice




def apply_for_job(char, evaluator = sample_job_evaluator):
    """
    Applies for a player posted job in the townhall
    Arguments:
    - `char`: The character object
    - `evaluator`: 
    """

    if char.is_working():
        return False

    job = evaluator(townhall.get_jobs(char))
    if job == None:
        return False

    char.visit(game_url+"Action.php?action=13", urllib.urlencode({"IDOffre":str(job.formcode)}))


    result = char.is_working()
    char.logger.write(log() + " Job Application: " + str(result) + " (" + str(char.activity) + ") " + '\n')
    return result




def work_in_mine(char, duration=1, mine=None):
    """
    Performs the activity of mining. You can set the duration of the activity
    as well as which mine(node number) to work in
    Arguments:
    - `mine`: the node number of the mine
    - `duration`: the hours to work
    Returns: True if got a spot for mining, False otherwise
    """
   
    if char.is_working():
        return False
    if duration not in [1,2,6,10,22]:
        duration = 1

    s1 = "textePage[1]['Texte'] = '"
    s2 = "textePage[2] = new"
    page = char.visit(outskirts_url).read()
    start = page.find(s1)
    end = page.find(s2)
    end = page.rfind("'",start,end)
    start+=len(s1)
    soup = BeautifulSoup(page[start:end])
    forms = soup.find_all('form')
    mine_list = [game_url+form['action'] for form in forms if "t=mine" in form['action']]
    mine_list = set(mine_list)

    if mine == None:
        for url in mine_list:
            char.visit(url, urllib.urlencode({'duree':str(duration)}))
    else:
        for url in mine_list:
            if "n="+str(mine) in url:
                char.visit(url, urllib.urlencode({'duree':str(duration)}))
                break


    result = char.is_working()
    char.logger.write(log() + " Mine Application: " + str(result) + " (" + str(char.activity) + ")" + '\n')
    return result



def apply_for_imw(char, duration=1):
    """
    Applies for IMW
    Arguments:
    - `duration`: Duration of activity in hours
    """

    if char.is_working():
        return False
    if duration not in [1,2,6,10,22]:
        duration = 1

    s1 = "textePage[1]['Texte'] = '"
    s2 = "textePage[2] = new"
    page = char.visit(outskirts_url).read()
    start = page.find(s1)
    end = page.find(s2)
    end = page.rfind("'",start,end)
    start+=len(s1)
    soup = BeautifulSoup(page[start:end])
    forms = soup.find_all('form')
    url_list = [game_url+form['action'] for form in forms if "t=rmi" in form['action']]
    url_list = set(url_list)

    for url in url_list:
        char.visit(url, urllib.urlencode({'duree':str(duration)}))
    

    result = char.is_working()
    char.logger.write(log() + " IMW Application: " + str(result) + " (" + str(char.activity) + ")" + "\n")
    return result



def pick_herbs(char, duration=2):
    """Picks medicinal herbs
    ARGUMENTS:
    -`char`: The character object
    -`duration`: Duration of the activity in hours
    RETURNS:
    -`True`: If the character is picking herbs
    -`False': Otherwise
    """

    if char.is_working():
        return False
    if duration not in [2,6,12,24]:
        duration = 2
    url = game_url+"Action.php?action=338&t=rechercheComposants"
    char.visit(url, urllib.urlencode({'duree':str(duration)}))

    result = char.is_working()
    char.logger.write(log() + " Pick herbs: " + str(result) + " (" + str(char.activity) + ")" + "\n")
    return result



def look_for_rare_materials(char):
    """
    Searches on the node for rare materials 
    Arguments:
    - `char`: The character object
    """

    if char.is_working():
        return False
    char.visit(game_url+"Action.php?action=275")
    result = char.is_working()
    char.logger.write(log() + " Look for rare materials: " + str(result) + " (" + str(char.activity) + ")" + "\n")
    return result



def travel(char, dst):
    """
    Makes the character travel to the given destination
    Arguments:
    - `char`: The character object
    - `dst`: The node number to travel to
    """
    if char.is_working():
        return False
    if char.load > char.maxload:
        char.logger.write(log() + " Unable to travel due to inventory overload: " + str(char.load) + "/" + str(char.maxload) + "\n")
        return False

    char.visit(game_url+"Action.php?action=68", urllib.urlencode({"n":str(dst)}))
    result = char.is_working()
    char.logger.write(log() + " Traveling to node " + str(dst) + " - " + str(result) + " (" + str(char.activity) + ")" + "\n")
    return result



def work_at_church(char):
    """
    Makes the character work at church
    """
    if char.is_working():
        return False

    char.visit((game_url + "Action.php?action=1"))
    char.logger.write(log() + " Working at church" + " (" + str(char.activity) + ")" + "\n")
    return True



def retreat(char):
    """
    Puts the character into retreat
    """
    if char.is_working():
        return False

    char.visit(game_url+"Action.php?action=37")
    char.logger.write(log() + "Going into retreat" + " (" + str(char.activity) + ")" + "\n")
    return True
    

def apply_for_militia(char):
    """
    Applies for militia job
    Arguments:
    - `char`:
    """
    if char.level < 1 or char.is_working():
        return False
    char.visit(game_url+"Action.php?action=43")



def harvester(char, rsc):
    """
    Harvests resource.
    Arguments:
    - `char`: The character object
    - `rsc`: The resource to be harvested
    """

    if rsc not in resource.resource_list:
        char.logger.write(log() + " Illegal resource: " + str(rsc) + "\n")
        return False

    if char.activity != resource.get_resource_string(rsc) and char.is_working():
        return False

    limit_Y = resource.get_max_Y_coordinate(rsc)
    max_yield=0
    chances = resource.get_max_moves(char, rsc)
    br = char.get_browser()
    x = 0
    y = resource.set_Y_coordinate(char, rsc)
    max_X = x
    max_Y = y
   
    while chances > 1 and 0 <= y <= limit_Y:
        url = game_url+"Action.php?action=50&x=" + str(x) + "&y=" + str(y)
        try:
            br.open(url, timeout=35)
        except:
            char.logger.write(log() + " -ERROR OPENING URL: " + url + "\n")
            traceback.print_exc(file=char.logger)
            time.sleep(15)

        text = resource.get_resource_text(char)
        tmp = resource.get_yield(text, rsc)
        char.logger.write("X:" + str(x) + " Y:" + str(y) + " " + str(tmp) + "\n")
        if tmp > max_yield:
            max_yield = tmp
            max_X = x
            max_Y = y
        x = resource.update_X_coordinate(x, y, rsc)
        y = (y-1) if x == 0 else y
        m = re.search("(\d+)(/)(\d+)", text)
        chances = int(m.group(3)) - int(m.group(1)) 

    char.visit(game_url+"Action.php?action=50&x="+str(max_X)+"&y="+str(max_Y))
    max_Yield = resource.get_yield(resource.get_resource_text(char), rsc)

    result = char.is_working()
    char.logger.write(log() + " Harvest " + str(rsc) + " : "  + str(result) + " (" + str(char.activity) + ")")
    if result:
        char.logger.write(" [X=" + str(max_X) + " Y=" + str(max_Y) + " " + str(max_yield) + "]")
    char.logger.write("\n")
    return result



def harvest_resource(char, autousetool=False, autobuytool=False, price=None):
    """
    Harvests the clan resource (Lake/Orchard/Forest)
    Arguments:
    - `char`: The character object
    """
    
    rsc = resource.get_resource_type(char)
    if rsc in resource.resource_list:
        if autousetool and not resource.has_equipped_tool(char, rsc):
            resource.use_tool(char, rsc)
        if autobuytool and not resource.has_equipped_tool(char, rsc):
            resource.buy_tool(char, rsc)
            resource.use_tool(char, rsc)
        return harvester(char, rsc)
    else:
        char.logger.write(log() + " Harvest Resource: False (" + str(char.activity)+ ") - unknown resource - " + str(rsc) + "\n")
        return False


