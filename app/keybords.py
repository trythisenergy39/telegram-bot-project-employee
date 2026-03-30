from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
import aiogram.types
from config import config
from urllib.parse import quote
from aiogram.utils.keyboard import InlineKeyboardBuilder

choose_role =InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text='Работодатель', callback_data='employer')],
[InlineKeyboardButton(text='Исполнитель', callback_data='worker')]])

choose_status = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text='Выбрать статус?', callback_data='status')]
                                                      ])

goto_choose_product = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text='Выбрать продукт?', callback_data='employer_choose_product')]])


employer_product = InlineKeyboardMarkup(inline_keyboard= [[InlineKeyboardButton(text='Услуга №1', callback_data='empl_Product_1')],
                                                          [InlineKeyboardButton(text='Услуга №2', callback_data='empl_Product_2')]
                                                          ])
prodlit_date = InlineKeyboardMarkup(inline_keyboard= [[InlineKeyboardButton(text='Да', callback_data='prodlit_date_two')],
                                                          [InlineKeyboardButton(text='Нет', callback_data='prodlit')]
                                                          ])
prodlit_accept = InlineKeyboardMarkup(inline_keyboard= [[InlineKeyboardButton(text='Да', callback_data='prodlit_accept_two')],
                                                          [InlineKeyboardButton(text='Нет', callback_data='prodlit')]
                                                          ])

employer_choose_posting_cost = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="Перейти к выбору объявления?", callback_data="employer_choose_posting_cost")]])

emp_by_prod = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="Купить по количеству просмотров 200", callback_data='empl_view_value')],
                                                    [InlineKeyboardButton(text="Купить по дате", callback_data='empl_time_value')]
                                                    ])

empl_goto_posting_accept = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="Перейти к созданию объявления", callback_data='create_posting_accept_')]])

empl_goto_posting_date = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="Перейти к созданию объявления", callback_data='create_posting_date_')]])

empl_goto_cash = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="Пополнить счёт", callback_data='employer_choose_product')]])

empl_lk=InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text='Выбор статуса', callback_data='status')],
                                              [InlineKeyboardButton(text='Объявления INFO', callback_data='postings_info')],
                                              [InlineKeyboardButton(text='Cлужба поддержки', callback_data='help')],
                                              [InlineKeyboardButton(text='Продлить объявление', callback_data='prodlit')]
                                              ])


def empl_publication_accept(posting_id: int) -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text='Опубликовать', callback_data=f'publication_posting_accept_{posting_id}')],
                                                                [InlineKeyboardButton(text='Удалить', callback_data=f'delete_posting_accept_{posting_id}')],
                                                                [InlineKeyboardButton(text='Редактировать', callback_data=f'edit_posting_accept_{posting_id}')]
                                                                ])
    return keyboard

def empl_publication_date(posting_id: int) -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text='Опубликовать', callback_data=f'publication_posting_date_{posting_id}')],
                                                                [InlineKeyboardButton(text='Удалить', callback_data=f'delete_posting_date_{posting_id}')],
                                                                [InlineKeyboardButton(text='Редактировать', callback_data=f'edit_posting_date_{posting_id}')]
                                                                ])
    return keyboard

def empl_get_product_keyboard(clbk: int, user_id: int) -> InlineKeyboardMarkup:
    text = f"Хочу купить Продукт №{clbk}, номер счёта для пополнения: {user_id}"
    encoded_text = quote(text)
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(
            text="Связаться с нами",
            url=f"https://t.me/{config.ADMIN_USERNAME}?text={encoded_text}"
        )]
    ])
    return keyboard

def help() -> InlineKeyboardMarkup:
    text = f"У меня возникла проблема с "
    encoded_text = quote(text)
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(
            text="Поддержка",
            url=f"https://t.me/{config.ADMIN_USERNAME}?text={encoded_text}"
        )]
    ])
    return keyboard

def employerschoosebuy_1(fcost: int, life_time_accept: int) -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text='Да', callback_data=f'empl_view_value_buy_{fcost}_{life_time_accept}')],
                                                     [InlineKeyboardButton(text='Нет', callback_data='employer_choose_posting_cost')]
                                                     ])
    return keyboard
def employerschoosebuy_2(fcost: int, life_time_accept: int) -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text='Да', callback_data=f'empl_date_value_buy_{fcost}_{life_time_accept}')],
                                                     [InlineKeyboardButton(text='Нет', callback_data='employer_choose_posting_cost')]
                                                     ])
    return keyboard

async def postings_id_a(posting_ids: list[int]):
    keyboard = InlineKeyboardBuilder()
    for posting_id in posting_ids:
        keyboard.add(InlineKeyboardButton(text=str(posting_id), callback_data=f'create_posting_accept_{posting_id}'))
    return keyboard.adjust(1).as_markup()

async def postings_id_d(posting_ids: list[int]):
    keyboard = InlineKeyboardBuilder()
    for posting_id in posting_ids:
        keyboard.add(InlineKeyboardButton(text=str(posting_id), callback_data=f'create_posting_date_{posting_id}'))
    return keyboard.adjust(1).as_markup()

async def postings_id_c(posting_ids: list[int]):
    keyboard = InlineKeyboardBuilder()
    for posting_id in posting_ids:
        keyboard.add(InlineKeyboardButton(text=str(posting_id), callback_data=f'prodlit_posting_accept_{posting_id}'))
    return keyboard.adjust(1).as_markup()

async def postings_id_e(posting_ids: list[int]):
    keyboard = InlineKeyboardBuilder()
    for posting_id in posting_ids:
        keyboard.add(InlineKeyboardButton(text=str(posting_id), callback_data=f'prodlit_posting_date_{posting_id}'))
    return keyboard.adjust(1).as_markup()