from socket import AF_INET, SOCK_STREAM, socket
import os
import threading
import logging

logging.basicConfig(level=logging.DEBUG,
                    format='(%(threadName)-9s) %(message)s',)

directory = os.getcwd() + '\\files\\'    #  directory of a project folder "files"
print directory
if os.path.isdir(directory) == False:
    os.mkdir('files')
recv_buffer_length = 1024
list_of_clients = []
file_lock = {}

class File:
    def __init__(self, name, directory):
        self.name = name
        self.directory = directory
        self.lock = threading.Lock()
        if os.path.isfile(directory + name) == False:
            print "File isn`t exist"
            f = open(directory + name, 'w')
            f.close()

    def read(self):
        f = None
        try:
            f = open(self.directory + self.name, 'r')
            message = f.read()
            return message
        except Exception as e:
            print e
        finally:
            if f is file:
                f.close()

    def edit(self, message, client_socket):
        print "Editting"
        print "Current edition:", message
        if message == 'Finished':
            return
        f = None
        while file_lock[self.name] == True:
            continue
        file_lock[self.name] = True
        try:
            message = message.split(' ')
            if message[0] == '1':       # insert
                element = message[1]
                line = int(message[2]) - 1
                position = int(message[3])
                self.lock.acquire()
                logging.debug('Acquired a lock for inserting')
                f = open(self.directory + self.name, 'r')
                lines = f.readlines()
                f.close()
                while line >= len(lines):
                    lines.append('\n')
                lines[line] = lines[line][:position]  + element + lines[line][position:]
                f = open(self.directory + self.name, 'w')
                for l in lines:
                    f.write(l)

            elif message[0] == '0':     # delete
                line = int(message[1]) - 1
                position = int(message[2])
                self.lock.acquire()
                logging.debug('Acquired a lock for deleting')
                f = open(self.directory + self.name, 'r')
                lines = f.readlines()
                f.close()
                if line < len(lines):
                    lines[line] = lines[line][:position] + lines[line][position+1:]
                    f = open(self.directory + self.name, 'w')
                    for l in lines:
                        f.write(l)

            elif message[0] == '3':
                element = ' '
                line = int(message[1]) - 1
                position = int(message[2])
                self.lock.acquire()
                logging.debug('Acquired a lock for inserting')
                f = open(self.directory + self.name, 'r')
                lines = f.readlines()
                f.close()
                while line >= len(lines):
                    lines.append('\n')
                lines[line] = lines[line][:position] + element + lines[line][position:]
                f = open(self.directory + self.name, 'w')
                for l in lines:
                    f.write(l)

            elif message[0] == '4':
                element = '\n'
                line = int(message[1]) - 1
                position = int(message[2])
                self.lock.acquire()
                logging.debug('Acquired a lock for inserting')
                f = open(self.directory + self.name, 'r')
                lines = f.readlines()
                f.close()
                while line >= len(lines):
                    lines.append('\n')
                lines[line] = lines[line][:position] + element + lines[line][position:]
                f = open(self.directory + self.name, 'w')
                for l in lines:
                    f.write(l)

        except Exception as e:
            print "Edition exception:", e

        finally:
            logging.debug('Released a lock for editting')
            if f is file:
                f.close()
            self.lock.release()
            file_lock[self.name] = False
            sendEdition(self.name, message, client_socket)


def sendListOfFiles(client_socket):
    files = os.listdir(directory)
    sep = ';;;'
    list = sep.join(files)
    if not list:
        list = 'empty'
    client_socket.sendall(list)


def editFile(file, client_socket):
    edition = client_socket.recv(recv_buffer_length)
    while 1:
        if edition == 'Finished':
            client_socket.send('Finished')
            break
        file.edit(edition, client_socket)
        edition = client_socket.recv(recv_buffer_length)


def sendEdition(file_name, edition, current_socket):
    try:
        print "Send edition"
        edition = ' '.join(edition)
        print "List of clients:", list_of_clients
        print "Current client:", current_socket
        for socket in list_of_clients:
            if socket != current_socket:
                socket.sendall(file_name + ' ' + edition)
                print "Edition sent", edition
    except Exception as e:
        print "Send edition exception:", e


def workWithClient(client_socket):
    action = client_socket.recv(recv_buffer_length)
    while action != 'Terminated':
        if action == 'Create new file':
            createNewFile(client_socket)
        elif action == 'Open/Edit file':
            openExistingFile(client_socket)
        elif action == 'Finished':
            print 'Finished command received'
            client_socket.send('Finished')
        action = client_socket.recv(recv_buffer_length)
        print action, 'action'
    client_socket.close()
    list_of_clients.remove(client_socket)


def createNewFile(client_socket):
    print 'Create new file'
    file_name = client_socket.recv(recv_buffer_length)
    if file_name == 'Finished':
        return
    print 'File name received', file_name
    if os.path.isfile(directory + file_name) == True:    # while file with such name is already exist
        print 'File with such name is exist'                # acknowledgement that file with such name is exist
        client_socket.sendall('1')
    else:
        print 'File with such name isn`t exist'
        client_socket.sendall('0')                              # acknowledgement that file with such name isn`t exist
        file_lock[file_name] = False
        file = File(file_name, directory)
        editFile(file, client_socket)


def openExistingFile(client_socket):
    print "Open existing file"
    sendListOfFiles(client_socket)
    print 'List of files sent'
    file_name = client_socket.recv(recv_buffer_length)
    if file_name == 'Finished':
        return
    print 'File name recieved', file_name
    if file_name not in file_lock:
        file_lock[file_name] = False
    file = File(file_name, directory)
    message = file.read()
    message += '\n'             # acknowledgement of ending of the file
    client_socket.sendall(message)
    print 'File sent'
    editFile(file, client_socket)


if __name__ == '__main__':
    s = socket(AF_INET, SOCK_STREAM)
    #s.bind(('192.168.43.27',7777))
    s.bind(('127.0.0.1',7777))
    backlog = 5
    s.listen(backlog)
    count = 1
    threads = []
    while True:
        try:
            client_socket, client_addr = s.accept()
            list_of_clients.append(client_socket)
            print "Client " + str(count) + " connected"
            t = threading.Thread(name='Thread ' + str(count), target = workWithClient, args = (client_socket, ))
            print 'Thread ' + str(count) + ' created'
            threads.append(t)
            t.start()
            print 'Thread ' + str(count) + ' started'
        finally:
            count += 1

