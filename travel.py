from gameurls import *
from collections import deque
from gamedata import node_map

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
        if len(arr):
            adjlist[int(arr[0])].append(int(arr[1]))
            adjlist[int(arr[1])].append(int(arr[0]))

    return adjlist


def get_node_number(char, adjlist):
    """
    Returns the node number the character is currently at
    Arguments:
    - `char`:
    """

    br = char.get_browser()
    br.open(outskirts_url)
    neighbours = []
    for form in br.forms():
        if "action=68" in form.action:
            neighbours.append(int(form.controls[0].value))
            
    for i in range(0, len(adjlist)):
        if i not in neighbours and len(adjlist[i]): #exclude the neighbours and disconnected nodes
            assertion = True #asserting that this is the characte's node
            for j in adjlist[i]:
                if j not in neighbours:
                    assertion = False
            if assertion: 
                return i

    print "Unable to find the character's node: " +  char.name
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


def get_next_hop(char, destination):
    """
    Returns the next node in the shortest path the character must travel inorder
    to reach 'destination'. 
    """
    if destination not in node_map:
        raise ValueError("Destination not in the db. - " + destination)

    destination = node_map[destination]
    adjlist = load_world_map()
    src = get_node_number(char, adjlist)

    if destination == src:
        return None

    depth = [-1] * len(adjlist)
    parents = breadth_first_visit(adjlist, depth, src)
    if depth[destination] == -1:
        print "Destination not reachable -- " + destination
        return None

    node = destination
    path = [node]
    while node != src: #parent of the source node is -1
        path.append(parents[node])
        node = parents[node]

    path = path[::-1]
    print path
    return path[2] if len(path) >= 3 else path[1]
