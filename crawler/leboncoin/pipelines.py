from scrapy.exceptions import DropItem


class ValidPropertyPipeline(object):
    def process_item(self, item, spider):
        required_fields = ['url', 'price', 'surface', 'type', 'rooms', 'city', 'image_urls']
        if all(field in item for field in required_fields):
            return item
        else:
            raise DropItem("not an interesting leboncoin property")
