import re

from gameurls import *
from collections import deque
from gamedata import node_map
from init import log

def load_world_map():
    """
    Returns the adjacency list of the world map.
    The file worldmap must be located in /data folder
    """
    file = open("./data/worldmap")
    lines = file.readlines()
    nodes = int(lines[0])
    adjlist = []
    while nodes:
        adjlist.append([])
        nodes-=1
    for i in range(1, len(lines)):
        arr = lines[i].strip().split(" ")
        if len(arr) == 2 and arr[0].isdigit() and arr[1].isdigit():
            adjlist[int(arr[0])].append(int(arr[1]))
            adjlist[int(arr[1])].append(int(arr[0]))
    file.close()
    return adjlist


def get_node_number(char, adjlist, neighbours):
    """
    Returns the node number the character is currently at
    Arguments:
    - `char`:
    """
    for i in range(0, len(adjlist)):
        if i not in neighbours and len(adjlist[i]): #exclude the neighbours and disconnected nodes
            assertion = True #asserting that this is the characte's node
            for j in adjlist[i]:
                if j not in neighbours:
                    assertion = False
            if assertion: 
                return i

    char.logger.write(log()+ "Unable to find the character's node: ")
    return None



def breadth_first_visit(graph, depth, src):
    """
    Performs a bread first visit from the source node
    Arguments:
    - `graph`:
    - `depth`:
    - `src`:
    """
    Q = deque()
    Q.append(src)
    depth[src] = 0
    parents = [-1] * len(graph)

    while len(Q):
        node = Q.popleft()
        for adjnode in graph[node]:
            if depth[adjnode] == -1:
                Q.append(adjnode)
                depth[adjnode] = depth[node] + 1
                parents[adjnode] = node
    
    return parents


def get_next_hop(char, destination, exclude_list = []):
    """
    Returns the next node in the shortest path the character must travel inorder
    to reach 'destination'. 
    
    `exclude_list`: A list of nodes to avoid. Used in case you know there are 
    enemy armies or robbers.

    Note: It takes care of whether or not the character is a noble (3 node coverage)
    or a normal traveller (2 node coverage)
    Arguments:
    -`destination`: can be a node number or the name of a town
    """

    if type(destination) is str:
        destination = destination.lower()
        if destination not in node_map:
            raise ValueError("Destination not in the db. - " + str(destination))
        destination = node_map[destination]
    if type(destination) is not str and type(destination) is not int:
        raise TypeError("Invalid type supplied as destination - " + str(destination))
    
    if not 1 <= destination <= 299:
        char.logger.write(log() + " Invalid node number\n")
        return None

    page = char.visit(outskirts_url).read()
    neighbours = []
    for m in re.finditer("(textePage\[0\]\[)(\d+)(\]\[\'Texte\'\] = \')", page, re.IGNORECASE):
        neighbours.append(int(m.group(2)))

    adjlist = load_world_map()    
    src = get_node_number(char, adjlist, neighbours)
    if destination == src:
        char.logger.write(log() + " We are at the destination\n")
        return None

    #Disconnecting the excluded nodes from the graph
    for node in exclude_list:
        for i in adjlist[node]:
            adjlist[i].remove(node)
        adjlist[node] = []
 
    
    depth = [-1] * len(adjlist)
    parents = breadth_first_visit(adjlist, depth, src)
    if depth[destination] == -1:
        char.logger.write(log() + " Destination not reachable -- " + str(destination))
        return None

    node = destination
    path = [node]
    while node != src: 
        path.append(parents[node])
        node = parents[node]

    path = path[::-1]
    char.logger.write(log() + " Route: Our Location-> " + str(path) + " <-Destination\n")

    #return the farthest neighbour -- takes care of noble travelling too
    dst = -1
    for node in neighbours:
        try:
            index = path.index(node)
            if index > dst:
                dst = index
        except:
            pass
    return path[dst]

