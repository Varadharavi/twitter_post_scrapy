import os

import scrapy
import tweepy
from scrapy.utils.project import get_project_settings


class QuotesSpider(scrapy.Spider):
    name = "quotes"
    start_urls = [
        'https://www.moneycontrol.com/corporate-calendar',
    ]

    def __init__(self, *args, **kwargs):
        super(QuotesSpider, self).__init__(*args, **kwargs)
        self.settings = get_project_settings()
        self.access_key = self.settings.get('ACCESS_KEY')
        self.access_secret = self.settings.get('ACCESS_SECRET')
        self.consumer_key = self.settings.get('CONSUMER_KEY')
        self.consumer_secret = self.settings.get('CONSUMER_SECRET')
        self.bearer_token = self.settings.get('BEARER_TOKEN')

        print(self.access_key)
        if not all([self.access_key, self.access_secret, self.consumer_key, self.consumer_secret, self.bearer_token]):
            raise ValueError("One or more Twitter API environment variables are not set")


    def parse(self, response):
        print(self.access_key)
        table = response.css('tbody#All-table-body')
        rows = table.css('tr')
        count = 0
        twitter_post_data = []
        for row in rows:
            data_text = row.css('td a::text').get()
            cells = row.css('td::text').getall()
            if data_text and len(cells) > 3 and "-" not in cells[3].strip():
                count += 1
                twitter_post_data.append({
                    "stock_name": data_text.replace(" ", ""),
                    "event_type": cells[0].strip() if len(cells) > 0 else None,
                    "announced_date": cells[1].strip() if len(cells) > 1 else None,
                    "ex_date": cells[2].strip() if len(cells) > 2 else None,
                    "dividend": cells[3].strip() if len(cells) > 3 else None
                })

            if count >= 5:
                break

        post_content = "\U0001F6A8 Dividend Update !!!\n\n"
        total_chars = len(post_content)
        for post in twitter_post_data:
            test = (f"#{post['stock_name']} ({post['event_type'].replace('Dividend - ', '')}) - "
                    f"{post['ex_date']}(ex-date) - Rs.{post['dividend']}\n")
            if total_chars + len(test) <= 280:
                post_content += test
                total_chars += len(test)
            else:
                break
        self.post_on_twitter(post_content.strip())

    def post_on_twitter(self, tweet):
        print(self.access_key)
        newapi = tweepy.Client(
            bearer_token=self.bearer_token,
            access_token=self.access_key,
            access_token_secret=self.access_secret,
            consumer_key=self.consumer_key,
            consumer_secret=self.consumer_secret,
        )

        try:
            post_result = newapi.create_tweet(text=tweet)
            print(post_result)
        except tweepy.TweepyException as error:
            print(f"Error: {error}")

# To run this Scrapy spider, save the code in a file (e.g., quotes_spider.py) and execute:
# scrapy runspider quotes_spider.py
