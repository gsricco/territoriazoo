import os
from dotenv import load_dotenv
from decimal import *
import requests
load_dotenv()

my_chat_id = os.getenv('CHAT_ID')
TOKEN = os.getenv('BOT_TOKEN')
URL = 'https://api.telegram.org/bot'
URLMETHOD = '/sendMessage'


# @app.task(ignore_result=True)
def send_order_bot(data):
    text_items = f""
    for item in data['items']:
        warning = ''
        if Decimal(item['quantity']) >= Decimal(item['stock_balance']):
            warning = '⚠️'
        text_items += f"🐤 Товар:\n" \
                      f"— Артикул:{item.get('article_number')},\n" \
                      f"— Кол-во: {item['quantity']},\n" \
                      f"— Остаток на складе: {item['stock_balance']}{warning},\n" \
                      f"— Цена: **{item['price']}**\n"
    text = f"📍Новый Заказ\n" \
           f"{data['customer'].get('customer_name')} {data['customer'].get('phone_number')}\n" \
           f"💴На сумму: {data.get('total_with_discount')},\n❗️скидка: {Decimal(data.get('total_no_discount')) - Decimal(data.get('total_with_discount'))}\n"
    requests.post(url=URL + TOKEN + URLMETHOD,
                  data={'chat_id': my_chat_id,
                        'text': f'{text + text_items}',
                        'parse_mode': 'markdown'}, json=True)


def call_back_bot(data):
    text = f"📞Новая заявка на консультацию!!!\n" \
           f"{data['customer_name']}, {data['phone_number']}"
    requests.post(url=URL + TOKEN + URLMETHOD,
                  data={'chat_id': my_chat_id,
                        'text': f'{text}',
                        'parse_mode': 'markdown'}, json=True)


def bot_comment(data):
    requests.post(url=URL + TOKEN + URLMETHOD,
                  data={'chat_id': my_chat_id,
                        'text': f'💬Добавлен новый комментарий,\n'
                                f'просмотреть можно в административной панеле сайта',
                        'parse_mode': 'markdown'}, json=True)


def basket_counter(items, discount_by_day):
    getcontext().prec = 6
    total_with_discount = Decimal('0')
    total_no_discount = Decimal('0')
    for item in items:
        discounts = [item['max_discount'], item['chosen_option']['discount_by_option']]
        discounts_list = [x for x in discounts if x is not None]
        if discounts_list:
            max_discount = max(discounts_list)
            if item['chosen_option']['partial']:
                item_quantity = item['chosen_option']['quantity'] / 1000
            else:
                item_quantity = item['chosen_option']['quantity']
            price_with_discount = (Decimal(item['chosen_option']['price']) * Decimal((100 - max_discount) / 100))
            total_with_discount += price_with_discount.quantize(Decimal("1.00"), ROUND_HALF_UP) * item_quantity
        else:
            if item['chosen_option']['partial']:
                item_quantity = item['chosen_option']['quantity'] / 1000
            else:
                item_quantity = item['chosen_option']['quantity']
            total_no_discount += Decimal(item['chosen_option']['price']) * Decimal(item_quantity)
    if len(discount_by_day) > 0:
        for discount in discount_by_day[0]['options']:
            if total_no_discount >= discount['min_price_for_discount']:
                total_no_discount = (Decimal(total_no_discount) * Decimal((100 - discount['discount_amount']) / 100)) \
                    .quantize(Decimal("1.00"), ROUND_HALF_UP)
                break
    final_sum = total_no_discount + total_with_discount
    return final_sum
