import re

from gameurls import *
from bs4 import BeautifulSoup

class Classroom(object):
    """
    This class represents a 'classroom-class' at the university.
    
    Attributes:
    1. teacher : The teacher
    2. subject : Subject being taught
    3. fee : The fee to attend the class
    4. free_places : The number of free places in the classroom.

    """
    def __init__(self, ID):
        self.teacher = None
        self.subject = None
        self.fee = None
        self.free_places = None

        self.ID = ID
        
        

def get_classrooms(char):
    """
    Returns a list of classrooms.
    """
    
    if char.level < 2:
        return []
    classrooms = []
    page = char.visit(province_url).read()

    for m in re.finditer("(textePage\[2\]\[1\]\[)(\d+)(\]\[\'Texte\'\] = \')", page, re.IGNORECASE):
        classroom = Classroom(int(m.group(2)))
        start = m.end(0)
        end = page.find("';", start)
        text = page[start:end]
        soup = BeautifulSoup(text)

        classroom.teacher = soup.a.text

        m = re.search("(Free\s*places\s*:\s*)(\d+)", soup.text, re.IGNORECASE)
        classroom.free_places = int(m.group(2))
        
        m = re.search("(Total\s*)(\d+).(\d+)", soup.text, re.IGNORECASE)
        classroom.fee = int(m.group(2)) * 100 + int(m.group(3))

        m = re.search("(Teaching\s*:\s*)(\w+.*)(\s*Free)", soup.text, re.IGNORECASE)
        classroom.subject = m.group(2).lower()

        classrooms.append(classroom)

    return classrooms
    
    
