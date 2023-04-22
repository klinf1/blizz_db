import datetime
import pytz
import os
from dotenv import load_dotenv

import main
import blizz_api
import logs
load_dotenv()
client = os.getenv('WOW_TOKEN')
secret = os.getenv('WOW_SECRET')
api_client = blizz_api.BlizzardApi(client, secret)


def get_tables():
    con, cur = main.get_connection()
    logger = logs.set_up_logger('tables_logger', 'tables_log.log')
    id_list = [id[0] for id in cur.execute('SELECT id FROM item_list')]
    for id in id_list:
        item_id = f'[{id}]'
        query = 'CREATE TABLE if NOT EXISTS {} (id INTEGER, lowest_price INTEGER, amount_on_sale INTEGER, time TEXT)'.format(item_id)
        cur.execute(query)
        con.commit()
        logger.info(f'table {id} created')
    con.close()


def get_price_data_and_populate(main_logger):
    main_logger.info('get_price_data_and_populate start')
    commodities = main.get_data()
    logger = logs.set_up_logger('prices_logger', 'prices_logs.log')
    logger.info('item prices start')
    con, cur = main.get_connection()
    tables = [name[0] for name in cur.execute("SELECT name FROM sqlite_master WHERE type='table';")]
    id_list = [id[0] for id in cur.execute('SELECT id FROM item_list')]
    for id in id_list:
        total_amount = 0
        prices = {}
        for commodity in commodities:
            if commodity.get('item').get('id') == id:
                price = commodity.get('unit_price')
                quantity = commodity.get('quantity')
                prices[price] = quantity
        for value in prices.values():
            total_amount += value
        try:
            lowest_price = min(list(prices.keys()))
        except Exception as e:
            logger.error(f'failed to find price for {id} {e}')
            lowest_price = 0
        time_now = datetime.datetime.now(pytz.timezone('CET'))
        time_now = time_now.strftime("%Y-%m-%d %H:%M:%S")
        to_insert = [id, lowest_price, total_amount, time_now]
        table = f'[{id}]'
        if str(id) in tables:
            query = 'INSERT INTO {} (id, lowest_price, amount_on_sale, time) VALUES (?,?,?,?)'.format(table)
            cur.execute(query, to_insert)
            con.commit()
            logger.info(f'info for {id} inserted')
    con.close()
    logger.info('item prices done')
    main_logger.info('get_price_data_and_populate stop')
