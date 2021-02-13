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

        for news_link in response.xpath("//a[@class='post__title_link']/@href").getall():
            yield Request(news_link, callback=self.parse_main)

        next_page = response.css('a.arrows-pagination__item-link_next::attr(href)')
        if len(next_page) > 0:
            yield Request('https://habr.com' + next_page[0].root.strip(),
                          callback=self.parse)

    def parse_main(self, response):

        news_id = response.css('article.post_full')[0].attrib['id']
        title = response.css('span.post__title-text::text')[0].root.strip()

        hubs = []
        for hubs_i in response.css('a.inline-list__item-link::text'):
            hubs.append(hubs_i.root.strip())

        tags = []
        for tags_i in response.css('ul.js-post-tags').css('a.post__tag::text'):
            tags.append(tags_i.root.strip())

        text = []
        for text_part in response.xpath("//div[@class='post__body post__body_full']"
                                        "/descendant-or-self::*/text()").getall():
            text.append(text_part.strip())

        author = response.css('span.user-info__nickname::text')[0].root.strip()

        try:
            author_karma = response.css('a.user-info__stats-item').css('div.stacked-counter__value::text')[0].root.strip()
        except:
            author_karma = 0

        try:
            author_rating = response.css('a.stacked-counter_rating').css('div.stacked-counter__value::text')[0].root.strip()
        except:
            author_rating = 0

        try:
            author_specialization = response.css('div.user-info__specialization::text')[0].root.strip()
        except:
            author_specialization = ""

        try:
            comments_counter = response.css('span.post-stats__comments-count::text')[0].root.strip()
        except:
            comments_counter = 0

        item = HabrNews()

        item['author'] = author
        item['author_karma'] = author_karma
        item['author_rating'] = author_rating
        item['author_specialization'] = author_specialization

        item['news_id'] = news_id.replace("post_", "")
        item['title'] = title
        item['comments_counter'] = str(comments_counter).replace("&plus;","")
        item['hubs'] = hubs
        item['tags'] = tags
        item['text'] = text

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
