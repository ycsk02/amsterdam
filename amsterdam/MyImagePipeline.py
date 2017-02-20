# -*- coding: utf-8 -*-
from database.connection import db
from database.models import Product
from sqlalchemy.orm.exc import NoResultFound
import logging

class AddTablePipeline(object):
    def process_item(self, item, spider):
        created = False
        try:
            obj = db.query(Product).filter(Product.targetId == item['targetId']).one()
        except NoResultFound:
            created = True
        if not created:
            try:
                logging.log(logging.WARNING, "This product is exists in database: %s"%item['url'])
                setattr(obj,'price',item['price'])
                setattr(obj,'oldprice',item['oldprice'])
                setattr(obj,'lastUpdatedTime',item['lastUpdatedTime'])
                setattr(obj,'updatedTimeBeforeLast','1')
                db.commit()
            except:
                logging.log(logging.ERROR, "This product update database failed: %s"%item['url'])
        else:
            record = Product(name=item['name'],
                            info = item['info'],
                            category = item['category'],
                            domain=item['domain'],
                            price=item['price'],
                            oldprice=item['oldprice'],
                            currency=item['currency'],
                            url=item['url'],
                            brand=item['brand'],
                            createdTime=item['createdTime'],
                            lastUpdatedTime=item['lastUpdatedTime'],
                            color=item['color'],
                            size=item['size'],
                            targetId=item['targetId'],
                            mainPicture=item['mainPicture'],
                            pictures=item['pictures'],
                            lpictures=item['lpictures'],
                            updatedTimeBeforeLast='0')
            try:
                db.add(record)
                db.commit()
            except:
                db.rollback()
        return item
