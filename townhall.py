import re

from gameurls import townhall_url
from bs4 import BeautifulSoup

class Job():
    """
    A job class that contains the information about the 
    job posted by other players on the townhall
    """

    def __init__(self):
        self.employer = None
        self.wage = None
        self.stat_required = False
        self.stat = None
        self.stat_value = None
        self.description = None
        self.formcode = None

    def __str__(self):
        return "\nEmployer: "+self.employer+"\nWages: "+str(self.wage)+"\nStat required: "+str(self.stat_required)+"\nStat: "+str(self.stat)+"\nStat value: "+str(self.stat_value)+"\nJob Profile: "+self.description+"\nForm Code: "+str(self.formcode)+"\n"




def get_jobs(char):
    """
    Returns a list of jobs that the player is eligible to apply for
    at the town hall.
    Arguments:
    - `br`:
    """

    response = char.visit(townhall_url)
    page = response.read()
    jobs = []

    for m in re.finditer("textePage\[2\]\[\d+\]\[\'Texte\'\] = \'", page, re.IGNORECASE):
        start = m.end(0)
        end = page.find("';", start)
        text = page[start:end]
        soup = BeautifulSoup(text)

        if  re.search('you have the profile for the job.', text, re.IGNORECASE)  or re.search('you meet the requirements for this job.',text, re.IGNORECASE):
            job = Job()
            job.employer = soup.a.text if soup.find('a') else "Province/County"
            m = re.search('Skills required: \d+ ', text, re.IGNORECASE)
            if m != None: #skills are required. we need to see which are that
                job.stat_required = True
                job.stat_value = int((m.group(0).split(" "))[2])
                job.stat = text[m.end(0):text.find("Points")].lower()
            m = re.search('(Wages\s*:\s*)([0-9.,]+)', text, re.IGNORECASE)
            job.wage =  float(re.sub(",", ".", m.group(2)))
            m = re.search('requires a worker to ', text, re.IGNORECASE)
            if m == None:
                m = re.search('looking for a ', text, re.IGNORECASE)
            job.description = text[m.end(0):text.find('.', m.end(0))]
            m = re.search('value="\d+"', text, re.IGNORECASE)
            m = re.search("\d+", m.group(0))
            job.formcode = int(m.group(0))
            jobs.append(job)

    return jobs


                
                
                
    
    


