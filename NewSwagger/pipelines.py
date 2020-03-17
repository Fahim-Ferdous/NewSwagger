# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import SQLAlchemyError

from scrapy.exceptions import DropItem

from .models import Base
from .models import PaperPage, Article


class PaperPagePipeline(object):
    def __init__(self, uri):
        engine = create_engine(uri)
        Session = sessionmaker()
        Session.configure(bind=engine)
        Base.metadata.create_all(engine)
        self.session = Session()

        self.paperPageIDs = {}

    @classmethod
    def from_crawler(cls, crawler):
        return cls(
            uri=crawler.settings.get('DBURI'),
        )

    def close_spider(self, spider):
        try:
            self.session.commit()
        except SQLAlchemyError:
            self.session.rollback()
        finally:
            self.session.close()

    def queryPaperPageID(self, paperPage):
        return self.session.query(PaperPage).\
            filter(PaperPage.paperPage == paperPage).\
            with_entities(PaperPage.id).first()

    def getPaperPageID(self, paperPage):
        id_ = self.paperPageIDs.get(paperPage)
        if id_ is None:
            row = self.queryPaperPageID(paperPage)
            if row is None:
                self.session.add(PaperPage(paperPage=paperPage))
            row = self.queryPaperPageID(paperPage)

            id_ = row[0]
            self.paperPageIDs[paperPage] = id_

        return id_

    # TODO: Add authors
    def process_item(self, item, _):
        cls = None
        if item.get('title'):
            cls = Article
            item['paperPage_id'] = self.getPaperPageID(item['paperPage'])
            del item['paperPage']

        if cls:
            self.session.add(cls(**item))
        else:
            DropItem(f'Unimplemented item {item}')
        return item
