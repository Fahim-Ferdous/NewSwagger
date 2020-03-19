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
from .models import PaperPage, Article, Author, author_articles


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

    def process_item(self, item, _):
        item['paperPage_id'] = self.getPaperPageID(item['paperPage'])
        authors = [Author(i[0].strip(), i[1]) for i in item['authors']]
        del item['paperPage'], item['authors']

        article = Article(**item)
        self.session.add(article)
        self.session.commit()
        for author in authors:
            try:
                article.authors.append(author)
                self.session.commit()
            except SQLAlchemyError:
                self.session.rollback()
