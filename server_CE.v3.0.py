from socket import AF_INET, SOCK_STREAM, socket
import os
import threading
import logging
from time import sleep

logging.basicConfig(level=logging.DEBUG,
                    format='(%(threadName)-9s) %(message)s',)

directory = os.getcwd() + '\\files\\'    #  directory of a project folder "files"

recv_buffer_length = 1024
list_of_clients = []

class File:
    def __init__(self, name, directory):
        print "Initialized"
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
            f.close()

    def edit(self, message):
        print "Editting"
        f = None
        try:
            message = message.split(' ')
            if message[0] == '1':
                element = message[1]
                line = int(message[2]) - 1
                position = int(message[3])
                self.lock.acquire()
                logging.debug('Acquired a lock for inserting')
                f = open(self.directory + self.name, 'r')
                contents = f.readlines()
                if line >= len(contents):
                    contents.insert(position, element)
                    print 'KEEEEEEEEEEEEEEEEEEEEEEEEEEk'
                #lines[line] = lines[line][:position] + element + lines[line][position:]
                else:
                    contents[line] = contents[line][:position]  + element + contents[line][position:]
                f.close()
                print contents
                f = open(self.directory + self.name, "w")
                contents = "".join(contents)
                f.write(contents)
                f.close()

            elif message[0] == '0':
                line = int(message[1]) - 1
                position = int(message[2])
                self.lock.acquire()
                logging.debug('Acquired a lock for deleting')
                f = open(self.directory + self.name, 'rw+')
                lines = f.readlines()
                lines[line] = lines[line][:position] + lines[line][position+1:]
                for line in lines:
                    f.write(line + '\n')
        finally:
            logging.debug('Released a lock')
            f.close()
            sendEdition(self.name, message)
            self.lock.release()

def sendListOfFiles(client_socket):
    files = os.listdir(directory)
    sep = ';;;'
    list = sep.join(files)
    client_socket.sendall(list)


def editFile(file, client_socket):
    edition = client_socket.recv(recv_buffer_length)
    while edition != 'Finished':
        file.edit(edition)
        edition = client_socket.recv(recv_buffer_length)

def sendEdition(file_name, edition):
    edition = ''.join(edition)
    for client_socket in list_of_clients:
        client_socket.sendall(file_name + ' ' + edition)

def workWithClient(client_socket):
    action = client_socket.recv(recv_buffer_length)
    while action != 'Terminate':
        if action == 'Create new file':
            createNewFile(client_socket)
        elif action == 'Open/Edit file':
            openExistingFile(client_socket)
        action = client_socket.recv(recv_buffer_length)
    client_socket.close()
    del list_of_clients[client_socket]

def createNewFile(client_socket):
    print 'Create new file'
    file_name = client_socket.recv(recv_buffer_length)
    print 'File name received'
    if os.path.isfile(directory + file_name) == True:    # while file with such name is already exist
        print 'File with such name is exist'                # acknowledgement that file with such name is exist
        client_socket.sendall('1')
    else:
        print 'File with such name isn`t exist'
        client_socket.sendall('0')                              # acknowledgement that file with such name isn`t exist

        file = File(file_name, directory + '\\')
        editFile(file, client_socket)

def openExistingFile(client_socket):
    print "Open existing file"
    sendListOfFiles(client_socket)
    print 'List of files sent'
    file_name = client_socket.recv(recv_buffer_length)
    print 'File name recieved', file_name
    file = File(file_name, directory)
    message = file.read()
    client_socket.sendall(message)
    print 'File sent'
    editFile(file, client_socket)

if __name__ == '__main__':
    s = socket(AF_INET, SOCK_STREAM)
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
            t = threading.Thread(name = 'Thread ' + str(count), target = workWithClient, args = (client_socket, ))
            print 'Thread ' + str(count) + ' created'
            threads.append(t)
            t.start()
            t.join()
        finally:
            client_socket.close()
            count += 1

