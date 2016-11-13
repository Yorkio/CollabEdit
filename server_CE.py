from socket import AF_INET, SOCK_STREAM, socket
import os
import threading
import logging

logging.basicConfig(level=logging.DEBUG,
                    format='(%(threadName)-9s) %(message)s',)

directory = os.path.dirname(os.path.abspath(__file__)) + '\\files\\'    #  directory of a project folder "files"

class File:
    def __init__(self, name, directory):
        self.name = name
        self.directory = directory
        self.lock = threading.Lock()
        if os.path.isfile(directory + name) == False:
            f = open(directory + name, 'w')
            f.close()

    def read(self):
        self.lock.acquire()
        try:
            logging.debug('Acquired a lock')
            f = open(self.directory + self.name, 'r')
            message = f.read()
            return message
        finally:
            logging.debug('Released a lock')
            f.close()
            self.lock.release()

    def write(self, message):
        self.lock.acquire()
        try:
            logging.debug('Acquired a lock')
            f = open(self.directory + self.name, 'w')
            f.write(message)
        finally:
            logging.debug('Released a lock')
            f.close()
            self.lock.release()

def workWithClient(client_socket):
    recv_buffer_length = 1024
    #sendListOfFiles(client_socket)
    #print 'List of files sent'
    action = client_socket.recv(recv_buffer_length)
    if action == 'Create new file':
        createNewFile(client_socket)
    elif action == 'Open existing file':
        openExistingFile(client_socket)

def sendListOfFiles(client_socket):
    files = os.listdir(directory)
    sep = ';;;'
    list = sep.join(files)
    client_socket.sendall(list)

def createNewFile(client_socket):
    print 'Create new file'
    recv_buffer_length = 1024
    file_name = client_socket.recv(recv_buffer_length)
    print 'File name received'
    count = 1
    while os.path.isfile(directory + file_name) == True and count <= 5:    # while file with such name is already exist
        print 'File with such name is exist. Trial #' + str(count)
        client_socket.sendall('1')
        file_name = client_socket.recv(recv_buffer_length)
        count += 1
    if count <= 5:
        print 'File with such name isn`t exist'
        client_socket.sendall('0')                          # acknowledgement that file with such name isn`t exist
        f = File(file_name, directory)
        message = ''
        while not message.endswith('\n'):
            m = client_socket.recv(recv_buffer_length)
            message += m
        print 'File received'
        f.write(message)
    client_socket.close()

def openExistingFile(client_socket):
    recv_buffer_length = 1024
    file_name = client_socket.recv(recv_buffer_length)
    print 'File name recieved'
    count = 1
    while os.path.isfile(directory + file_name) == True and count <= 5:    # while file with such name isn`t exist
        print 'File with such name isn`t exist. Trial #' + str(count)
        client_socket.sendall('1')
        file_name = client_socket.recv(recv_buffer_length)
    if count <= 5:
        print 'File with such name is exist'
        client_socket.sendall('0')                          # acknowledgement that file with such name is exist
        f = File(file_name, directory)
        message = f.read()
        client_socket.sendall(message)
        print 'File sent'
    client_socket.close()

if __name__ == '__main__':
    s = socket(AF_INET, SOCK_STREAM)
    s.bind(('127.0.0.1',7777))
    backlog = 5
    s.listen(backlog)
    count = 1
    while True:
        try:
            client_socket,client_addr = s.accept()
            print "Client " + str(count) + " connected"
            threads = []
            t = threading.Thread(name = 'Thread ' + str(count), target = workWithClient, args = (client_socket, ))
            print 'Thread ' + str(count) + ' created'
            threads.append(t)
            t.start()
            t.join()
        finally:
            client_socket.close()

