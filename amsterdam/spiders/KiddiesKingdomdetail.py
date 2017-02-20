# -*- coding: utf-8 -*-
import requests
import threading
import time
import MySQLdb as mysqldb
from scrapy.selector import Selector

config = {
    'host':'127.0.0.1',
    'port':3306,
    'user':'root',
    'passwd':'nopass',
    'db':'spider',
    'charset':'utf8'
}

def parse_product(url,productid):
    url = url
    productid = productid
    conn = mysqldb.connect(**config)
    cursor = conn.cursor()
    response = requests.get(url)
    sel = Selector(response)
    info = sel.xpath('//div[@id="idTab1"]')[0].extract()
    cursor = conn.cursor()
    cursor.execute("update t_unsettled_product set info=%s where id=%s",(info,productid))
    conn.commit()
    conn.close()

if __name__ == '__main__':
    conn = mysqldb.connect(**config)
    cursor = conn.cursor()
    cursor.execute('select id,url,info,category,targetID,mainpicture,pictures,lpictures from t_unsettled_product order by id limit 50;')
    while True:
        results = cursor.fetchmany(5)
        if not results:
            break
        threads = []
        for result in results:
            productid = result[0]
            url = result[1]
            t = threading.Thread(target=parse_product, args=(url,productid,))
            threads.append(t)
            t.start()
