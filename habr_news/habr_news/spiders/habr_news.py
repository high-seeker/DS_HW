import scrapy
from scrapy import Request
from scrapy.crawler import CrawlerProcess

class HabrNews(scrapy.Item):

    author = scrapy.Field()
    author_karma = scrapy.Field()
    author_rating = scrapy.Field()
    author_specialization = scrapy.Field()
    comments_counter = scrapy.Field()
    hubs = scrapy.Field()
    news_id = scrapy.Field()
    tags = scrapy.Field()
    text = scrapy.Field()
    title = scrapy.Field()

class HabrNewsSpider(scrapy.Spider):
    name = 'habr_news'  # spider_name
    allowed_domains = ['habr.com']
    start_urls = ['https://habr.com/ru/news/']

    def parse(self, response):
        for news in response.css('li.content-list__item_post'):

            try:
                news_id = news.attrib['id']
            except:
                continue
            if news_id == 'effect':
               continue

            title = news.css('a.post__title_link::text')[0].root.strip()
            author = news.css('span.user-info__nickname::text')[0].root.strip()

            try:
                comments_counter = news.css('span.post-stats__comments-count::text')[0].root.strip()
            except:
                comments_counter = 0

            hubs = []
            for hubs_i in news.css('a.inline-list__item-link::text'):
                hubs.append(hubs_i.root.strip())

            text_conc = ''
            for text_i in news.css('div.post__text-html').css('p::text'):
                text_conc = text_conc + text_i.root.strip()

            mainpage = response.css('a.post__habracut-btn::attr(href)')[0].root.strip()

            yield Request(mainpage, callback=self.parse_main,
                          cb_kwargs=dict(news_id=news_id,
                                         title=title,
                                         author=author,
                                         comments_counter=comments_counter,
                                         hubs=hubs,
                                         text_conc=text_conc))

        next_page = response.css('a.arrows-pagination__item-link_next::attr(href)')
        if len(next_page) > 0:
            yield Request('https://habr.com' + next_page[0].root.strip(),
                          callback=self.parse)

    def parse_main(self, response, news_id, title, author, comments_counter, hubs, text_conc):

        tags = []
        for hubs_i in response.css('ul.js-post-tags').css('a.post__tag::text'):
            tags.append(hubs_i.root.strip())

        # TO DO - Разобраться с непечатными символами!
        #text_conc = ''
        #for text_i in response.css('div.post__text_v2').css('p::text'):
        #    text_conc = text_conc + text_i.root.strip()

        author_link = response.css('a.post__user-info::attr(href)')[0].root.strip()

        yield Request(author_link, callback=self.parse_author,
                          cb_kwargs=dict(news_id=news_id,
                                         title=title,
                                         author=author,
                                         comments_counter=comments_counter,
                                         hubs=hubs,
                                         tags=tags,
                                         text_conc=text_conc))


    def parse_author(self, response, news_id, title, author, comments_counter, hubs, tags, text_conc):

        author_karma = response.css('a.user-info__stats-item').css('div.stacked-counter__value::text')[0].root.strip()
        author_rating = response.css('a.stacked-counter_rating').css('div.stacked-counter__value::text')[0].root.strip()
        author_specialization = response.css('div.user-info__specialization::text')[0].root.strip()

        item = HabrNews()

        item['author'] = author
        item['author_karma'] = author_karma
        item['author_rating'] = author_rating
        item['author_specialization'] = author_specialization

        item['news_id'] = news_id.replace("post_", "")
        item['title'] = title
        item['comments_counter'] = comments_counter
        item['hubs'] = hubs
        item['tags'] = tags
        item['text'] = text_conc

        yield item


# if __name__ == '__main__':
#     from scrapy.cmdline import execute
#
#     execute()

if __name__ == '__main__':
    process = CrawlerProcess(settings={
        "FEEDS": {
            # сохранить результаты в файлы
            "./../../habr_news.json": {"format": "json"},
            "./../../habr_news.csv": {"format": "csv"}
        },
        "LOG_LEVEL": "ERROR"        # без логов в терминале
    })

    process.crawl(HabrNewsSpider)

    # the script will block here until the crawling is finished
    process.start()
