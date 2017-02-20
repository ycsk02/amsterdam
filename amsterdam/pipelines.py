# -*- coding: utf-8 -*-
from amsterdam.database.connection import db,es
from amsterdam.database.models import Product,TProduct
from sqlalchemy.orm.exc import NoResultFound
import logging
import scrapy
from scrapy.pipelines.images import ImagesPipeline
from amsterdam import settings

from qiniu import Auth
from qiniu import put_file
from PIL import Image
import mimetypes
from os.path import basename
import requests

# access_key='YIEn4E6nMpVI8ijzZeKad945PsLZeyudrXtyWZGu'
# secret_key='mVOQ6dXpyVCVTQ2wRgZyeoOkEogs6vTc2PtjNZTI'
access_key = settings.ACCESS_KEY
secret_key = settings.SECRET_KEY

class AddElasticsearchPipeline(object):
    def process_item(self,item,spider):
        #doc = {k:item[k] for k in item.keys() - {'mainPicture','lpictures','updatedTimeBeforeLast','size','color',}}
        try:
            obj = db.query(TProduct).filter(TProduct.targetId == item['id']).one()
            settledId = obj.id
        except NoResultFound:
            settledId = ''
        doc = {'id':item['id'],'name':item['name'],'info':item['info'],'category':item['category'],'domain':item['domain'],'price':item['price'],'oldprice':item['oldprice'],
                'currency':item['currency'],'url':item['url'],'brand':item['brand'],'pictures':item['pictures'],'createdTime':item['createdTime'],'lastUpdatedTime':item['lastUpdatedTime'],
                'settledId':settledId}
        #logging.log(logging.WARNING, "This ES record value is: %s"%(doc))
        es.index(index='production-products',doc_type='products',id=item['id'],body=dict(doc))
        #es.indices.refresh(index="production-products")
        #es.update(index='production-products',doc_type='products',id=1,body={"doc":{"price":12}})
        return item

class UpdatePricePipeline(object):
    def process_item(self,item,spider):
        try:
            obj = db.query(TProduct).filter(TProduct.targetId == item['id']).one()
            online = True
        except NoResultFound:
            online = False
        if online:
            if obj.price != str(item['price']):
                #logging.log(logging.WARNING, "This DB record value is: %s %s"%(item['price'],obj.price))
                setattr(obj,'price',item['price'])
                setattr(obj,'oldprice',item['oldprice'])
                db.commit()
                if obj.pid:
                    priceurl = settings.UPDATEPRICEURL+obj.pid+"?price="+str(item['price'])+"&old_price="+str(item['oldprice'])
                    try:
                        requests.get(priceurl,timeout=5)
                        logging.log(logging.WARNING, "This product update online price: %s"%priceurl)
                    except:
                        logging.log(logging.ERROR, "This product update online price failed: %s"%item['url'])
        return item

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
                if obj.price != item['price']:
                    setattr(obj,'price',item['price'])
                    setattr(obj,'oldprice',item['oldprice'])
                    # setattr(obj,'mainPicture',item['mainPicture'])
                    # setattr(obj,'lpictures',item['lpictures'])
                setattr(obj,'lastUpdatedTime',item['lastUpdatedTime'])
                setattr(obj,'updatedTimeBeforeLast','1')
                db.commit()
                item['id'] = obj.id
                item['createdTime'] = obj.createdTime
                #logging.log(logging.WARNING, "This DB record value is: %s %s"%(item['id'],obj.id))
            except:
                db.rollback()
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
                            lpictures= item['lpictures'],
                            updatedTimeBeforeLast='0')
            try:
                db.add(record)
                db.commit()
                item['id'] = record.id
                #logging.log(logging.WARNING, "This DB record value is: %s"%record.id)
            except:
                db.rollback()
        return item

class MyImagePipeline(ImagesPipeline):
    def get_media_requests(self, item, info):
        try:
            obj = db.query(Product).filter(Product.targetId == item['targetId']).one()
        except NoResultFound:
            created = True
            for image_url in item['image_urls']:
                yield scrapy.Request(image_url)

    def image_thumbs(self,image_file):
        for image in image_file:
            filename=basename(image)
            ofilename=filename.split('.')[0]
            sfilename=ofilename+'_s'
            dfilename=ofilename+'_d'
            mimetypes.init()
            mime,x = mimetypes.guess_type('/images'+image)
            im = Image.open('/images/'+image)
            im.thumbnail((210,235))
            im.save('/images/full/'+sfilename,format=im.format)
            im = Image.open('/images/'+image)
            im.thumbnail((450,450))
            im.save('/images/full/'+dfilename,format=im.format)
            qiniu_connect = Auth(access_key,secret_key)
            token = qiniu_connect.upload_token('public')
            ret,info = put_file(token,ofilename,'/images/'+image,mime_type=mime,check_crc=True)
            ret,info = put_file(token,sfilename,'/images/full/'+sfilename,mime_type=mime,check_crc=True)
            ret,info = put_file(token,dfilename,'/images/full/'+dfilename,mime_type=mime,check_crc=True)

    def item_completed(self, results, item, info):
        image_paths = [x['path'] for ok, x in results if ok]
        image_checksum = [x['checksum'] for ok, x in results if ok]
        if image_paths:
            #item['lpictures'] = ",".join(image_checksum)
            item['lpictures'] = ",".join([ basename(x).split('.')[0] for x in image_paths ])
            item['mainPicture'] = basename(image_paths[0]).split('.')[0]
            # logging.log(logging.WARNING, "This image_checksum value is: %s"%image_checksum)
            # logging.log(logging.WARNING, "This image_paths value is: %s"%image_paths)
            self.image_thumbs(image_paths)
        return item
