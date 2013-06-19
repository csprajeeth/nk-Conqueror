from collections import namedtuple

server_maintainance_start = "8:59:00"
server_maintainance_end = "9:10:00"

healthTable = {
"you are fit":6,
"you are exhausted":5,
"you are weak":4,
"you are skinny":3,
"you are bony":2,
"you are dying":1,
"you are dead":0
}

hungerTable = {
"you are not hungry.":0,
"you\\'re hungry":1,
"you\\'re veryhungry":2,
"you\\'re very hungry":2,
"you\\'re very\\nhungry":2,
"you\\'re starving":3
}

scrape_strings = {
"hunger":"hunger\s*:\s*",
"health":"(health|fitness)\s*:\s*",
"activity":"activity\s*:\s*",
}

stat_strings = {
"str":"strength",
"int":"intelligence",
"charisma":"charisma",
"rep":"reputation points"
}

activity_strings = {
"mine":'you are working in the mine', 
"imw":'you are working for the province',
"travel":'traveling',
"none":'none',
"lake":'fishing',
"orchard":'picking fruit',
"forest":'cut wood',
"search":"search for valuable resources",
}

resource_strings = {
"lake":"lake",
"orchard":"orchard",
"forest":"forest",
}

item_strings = {
"boat":"canoe",
"small ladder":"small ladder",
"large ladder":"large ladder",
"axe":"obsidian axe",
}

GameStrings = namedtuple('GameStrings', ['scrape', 'stats', 'activity', 'resource', 'items'])
game_strings = GameStrings(scrape = scrape_strings, stats = stat_strings, activity = activity_strings,
                           resource = resource_strings, items = item_strings)


item_map = {
"money":0,
"quachtli":0,
"pounds":0,
"pound":0,

"bread":50,
"tortilla":50,
"tortillas":50,
"fruit":51,
"fruits":51,
"bean":52,
"beans":52,
"corn":52,
"bags of corn":52,
"bag of corn":52,
"bag of beans":52,
"bags of beans":52,
"egg":53,
"eggs":53,
"milk":53,
"bottle of milk":53,
"bottles of milk":53,
"fish":54,
"fishes":54,
"meat":55,
"piece of meat":55,
"pieces of meat":55,
"maize":56,
"wheat":56,
"bag of maize":56,
"bags of maize":56,
"flour":57,
"maize flour bag":57,
"maize flour bags":57,

"stone":59,
"quintal of stone":59,
"quintals of stone":59,
"peccary":60,
"carcass of peccary":60,
"carcasses of peccary":60,
"wool":61,
"ball of wool":61,
"balls of wool":61,
"agave":62,
"agave fabric":62,
"agave fabrics":62,

"vegetable":64,
"vegetables":64,
"wood":65,
"wood bushel":65,
"wood bushels":65,
"small ladder":66,
"small ladders":66,
"large ladder":67,
"large ladders":67,
"oar":68,
"oars":68,
"shaft":70,
"shafts":70,
"canoe":71,
"canoes":71,
"pepito":72,
"pepitos":72,
"axe":73,
"obsidian axe":73,
"obsidian axes":73,

"blunted obsidian axes":83,
"blunted obsidian axe":83,

"obsidian ore":76,
"kilo of obsidian ore":76,
"kilos of obsidian ore":76,

"hamper":78,
"hampers":78,
"knife":79,
"knives":79,
"flint knife":79,
"flint knives":79,
"obsidian shard":80,
"obsidian shards":80,

"headdress":84,
"sarapes":85,
"sarape":85,
"huipils":86,
"huipil":86,

"loincloths":88,
"loincloth":88,

"men's leggings":91,
"men's legging":91,
"woman's leggings":92,
"woman's legging":92,
"sandals":93,
"sandal":93,

"sword":105,
"swords":105,
"club":105,
"clubs":105,
"shield":106,
"shields":106,

"handcart":182,
"carts":182,

"fleur pavot blanc":341,
"fleurs pavot blanc":341,

"poplar bud":352,
"poplar buds":352,
"manioc root":353,
"manioc roots":353,
"magnolia flower":354,
"magnolia flowers":354,
"sarsaparilla root":355,
"sarsaparilla roots":355,
"garlic bulb":356,
"garlic bulbs":356,
"tarragon leaves":357,
"tarragon leaf ":357,
"cacao leaves":358,
"cacao leaf":358,
"tabasco seeds":359,
"tabasco seed":359,
"pine resins":360,
"pine resin":360,
"sage leaves":361,
"sage leaf":361,
"tomato roots":362,
"tomato root":362,
"amaryllis flowers":363,
"amaryllis flower":363,
"leaves of wild acanthus":364,
"leaf of wild acanthus":364,
"black elderberry berry":365,
"black elderberry berries":365
}

hp_info = {   
"bread":2,
"tortilla":2,
"tortillas":2,
"fruit":1,
"fruits":1,
"bean":1,
"beans":1,
"corn":1,
"bag of corn":1,
"bags of corn":1,
"bag of beans":1,
"bags of beans":1,
"egg":1,
"eggs":1,
"milk":1,
"bottle of milk":1,
"bottles of milk":1,
"fish":2,
"fishes":2,
"meat":2,
"piece of meat":2,
"pieces of meat":2,
"vegetable":1,
"vegetables":1
}


r_food_map = {
50:"bread",
51:"fruits",
52:"bean",
53:"egg",
54:"fish",
55:"meat",
64:"vegetables"
}

node_map = {
#tepeyecac (the bot's birth place)
"itzohcan":17,
"tecalco":4,
"tecmilco":50,
"ehuacalco":12,
"quecholac":8,
"huaxtepec":48,

#quiyauhteopan
"toliman":73,
"cualac":71,
"mitzinco":69,
"olinallan":67,
"ichcatlan":65,
"tepoztitlan":63,
"ahuatzitzinco":61,

#yohualtepec 
"cuauhtinchan":28,
"tzilacaapan":26,
"tecamachalco":33,
"huehuehtlan":35,

#teotitlan (the land of tits)
"cuayamecalco":117,
"tehuacan":220,
"tepelmeme":112,
"ajalpan":115,
#tequixtepec - node number ??
"coyotepec":142,

#chalco
"xochimilcatzinco":21,
"cuauhtlan":19,
"coacalco":55,
#xaloztoc does not make an appearence due to name conflict
#with another one in orientale

#cuauhnahuac (how the fk do you pronounce this?)
"chimalco":206,
"zacatepec":204,
"amocoztitlan":208,
"atl poyeccan":200,
"xiuhtepec":211,

#d'Acolhuahcan
"ameyalco":154,
"tenochtitlan":161,
"tizatepec":151,
"olac":166,
"xicco":168,
"matixco":156,

#occidentale
"epatlan":1,
"nopaluca":86,
"cuamantzingo":76,
"tulancingo":97,
"ixtenco":102,
"mazapa":99,
"zotoluca":174,
"sultepec":175,
"amecameca":78,

#metztitlan
"coyol":145,
"huatepango":147,
"poxtatla":140,
"ixhuatlan":136,
"acuimantla":133,
"yatipan":138,
"ixmiquilpan":128,

#cuauhtochco
"olintla":192,
"ahuilizapan":186,
"acatic":184,
"misantla":181,
"tototlan":188,

#orientale
"huiloapan":80,
"tlaxcala":217, #love this name
"ixtacuixtla":83,
"zoquiapan":92,
"huamantla":105,
"axotla":110,
"calpan":107,
"xlcotencatl":125,
}


field_map = {
"maize":1,
"bean":2,
"beans":2,
"turkey":3,
"turkeys":3,
"rabbit":4,
"rabbits":4,
"pig":5,
"pigs":5,
"peccary":5,
"peccaries":5,
"vegetables":6,
"vegetable":6,
"agave":7,
"agaves":7,
"hibiscus":9,
}


r_field_map = {
1:"maize",
2:"beans",
6:"vegetables"
}

__all__ = ["server_maintainance_start", "server_maintainance_end", "healthTable", "hungerTable", 
           "game_strings", "item_map", "hp_info", "r_food_map", "node_map", "field_map", "r_field_map"]
