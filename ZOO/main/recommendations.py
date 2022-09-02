import redis
from django.conf import settings

r = redis.Redis(host=settings.REDIS_HOST,
                port=settings.REDIS_PORT,
                db=settings.REDIS_DB,)


class Recommend:

    def get_product_key(self, id):
        return f'product:{id}:purchased_with'

    def products_bought(self, products):
        product_ids = [p['id'] for p in products]
        for product_id in product_ids:
            for with_id in product_ids:
                if product_id != with_id:
                    r.zincrby(self.get_product_key(product_id), 1, with_id)

    def suggest_products_for(self, product_id, max_results=12):
        name = self.get_product_key(product_id)
        suggestions = r.zrange(name, 0, -1, desc=True)[:max_results]
        suggested_products_ids = [int(id) for id in suggestions]
        return suggested_products_ids
