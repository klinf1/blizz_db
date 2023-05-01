import main


def get_item_list_table():
    con, cur = main.get_connection()
    cur.execute('''CREATE TABLE if NOT EXISTS item_list
                   (id INTEGER,
                   name TEXT,
                   class TEXT,
                   subclass TEXT,
                   description TEXT,
                   UNIQUE(id))
    ''')
    con.commit()
    con.close()


def get_item_data(id, logger):
    item = main.api_client.wow.game_data.get_item('eu', 'en_US', id)
    to_return = [None, None, None, None]
    name = item.get('name')
    item_class = item.get('item_class').get('name')
    item_subclass = item.get('item_subclass').get('name')
    description = item.get('description')
    if not name:
        logger.error(f'could not find information on {id}')
        return to_return
    if name:
        to_return[0] = name
    if item_class:
        to_return[1] = item_class
    if item_subclass:
        to_return[2] = item_subclass
    if description:
        to_return[3] = description
    return to_return


def insert_into_item_list(id, name, type, subclass, desc):
    to_insert = (id, name, type, subclass, desc)
    con, cur = main.get_connection()
    cur.execute(
        '''INSERT OR IGNORE INTO item_list (id,name,class,subclass,description) VALUES (?,?,?,?,?)''',
        to_insert
    )
    con.commit()
    con.close()
