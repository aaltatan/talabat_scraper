import json

import scrapy
from scrapy.http import Response, Request


class RestaurantsSpider(scrapy.Spider):
    name = "restaurants"
    allowed_domains = ["www.talabat.com"]
    country = "oman"

    def start_requests(self):
        yield Request(
            url=f"https://www.talabat.com/{self.country}/restaurants"
        )

    def parse(self, res: Response):
        response: scrapy.Selector = res.copy()
        next_data = response.css('#__NEXT_DATA__::text').get('')
        data: dict = json.loads(next_data)
        restaurants = data['props']['pageProps']['restaurants']
        for rest in restaurants:
            yield Request(
                url=f'https://www.talabat.com/{self.country}/{rest["slug"]}',
                callback=self.parse_id,
                cb_kwargs={'id': rest['id']}
            )

    def parse_id(self, res: Response, id: str):
        response: scrapy.Selector = res.copy()
        next_data = response.css('#__NEXT_DATA__::text').get('')
        data: dict = json.loads(next_data)
        restaurant = json.dumps(data['props']['pageProps']['data'])
        
        yield Request(
            url=f'https://www.talabat.com/nextApi/v1/restaurant/{id}/reviews',
            callback=self.parse_restaurant,
            cb_kwargs={'restaurant': restaurant}
        )
        
    def parse_restaurant(self, res: Response, restaurant: str):
        response: dict = json.loads(res.text)
        
        reviews: list[dict] = response['result']
        restaurant: dict = json.loads(restaurant)
        
        yield {
            **restaurant,
            'reviews': reviews,
        }
        