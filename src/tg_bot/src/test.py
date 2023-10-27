import http.client
import json

from start import ResponseCodes, Ticket, User

database_connection = http.client.HTTPConnection('localhost', 8081, timeout=10)


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


# Tests


def check_user_test(user_id):
    return check_user_in_db(user_id)


def get_user_test(user_id):
    return get_user_from_db(user_id)


def add_user_test(telegram_user_id, telegram_chat_id, last_name):
    return add_user_to_db(User(telegram_user_id, telegram_chat_id, last_name))


def update_user_test(user_id, last_name):
    user_to_update = get_user_from_db(user_id)
    user_to_update.last_name = last_name
    return update_user_in_db(user_to_update)


def get_all_user_tickets_test(user_id):
    return get_all_user_tickets(user_id)


def get_open_user_tickets_test(user_id):
    return get_open_user_tickets_test(user_id)


def add_ticket_test(user_id, country_name, referral_number):
    user = get_user_from_db(user_id)
    user_db_id = user.id
    return add_ticket_to_db(Ticket(user_id=user_db_id, country_name=country_name, referral_number=referral_number))


def update_ticket_test(ticket_id, country):
    ticket = get_ticket_from_db(ticket_id)
    ticket.country_name = country
    return update_ticket_in_db(ticket)


if __name__ == "__main__":
    # Check User:
    # print(check_user_test("4"))

    # Get User
    # print(get_user_test("3"))

    # Add User:
    # print(add_user_test("3", "3", "Nikolaev"))

    # Update User
    # print(update_user_test("2", "Popover"))

    # Get All User Tickets
    # print(get_all_user_tickets_test("1"))

    # Add ticket
    # print(add_ticket_test("1", "EE", "1337"))

    # Update Ticket
    print(update_ticket_test("6116a35ee50edf549844f211", "NL"))
