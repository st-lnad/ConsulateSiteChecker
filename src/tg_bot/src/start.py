import codecs
import dataclasses
import http.client
import json
from enum import Enum
from json import load
import os

import telebot
from telebot import types

user_dict = {}
BOT_KEY = os.getenv("BOT_KEY")

texts_file = codecs.open('src/texts.json', 'r', 'utf-8')
texts = load(texts_file)
texts_file.close()

database_connection = http.client.HTTPConnection('localhost', 8081, timeout=10)


class ResponseCodes(Enum):
    ACCEPTED = 202
    NOT_FOUND = 404
    BAD_REQUEST = 400


@dataclasses.dataclass()
class User:
    id: str
    telegram_user_id: str
    telegram_chat_id: str
    last_name: str
    demo_requests_num: int
    tickets: list
    notification_freq: int

    def __init__(self, *args, **kwargs):
        if "json_data" in kwargs:
            json_data = kwargs.get('json_data')
            self.id = json_data['id']
            self.telegram_user_id = json_data['telegramUserId']
            self.telegram_chat_id = json_data['telegramChatId']
            self.last_name = json_data['lastName']
            self.demo_requests_num = json_data['demoRequestNumber']
            self.tickets = []
            for id_data in json_data['tickets']:
                self.tickets.append(id_data)
            self.notification_freq = json_data['notificationFrequency']

        else:
            self.id = None
            self.telegram_user_id = kwargs.get("telegram_user_id")
            self.telegram_chat_id = kwargs.get("telegram_chat_id")
            self.last_name = kwargs.get("last_name")
            self.demo_requests_num = None
            self.tickets = []
            self.notification_freq = None

    def to_json(self):
        result = "{  "
        if self.id is not None:
            result += "\"id\": \"" + self.id + "\","
        if self.telegram_user_id is not None:
            result += "\"telegramUserId\": \"" + self.telegram_user_id + "\","
        if self.telegram_chat_id is not None:
            result += "\"telegramChatId\": \"" + self.telegram_chat_id + "\","
        if self.last_name is not None:
            result += "\"lastName\": \"" + self.last_name + "\","
        if self.demo_requests_num is not None:
            result += "\"demoRequestNumber\": \"" + str(self.demo_requests_num) + "\","
        if self.tickets is not None:
            result += "\"tickets\": ["
            for data in self.tickets:
                result += "\"" + data + "\""
            result += "],"
        if self.notification_freq is not None:
            result += "\"notificationFrequency\": \"" + str(self.notification_freq) + "\","

        result = result[:-1]

        result += "} "

        return result


@dataclasses.dataclass()
class Ticket:
    id: str
    user_id: str
    country_name: str
    referral_number: str
    last_name: str
    answer_addresses: list
    creation_date: str
    delete_date: str

    def __init__(self, *args, **kwargs):
        if "json_data" in kwargs:
            json_data = kwargs.get("json_data")
            self.id = json_data['id']
            self.user_id = json_data['userId']
            self.country_name = json_data['countryName']
            self.referral_number = json_data['referralNumber']
            self.last_name = json_data['lastName']
            self.answer_addresses = []
            for address in json_data['answerAddresses']:
                self.answer_addresses.append(address)
            self.creation_date = json_data['creationDate']
            self.delete_date = json_data['deleteDate']
        else:
            self.id = None
            self.user_id = kwargs.get("user_id")
            self.country_name = kwargs.get("country_name")
            self.referral_number = kwargs.get("referral_number")
            self.last_name = None
            self.id = None
            self.answer_addresses = []
            self.creation_date = None
            self.delete_date = None

    def to_json(self):
        result = "{  "
        if self.id is not None:
            result += "\"id\": \"" + self.id + "\","
        if self.user_id is not None:
            result += "\"userId\": \"" + self.user_id + "\","
        if self.country_name is not None:
            result += "\"countryName\": \"" + self.country_name + "\","
        if self.referral_number is not None:
            result += "\"referralNumber\": \"" + self.referral_number + "\","
        if self.last_name is not None:
            result += "\"lastName\": \"" + str(self.last_name) + "\","
        if self.answer_addresses is not None:
            result += "\"answerAddresses\": ["
            for address in self.answer_addresses:
                result += "\"" + address + "\""
            result += "],"
        if self.creation_date is not None:
            result += "\"creationDate\": \"" + str(self.creation_date) + "\","
        if self.delete_date is not None:
            result += "\"deleteDate\": \"" + str(self.delete_date) + "\","

        result = result[:-1]

        result += "}"

        return result


if __name__ == '__main__':
    bot = telebot.TeleBot(BOT_KEY)


    @bot.message_handler(commands=['help', 'start', 'restart', 'menu'])
    def start(message: types.Message):
        main_menu(message.chat.id)


    @bot.callback_query_handler(func=lambda call: True)
    def handle(call):
        bot.answer_callback_query(call.id)
        bot.edit_message_reply_markup(chat_id=call.message.chat.id,
                                      message_id=call.message.id,
                                      reply_markup=types.InlineKeyboardMarkup())
        if str(call.data) == 'main_menu':
            main_menu(call.message.chat.id)
        elif str(call.data) == 'ticket_menu':
            ticket_menu(call)
        elif str(call.data) == 'pay_menu':
            pass
        elif str(call.data) == 'settings_menu':
            pass
        elif str(call.data) == 'parse':
            pass
        elif str(call.data) == 'add_data':
            request_of_last_name(call.message.chat.id)
        else:
            print("Unknown callback, ooops. Coder, where is it, idiot?")


    def main_menu(chat_id):
        markup = types.InlineKeyboardMarkup()

        button_a: types.InlineKeyboardButton
        if chat_id in user_dict or check_user_in_db(chat_id=chat_id):  # check in DB
            button_a = types.InlineKeyboardButton('Проверить', callback_data='TODO')
        else:
            button_a = types.InlineKeyboardButton('Демо режим', callback_data='demo_menu')
        button_b = types.InlineKeyboardButton('Мои документы', callback_data='ticket_menu')
        button_c = types.InlineKeyboardButton('Оплата', callback_data='pay_menu')
        button_d = types.InlineKeyboardButton('Настройки', callback_data='settings_menu')

        markup.row(button_a)
        markup.row(button_b, button_c, button_d)
        print(texts['greeting'])
        bot.send_message(chat_id, texts['greeting'], reply_markup=markup)


    def ticket_menu(call: types.CallbackQuery):
        markup = types.InlineKeyboardMarkup()

        button_a = types.InlineKeyboardButton('Список', callback_data='tickets_list')
        button_b = types.InlineKeyboardButton('Добавить', callback_data='add_ticket')
        button_c = types.InlineKeyboardButton('Редактировать', callback_data='edit_ticket')
        button_d = types.InlineKeyboardButton('Удалить комплект', callback_data='del_ticket')

        markup.row(button_a, button_b)
        markup.row(button_c, button_d)

        bot.send_message(call.message.chat.id, texts['ticket_menu'], reply_markup=markup)


    def pay_menu():
        pass


    def settings_menu(call: types.CallbackQuery):
        markup = types.InlineKeyboardMarkup()

        button_a = types.InlineKeyboardButton('Частота уведомлений', callback_data='Notification_frequency')
        markup.row(button_a)

        bot.send_message(call.message.chat.id, texts['settings_menu'], reply_markup=markup)


    def request_of_last_name(chat_id):
        msg = bot.send_message(chat_id, "Введите ваш Last Name (фамилию):")
        bot.register_next_step_handler(msg, get_last_name)


    def get_last_name(message: types.Message):
        name = message.text
        if not validate(last_name=name):
            msg = bot.send_message(message.chat.id, texts['last_name_error'])  # TODO занести в json
            bot.register_next_step_handler(msg, get_last_name)
        chat_id = message.chat.id
        user = User(name)
        user_dict[chat_id] = user
        request_of_ref_num(message.chat.id)


    def request_of_ref_num(chat_id):
        msg = bot.send_message(chat_id, "Введите ваш Reference Number:")
        bot.register_next_step_handler(msg, get_ref_num)


    def get_ref_num(message: types.Message):
        ref_num = message.text
        if not validate(ref_num=ref_num):
            msg = bot.send_message(message.chat.id, texts['reference_num_error'])  # TODO занести в json
            bot.register_next_step_handler(msg, get_last_name)
        chat_id = message.chat.id
        user = user_dict[chat_id]
        user.ref_num = ref_num
        print(user.last_name, user.ref_num)


    def validate(last_name=None, ref_num=None):
        if last_name:
            return True  # TODO
        if ref_num:
            return True  # TODO
        return False


    def check_user_in_db(user_id):
        database_connection.request("GET", "/users/telegram/" + user_id)
        response = database_connection.getresponse()
        return response.getcode() == ResponseCodes.ACCEPTED.value


    def get_user_from_db(user_id):
        database_connection.request("GET", "/users/telegram/" + user_id)
        response = database_connection.getresponse()
        if response.getcode() == ResponseCodes.ACCEPTED.value:
            return User(json_data=json.load(response))
        else:
            raise RuntimeError("Unable to find user with telegram id: " + user_id)


    def add_user_to_db(user: User):
        headers = {'Content-type': 'application/json'}
        database_connection.connect()
        database_connection.request("POST", "/users/create", user.to_json(), headers)
        response = database_connection.getresponse()
        if response.getcode() == ResponseCodes.ACCEPTED.value:
            return User(json_data=json.load(response))
        else:
            raise RuntimeError("Error occurred while adding new user")


    def update_user_in_db(user: User):
        headers = {'Content-type': 'application/json'}
        database_connection.request("PUT", "/users/update/" + str(user.id), user.to_json(), headers)
        response = database_connection.getresponse()
        if response.getcode() == ResponseCodes.ACCEPTED.value:
            return User(json_data=json.load(response))
        else:
            raise RuntimeError("Error occurred while updating user")


    def get_all_user_tickets(user_id):
        database_connection.request("GET", "/users/telegram/" + user_id)
        response = database_connection.getresponse()

        if response.getcode() == ResponseCodes.ACCEPTED.value:
            user = User(json_data=json.load(response))
        else:
            raise RuntimeError("Unable to find user with telegram id: " + str(user_id))

        database_connection.request("GET", "/users/" + str(user.id) + "/tickets")
        response = database_connection.getresponse()

        if response.getcode() != ResponseCodes.ACCEPTED.value:
            raise RuntimeError("Unable to find user with id: " + str(user.id))

        tickets = []
        for ticket in json.load(response):
            if ticket is not None:
                tickets.append(Ticket(json_data=ticket))

        return tickets


    def get_open_user_tickets(user_id):
        database_connection.request("GET", "/users/telegram/" + user_id)
        response = database_connection.getresponse()

        if response.getcode() == ResponseCodes.ACCEPTED.value:
            user = User(json_data=json.load(response))
        else:
            raise RuntimeError("Unable to find user with telegram id: " + user_id)

        database_connection.request("GET", "/users/" + user.id + "/tickets/open")
        response = database_connection.getresponse()

        if response.getcode() != ResponseCodes.ACCEPTED.value:
            raise RuntimeError("Unable to find user with id: " + user.id)

        tickets = []
        for ticket in json.load(response):
            tickets.append(Ticket(json_data=ticket))

        return tickets


    def get_ticket_from_db(ticket_id):
        database_connection.request("GET", "/tickets/" + ticket_id)
        response = database_connection.getresponse()

        if response.getcode() == ResponseCodes.ACCEPTED.value:
            return Ticket(json_data=json.load(response))
        else:
            raise RuntimeError("Unable to find ticket with id: " + ticket_id)


    def add_ticket_to_db(ticket: Ticket):
        headers = {'Content-type': 'application/json'}
        database_connection.request("POST", "/tickets/create", ticket.to_json(), headers)
        print(ticket.to_json())
        response = database_connection.getresponse()

        if response.getcode() == ResponseCodes.ACCEPTED.value:
            return Ticket(json_data=json.load(response))
        else:
            raise RuntimeError("Error occurred while creating new ticket")


    def update_ticket_in_db(ticket: Ticket):
        headers = {'Content-type': 'application/json'}
        database_connection.request("PUT", "/tickets/update/" + ticket.id, ticket.to_json(), headers)
        response = database_connection.getresponse()

        if response.getcode() == ResponseCodes.ACCEPTED.value:
            return Ticket(json_data=json.load(response))
        else:
            raise RuntimeWarning("Error occurred while updating ticket")


    bot.polling()
