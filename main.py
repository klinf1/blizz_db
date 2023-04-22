import os
import sqlite3
from dotenv import load_dotenv
import time
import asyncio


import blizz_api
import item_list
import item_prices
import logs


load_dotenv()

client = os.getenv('WOW_TOKEN')
secret = os.getenv('WOW_SECRET')
api_client = blizz_api.BlizzardApi(client, secret)


def get_data():
    commodities = api_client.wow.game_data.get_commodity_auctions(
        'eu', 'en_US'
    )
    return commodities.get('auctions')


def get_connection():
    con = sqlite3.connect('item_history.db', isolation_level=None)
    con.execute('pragma journal_mode=wal;')
    cur = con.cursor()
    return con, cur


def populate_item_list():
    commodities = get_data()
    item_list.get_item_list_table()
    items_checked = []
    con, cur = get_connection()
    logger = logs.set_up_logger('item_list_logger', 'item_list_log.log')
    existing_ids = [id[0] for id in cur.execute('SELECT id FROM item_list')]
    for commodity in commodities:
        item_id = commodity.get('item').get('id')
        if item_id not in items_checked and item_id not in existing_ids:
            items_checked.append(item_id)
            try:
                item_name, item_type = item_list.get_item_data(item_id, logger)
                logger.info(f'data for {item_id}: {item_name}, {item_type}')
            except Exception as e:
                logger.error(e)
            if item_name is not None:
                item_list.insert_into_item_list(item_id, item_name, item_type)
    con.close()


async def hourly_check(logger):
    while True:
        logger.info('hourly start')
        time_start = time.time()
        con, cur = get_connection()
        id_list = [id[0] for id in cur.execute('SELECT id FROM item_list')]
        new_list = []
        existing_tables = [name[0] for name in cur.execute("SELECT name FROM sqlite_master WHERE type='table';")]
        comm = get_data()
        for c in comm:
            id = c.get('item').get('id')
            new_list.append(id)
        for item in id_list:
            if item not in new_list:
                try:
                    item_name, item_type = item_list.get_item_data(item, logger)
                except Exception as e:
                    logger.error(e)
                if item_name is not None:
                    item_list.insert_into_item_list(item, item_name, item_type)
                if str(item) not in existing_tables:
                    query = 'CREATE TABLE if NOT EXISTS {} (id INTEGER, lowest_price INTEGER, amount_on_sale INTEGER, time TEXT)'.format(f'[{item}]')
                    cur.execute(query)
                    con.commit()
        logger.info('check for new items done')
        logger.info('start populating price tables')
        item_prices.get_price_data_and_populate(logger)
        time_end = time.time()
        sleep_time = (3600 - (time_end - time_start))
        con.close()
        logger.info('hourly sleep')
        await asyncio.sleep(sleep_time)


async def main(logger):
    logger.info('started first item_list')
    populate_item_list()
    logger.info('started first tables')
    item_prices.get_tables()
    while True:
        await hourly_check(logger)


if __name__ == '__main__':
    main_logger = logs.set_up_logger('main_logger', 'main_logger.log')
    asyncio.run(main(main_logger))
