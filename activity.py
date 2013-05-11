from  gameurls import *
from townhall import Job
from init import log

import time
import mechanize
import townhall


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
    


def work_in_mine(char, duration=22, mine=None):
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

    br = char.visit(outskirts_url)
    if duration not in [1,2,6,10,22]:
        duration = 22


    if mine == None:
        for form in br.forms():
            if form.action.find('t=mine') != -1:
                form["duree"] = [str(duration)]
                br.form = form
                br.submit()
                time.sleep(10)
                if char.is_working():
                    break

    else:
        for form in br.forms():
            if form.action.find('t=mine') != -1 and form.action.find("n="+str(mine)) != -1:
                form["duree"] = [str(duration)]
                br.form = form 
                br.submit()
    char.logout()
    time.sleep(5)  #experimental
    char.login()
    result = char.is_working()
    char.logger.write(log() + " Mine Application: " + str(result) + '\n')
    return result




def apply_for_job(char, job_evaluator=sample_job_evaluator):
    """
    Applies for a player posted job at the townhall.
    Arguments:
    - `job_evaluator`: A function that evaluates the job list and
    returns a job choice or None
    Returns: True if we got a job that we like, False otherwise
    """
    if char.is_working():
        return False

    br = char.visit(townhall_url)
    jobs = townhall.get_jobs(br)
    choice = sample_job_evaluator(jobs)
    if choice == None:
        return False


    for form in br.forms():
        if form.action.find('action=13') != -1: #selects job application form
           if int(form.controls[0].value) == choice.formcode:
               br.form = form 
               br.submit()
    char.logout()
    time.sleep(5)  #experimental
    char.login()
    result = char.is_working()
    char.logger.write(log() + " Job Application: " + str(result) + "\n")
    return result



def apply_for_imw(char, duration=22):
    """
    Works at the IMW
    Arguments:
    - `char`:
    - `duration`:
    """
    if char.is_working():
        return False
    if duration not in [1,2,6,10,22]:
        duration=22
    br = char.visit(outskirts_url)

    try:
        for form in br.forms():
            if form.action.find("action=338") != -1 and form.action.find("t=rmi") !=-1:
                br.form = form
                br["duree"] = [str(duration)]
                br.submit()
                break
    except:
        char.logger.write(log() + "GOT EXCEPTION IN IMW FORM\n")
        char.logger.write(str(br.response().read()))

    char.logout()
    time.sleep(5)  #experimental
    char.login()
    result = char.is_working()
    char.logger.write(log() + " IMW Application: " + str(result) + "\n")



def work_at_church(char):
    """
    Makes the character work at church
    """
    if char.is_working():
        return False

    br = char.visit((game_url + "Action.php?action=1"))
    char.logger.write(log() + " Working at church\n")
    return True



def retreat(char):
    """
    Puts the character into retreat
    """
    if char.is_working():
        return False
    br = char.get_browser()
    br.open(game_url+"Action.php?action=37")
    return True
    


def travel(char, dst):
    """
    Makes the character travel to the given destination
    Arguments:
    - `char`:
    - `dst`: The node number to travel to
    """
    
    br = char.visit(outskirts_url)

    for form in br.forms():
        if form.action.find("action=68") != -1:
            if int(form.controls[0].value) == dst:
                br.form = form
                br.submit()
    char.logout()
    time.sleep(5)  #experimental
    char.login()
    return char.is_working()
