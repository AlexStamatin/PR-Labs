import socket
import threading
import random
import string


def help_info(arg):
    info = ''
    for key, value in command_descriptions.items():
        info += key + value + '\n'
    return info


def hello(arg):
    return 'Hello ' + arg


def flip(arg):
    return random.choice(['Heads', 'Tails'])


def nextchar(chars):
    return random.choice(chars)


def randpass(arg):
    try:
        arg = int(arg)
        if arg < 6 or arg > 20:
            return "Length outside (6-20) range"
        length = arg - 3
        pwd = []
        possible_chars = string.ascii_letters + string.digits + string.punctuation
        pwd.append(random.choice(string.ascii_lowercase))
        pwd.append(random.choice(string.ascii_uppercase))
        pwd.append(str(random.randint(0,9)))
        for i in range(length):
            pwd.append(nextchar(possible_chars))
    except ValueError:
        return "Invalid length"
    random.shuffle(pwd)
    return ''.join(pwd)


def dice(arg):
    return random.choice(['1', '2', '3', '4', '5', '6'])


def handle_commands(command, param):
    try:
        func = commands.get(command)
        if func == None:
            raise KeyError
        print(command, param)
        return func(param)
    except KeyError:
        return find_similar_commands(command)


def find_similar_commands(invalid_command):
    similar = {}
    for valid in command_descriptions:
        distance = damerau_levenshtein_distance(invalid_command, valid)
        similar[valid] = distance
    similar = min(similar, key=similar.get)
    if len(similar):
        return 'Invalid command entered. Did you mean ' + similar + ' ?'
    else:
        return 'Invalid command entered'


def damerau_levenshtein_distance(s1, s2):
    if len(s1) < len(s2):
        return damerau_levenshtein_distance(s2, s1)

        # len(s1) >= len(s2)
    if len(s2) == 0:
        return len(s1)

    previous_row = range(len(s2) + 1)
    for i, c1 in enumerate(s1):
        current_row = [i + 1]
        for j, c2 in enumerate(s2):
            insertions = previous_row[
                             j + 1] + 1  # j+1 instead of j since previous_row and current_row are one character longer
            deletions = current_row[j] + 1  # than s2
            substitutions = previous_row[j] + (c1 != c2)
            current_row.append(min(insertions, deletions, substitutions))
        previous_row = current_row

    return previous_row[-1]

commands = {
    '/help': help_info,
    '/hello': hello,
    '/flip' : flip,
    '/dice' : dice,
    '/password' : randpass
}


command_descriptions = {
    '/dice': '- Virtually role a six-sided die',
    '/flip': '- Virtually flip a coin',
    '/help': ' - Shows available commands',
    '/hello': '- Shows a greeting message. Parameter : name',
    '/password': '- Generates a random password. Parameter : password length',

}

server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

server_socket.bind(('127.0.0.1', 8080))

# Start listening on socket, maximum number of queued connections - 10
server_socket.listen(10)
print('Socket initialised')


def process(client_message):
    param = ''
    message_arrg = client_message.strip().split(' ')
    if len(message_arrg) == 2:
        command, param = message_arrg
    elif len(message_arrg) == 1:
        command = message_arrg[0]
    else:
        return "Wrong command"
    return handle_commands(command, param)


def handle_client_connection(connection):
    # infinite loop so that function do not terminate and thread do not end.
    while True:

        # Receiving from client
        data = connection.recv(1024)
        reply = process(data.decode()).encode()
        if not data:
            break

        connection.sendall(reply)

    # came out of loop
    connection.close()

while 1:
    # wait to accept a connection - blocking call
    connection, address = server_socket.accept()
    print('Connected with ' + address[0] + ':' + str(address[1]))

    thread = threading.Thread(target=handle_client_connection, args=(connection,))
    thread.start()

