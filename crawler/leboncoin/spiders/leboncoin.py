# -*- coding: utf-8 -*-
import scrapy


class Property(scrapy.Item):
    url = scrapy.Field()
    price = scrapy.Field()
    surface = scrapy.Field()
    type = scrapy.Field()
    rooms = scrapy.Field()
    city = scrapy.Field()
    image_urls = scrapy.Field()
    images = scrapy.Field()


class LeboncoinSpider(scrapy.Spider):
    name = 'leboncoin'
    start_urls = [
        'https://www.leboncoin.fr/ventes_immobilieres/offres/aquitaine/gironde/?ret=1&ret=2'
    ]

    def parse(self, response):
        property = Property()

        for leBonCoinProperty in response.css('section.mainList a.list_item'):
            detail_url = leBonCoinProperty.xpath('./@href').extract_first()
            property['url'] = 'https:%s' % detail_url
            yield scrapy.Request(
                url=response.urljoin(detail_url),
                callback=self.extract_meta_from_property,
                meta={'property': property}
            )

        next_page = response.css('a#next::attr(href)').extract_first()
        if next_page is not None:
            next_page = response.urljoin(next_page)
            yield scrapy.Request(next_page, callback=self.parse)

    def extract_meta_from_property(self, response):
        property = response.meta['property']
        properties = response.css('section.properties h2')
        price = properties.css('.item_price').xpath('./@content').extract_first()
        if price:
            property['price'] = int(price)
        surface = properties.xpath('.//span[.="Surface"]/following-sibling::span/text()').extract_first()
        if surface:
            property['surface'] = int(surface.lower().replace("m", "").replace(" ", "").strip())
        rooms = properties.xpath('.//span[.="Pièces"]/following-sibling::span/text()')
        if rooms:
            property['rooms'] = int(rooms.extract_first())
        property['type'] = properties.xpath('.//span[.="Type de bien"]/following-sibling::span/text()').extract_first()
        property['city'] = properties.xpath('.//span[@itemprop="address"]/text()').extract_first().strip()
        images_script = response.css('.item_photo').xpath('./following-sibling::script/text()')
        if images_script:
            images = images_script[0].re('images\[\d\]\s*=\s*"(.*?)"')
            property['image_urls'] = ['http:%s' % i for i in images]
        yield property
