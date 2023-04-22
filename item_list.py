import main


def get_item_list_table():
    con, cur = main.get_connection()
    cur.execute('''CREATE TABLE if NOT EXISTS item_list
                   (id INTEGER,
                   name TEXT,
                   type TEXT,
                   UNIQUE(id))
    ''')
    con.commit()
    con.close()


def get_item_data(id, logger):
    item = main.api_client.wow.game_data.get_item('eu', 'en_US', id)
    item_name = item.get('name')
    if item_name is None:
        logger.error(f'could not get info on {id} {item}')
        return (None, None)
    item_class = item.get('item_class')
    if item_class is None:
        return item_name, 'None'
    item_type = item_class.get('name')
    if item_type is None:
        return item_name, 'None'
    return item_name, item_type


def insert_into_item_list(id, name, type):
    to_insert = (id, name, type)
    con, cur = main.get_connection()
    cur.execute(
        '''INSERT OR IGNORE INTO item_list (id,name,type) VALUES (?,?,?)''',
        to_insert
    )
    con.commit()
    con.close()
