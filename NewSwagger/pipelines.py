# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

from scrapy.exceptions import DropItem

from .models import Base
from .models import PaperPage, Article


class PaperPagePipeline(object):
    def __init__(self, uri):
        engine = create_engine(uri, echo=True)
        Session = sessionmaker()
        Session.configure(bind=engine)
        Base.metadata.create_all(engine)
        self.session = Session()

    @classmethod
    def from_crawler(cls, crawler):
        return cls(
            uri=crawler.settings.get('DBURI'),
        )

    def close_spider(self, spider):
        try:
            self.session.commit()
        except:
            self.session.rollback()
        finally:
            self.session.close()

    def process_item(self, item, spider):
        cls = None
        if item.get('paperPage'):
            cls = PaperPage
        elif item.get('title'):
            cls = Article

        if cls:
            self.session.add(cls(**item))
        else:
            DropItem(f'Unimplemented item {item}')
        return item
