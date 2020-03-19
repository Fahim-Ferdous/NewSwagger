""" Aggregate The Daily Star for seuptitious purposes"""
# -*- coding: utf-8 -*-
import datetime
import logging
from urllib.parse import parse_qsl
from collections import defaultdict

import scrapy
from scrapy import Request


class ThedailystarSpider(scrapy.Spider):
    """ Right now:
            Parse only the /newspaper path with current date.
    """
    name = 'thedailystar'
    allowed_domains = ['thedailystar.net']
    start_urls = []

    progress_dict = defaultdict(int)
    lastdate = datetime.date(2019, 1, 1)
    datelimit = datetime.date.today()
    totaldays = None
    done = 0

    def start_requests(self):
        filename = 'lastdate.txt'
        try:
            with open(filename) as datefile:
                self.lastdate = datetime.datetime.\
                        strptime(datefile.read().strip(), '%Y-%m-%d').\
                        date()
        except FileNotFoundError:
            self.log(f'File <{filename}> was not found', logging.WARNING)

        self.totaldays = (self.datelimit - self.lastdate).days
        # TODO: Make lastdate more accurate by
        # updating it only after parsing whole day.
        try:
            while self.lastdate <= self.datelimit:
                yield Request(
                    'http://thedailystar.net/newspaper?date=' +
                    str(self.lastdate),
                    self.parse,
                )
                self.lastdate += datetime.timedelta(days=1)
        finally:
            with open(filename, 'w') as datefile:
                print(str(self.lastdate), file=datefile)

    def parse(self, response):
        date = None
        try:
            date = parse_qsl(response.request.url)[0][1]
        except IndexError:
            date = str(datetime.date.today())

        for pane in response.css('.pane-news-col'):
            page = pane.css('h2::text').extract_first()
            for anchor in pane.css('h5 > a'):
                self.progress_dict[date] += 1
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
        try:
            author = response.css('a[href^=\\/author]')
            smallText = response.\
                css('.small-text > meta[itemprop]::attr(content)').\
                extract()
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
            item = {
                'authors': author,
                'paperPage': parentPage,
                'published': smallText[0],
                'modified': smallText[1],
                'body': response.css('.field-body p::text').extract(),
            }

        except IndexError:
            try:
                item = next(self.parseInFocusArticle(response, parentPage))
            except StopIteration:
                pass

        date = item['published'].split('T')[0]
        self.progress_dict[date] -= 1

        if not self.progress_dict[date]:
            days = self.totaldays
            self.done += 1

            progress = round(self.done / self.totaldays * 100, 2)
            self.log(
                f'Completed date: {date} ({progress}% {self.done} of {days})',
                logging.INFO,
            )
            del self.progress_dict[date]

        item['title'] = title
        item['published'] = datetime.datetime.fromisoformat(item['published'])
        item['modified'] = datetime.datetime.fromisoformat(item['modified'])
        item['body'] = '\n\n'.join(item['body']).strip()
        yield item

    def parseInFocusArticle(self, response, parentPage):
        meta = response.css('meta[property^=article]::attr(content)').extract()
        author = response.css('p[class=author] > a')
        yield {
            'authors': list(zip(
                author.css('::text').extract(),
                author.css('::attr(href)').extract(),
            )),
            'paperPage': parentPage,
            'published': meta[0],
            'modified': meta[1],
            'body': response.css('div .description p::text').extract(),
        }
