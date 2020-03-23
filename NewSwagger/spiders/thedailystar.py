""" Aggregate The Daily Star for seuptitious purposes"""
# -*- coding: utf-8 -*-
import logging
from urllib.parse import parse_qsl, urlsplit
from collections import defaultdict
from datetime import date, datetime, timedelta

import scrapy
from scrapy import Request
from scrapy.selector.unified import SelectorList


class ThedailystarSpider(scrapy.Spider):
    """ Right now:
            Parse only the /newspaper path with current date.
    """
    name = 'thedailystar'
    allowed_domains = ['thedailystar.net']
    start_urls = []

    progress_dict = defaultdict(int)
    lastdate = date(2019, 1, 1)
    datelimit = date.today()
    totaldays = None
    done = 0

    def start_requests(self):
        filename = 'lastdate.txt'
        try:
            with open(filename) as datefile:
                self.lastdate = datetime.\
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
                    self.parse_page,
                )
                self.lastdate += timedelta(days=1)
        finally:
            with open(filename, 'w') as datefile:
                print(str(self.lastdate), file=datefile)

    def parse(self, response):
        ''' This function is only to help when you
            run scrapy with the `parse' parameter.
        '''
        if urlsplit(response.request.url).path != '/newspaper':
            try:
                yield next(self.parse_article(response, None))
            except StopIteration:
                pass
        else:
            self.parse_page(response)

    def parse_page(self, response):
        article_date = str(date.today())
        try:
            article_date = parse_qsl(response.request.url)[0][1]
        except IndexError:
            pass

        for pane in response.css('.pane-news-col'):
            paper_page = pane.css('h2::text').get()
            for anchor in pane.css('h5 > a'):
                self.progress_dict[article_date] += 1
                yield response.follow(
                    anchor.attrib['href'],
                    callback=self.parse_article,
                    cb_kwargs={'paper_page': paper_page},
                )

    def parse_article(self, response, paper_page):
        try:
            author = response.css('a[href^=\\/author]')
            published = response.\
                css('meta[itemprop=datePublished]::attr(content)').\
                get().split('T')[0]
            if author:
                author = list(zip(
                    [i.strip() for i in author.css('::text').extract()],
                    author.css('::attr(href)').extract()
                ))
            else:
                author = [(
                    response.css('span[itemprop=name]::text')[-1].get(),
                    None,
                )]
            item = {
                'title': response.css('h1::text').get(),
                'authors': author,
                'published': published,
                'body': response.css(', '.join([
                    'h2 em::text',
                    'div .caption::text',
                    'div .field-body p::text',
                    'div .field-body p em::text',
                    'div .field-body p h2::text',
                    'div .field-body p span::text',
                    'div .field-body p strong::text',
                    'div .field-body div::text',
                    'div .field-body div span::text',
                ])).extract(),
            }

        except (IndexError, AttributeError):
            try:
                item = next(self.parse_special_article(response))
            except StopIteration:
                pass

        article_date = item['published']
        self.progress_dict[article_date] -= 1

        if not self.progress_dict[article_date]:
            self.done += 1

            progress = round(self.done / self.totaldays * 100, 2)
            self.log(
                'Completed date: {} ({}% {} of {})'.format(
                    article_date, progress, self.done, self.totaldays,
                ),
                logging.INFO,
            )
            del self.progress_dict[article_date]

        item['url'] = response.request.url
        item['published'] = datetime.fromisoformat(article_date).date()
        item['body'] = '\n'.join(item['body']).strip()
        item['paperPage'] = paper_page
        yield item

    def parse_special_article(self, response):
        ''' Parse article with dark backround.
            Example:
                https://www.thedailystar.net/in-focus/news/pandemics-changed-history-1881355
        '''

        authors = []
        selection = response.css('p.author > a')
        if selection:
            authors.extend(list(zip(
                selection.css('::text').extract(),
                selection.css('::attr(href)').extract(),
            )))

        selection = response.css('p.author::text')
        if selection:
            authors.extend(
                [
                    (i.strip(), None)
                    for i in selection.extract()
                    if i.strip() not in ['and']
                ]
            )

        yield {
            'title': response.css('h1::text').get(),
            'authors': authors,
            'published':
                response.css('meta[property^=article]::attr(content)').get(),
            'body': response.css(', '.join([
                'h2 em::text',
                'div .description p::text',
                'div .description p strong::text',
                'div .caption::text',
            ])).extract(),
        }
