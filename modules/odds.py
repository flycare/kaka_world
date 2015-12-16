
from config.search_config import *



def getItemByArea(area):
    import random
    area_config=SEARCH_CONFIG[area]

    table=getRelativeOddsTable(area)
    table_id=random.choice(table)
    items= area_config[table_id]['value']
    num =   area_config[table_id]['num']
    return random.choice(items),num

def getItemByAreaForTreasure(area):
    import random
    area_config=TREASURE_CONFIG[area]

    table=getRelativeOddsTable(area)
    table_id=random.choice(table)
    items= area_config[table_id]['value']
    num =   area_config[table_id]['num']
    return random.choice(items),num

def getRelativeOddsTable(area_id):
    key=str(area_id)+'_table'
    if SEARCH_CONFIG.has_key(key):
        return SEARCH_CONFIG[key]
    else:
        items = SEARCH_CONFIG[area_id]
        sequence = []
        relative_odds = []
        for i in range(len(items)):
            sequence.append(i)
            relative_odds.append(items[i]['relative_odds'])
        #print 'sequence--------------',sequence
        #print 'relative_odds--------------',relative_odds
        table = [ z for x, y in zip(sequence, relative_odds) for z in [x]*y ]
        #print 'table--------------',table
        SEARCH_CONFIG[key]=table
        return table
    
    
