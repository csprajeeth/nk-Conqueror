import urllib
import time
import townhall

from townhall import Job
from init import log
from gameurls import *
from bs4 import BeautifulSoup



def sample_job_evaluator(jobs):
    """Returns a job from the list of jobs to perform or returns None
    if none of the job matches the criteria    
    Arguments:
    - `jobs`:
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
    - `char`:
    - `evaluator`: 
    """

    if char.is_working():
        return False

    job = evaluator(townhall.get_jobs(char))
    if job == None:
        return False

    char.visit(game_url+"Action.php?action=13", urllib.urlencode({"IDOffre":str(job.formcode)}))


    result = char.is_working()
    char.logger.write(log() + " Job Application: " + str(result) + " (" + str(char.activity) + ")" + '\n')
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
    - `duration`:
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
    
    for url in url_list:
        char.visit(url, urllib.urlencode({'duree':str(duration)}))
    

    result = char.is_working()
    char.logger.write(log() + " IMW Application: " + str(result) + " (" + str(char.activity) + ")" + "\n")
    return result




def travel(char, dst):
    """
    Makes the character travel to the given destination
    Arguments:
    - `char`:
    - `dst`: The node number to travel to
    """
    if char.is_working():
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
    
