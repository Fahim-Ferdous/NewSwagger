""" Aggregate The Daily Star for seuptitious purposes"""
# -*- coding: utf-8 -*-
import datetime
import logging

import scrapy
from scrapy import Request


class ThedailystarSpider(scrapy.Spider):
    """ Right now:
            Parse only the /newspaper path with current date.
    """
    name = 'thedailystar'
    allowed_domains = ['thedailystar.net']
    start_urls = []

    def start_requests(self):
        filename = 'lastdate.txt'
        lastdate = datetime.date(2019, 1, 1)
        try:
            with open(filename) as datefile:
                lastdate = datetime.datetime.\
                        strptime(datefile.read().strip(), '%Y-%m-%d').\
                        date()
        except FileNotFoundError:
            self.log(f'File <{filename}> was not found', logging.WARNING)

        # TODO: Make lastdate more accurate by
        # updating it only after parsing whole day.
        try:
            while lastdate <= datetime.date.today():
                yield Request(
                    'http://thedailystar.net/newspaper?date='+str(lastdate),
                    self.parse,
                )
                lastdate += datetime.timedelta(days=1)
        finally:
            with open(filename, 'w') as datefile:
                print(str(lastdate), file=datefile)

    def parse(self, response):
        for pane in response.css('.pane-news-col'):
            page = pane.css('h2::text').extract_first()
            for anchor in pane.css('h5 > a'):
                yield response.follow(
                    anchor.attrib['href'],
                    callback=self.parseArticle,
                    cb_kwargs={
                        'parentPage': page,
                        'title': anchor.css('::text').get(),
                        'parentURL': response.request.url,
                    }
                )

    def parseArticle(self, response, parentURL, title, parentPage):
        smallText = response.\
                css('.small-text > meta[itemprop]::attr(content)').\
                extract()

        try:
            author = response.css('a[href^=\\/author]')
            if author:
                author = list(zip(
                    author.css('::text').extract(),
                    author.css('::attr(href)').extract()
                ))
            else:
                author = [(
                    response.css('span[itemprop=name]::text')[-1].get(),
                    None,
                )]
            yield {
                'title': title,
                'authors': author,
                'paperPage': parentPage,
                'published': datetime.datetime.fromisoformat(smallText[0]),
                'modified': datetime.datetime.fromisoformat(smallText[1]),
                'body': '\n\n'.join(
                    response.css('.field-body p::text').extract(),
                ).strip(),
            }

        except IndexError:
            try:
                yield next(self.parseInFocusArticle(response, title,
                                                    parentURL, parentPage))
            except StopIteration:
                self.log(response.request.url+' >>>> '+parentURL,
                         logging.WARNING)

    def parseInFocusArticle(self, response, title, parentURL, parentPage):
        meta = response.css('meta[property^=article]::attr(content)').extract()
        author = response.css('p[class=author] > a')
        yield {
            'title': title,
            'authors': list(zip(
                author.css('::text').extract(),
                author.css('::attr(href)').extract(),
            )),
            'paperPage': parentPage,
            'published': datetime.datetime.fromisoformat(meta[0]),
            'modified': datetime.datetime.fromisoformat(meta[1]),
            'body': '\n\n'.join(
                response.css('div .description p::text').extract(),
            ).strip(),
        }
