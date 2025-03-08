import json
import logging
import math

import scrapy
from scrapy.http import FormRequest, Request, Response

logging.basicConfig(
    filemode="a",
    filename="logger.log",
    format="[%(asctime)s] %(levelname)s | %(name)s => %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    encoding="utf-8",
    level=logging.INFO,
)


class SiteMapSpider(scrapy.Spider):
    name = "sitemap"
    allowed_domains = ["www.talabat.com"]
    country = "oman"

    def start_requests(self):
        base_url = f"https://www.talabat.com/{self.country}/sitemap"
        yield Request(base_url)

    def parse(self, res: Response):
        response: scrapy.Selector = res.copy()
        links = response.css(
            "#__next > div:nth-child(4) > div.sc-667fe0db-0.cTJMQW > div > div:nth-child(9) a::attr(href)"
        ).getall()
        for link in links:
            link_list = link.split("/")
            id = link_list[-2]
            slug = link_list[-1]
            url = f"https://www.talabat.com/_next/data/manifests/listing.json?countrySlug={self.country}&areaId={id}&areaSlug={slug}"
            yield Request(
                url=url,
                callback=self.parse_pagination,
                cb_kwargs={"id": id, "slug": slug},
            )

    def parse_pagination(self, res: Response, id: int, slug: str):
        response: dict = json.loads(res.text)

        total_vendors = int(response["pageProps"]["data"]["totalVendors"])
        pages_count = math.ceil(total_vendors / 15)

        for idx in range(1, pages_count + 1):
            params: dict = {
                "countrySlug": self.country,
                "areaId": str(id),
                "areaSlug": slug,
                "page": str(idx),
            }
            url = "https://www.talabat.com/_next/data/manifests/listing.json"
            yield FormRequest(
                url=url, method="GET", formdata=params, callback=self.parse_data
            )

    def parse_data(self, res: Response):
        response: dict = json.loads(res.text)
        vendors = response["pageProps"]["data"]["vendors"]
        for v in vendors:
            yield {
                **v,
                "url": res.url,
            }
