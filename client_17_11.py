from socket import AF_INET, SOCK_STREAM, socket, SHUT_WR
import os

CLIENT_HOME_PATH = os.path.dirname(os.path.abspath(__file__)) + '\\local_files\\'
socket = socket(AF_INET, SOCK_STREAM)
destination = ('127.0.0.1', 7777)
recv_buffer_length = 1024
socket.connect(destination)

def receive_file(file):
    with open(CLIENT_HOME_PATH+file, 'w') as file:
        while True:
            m = socket.recv(recv_buffer_length)
            if len(m) != 0:
                file.write(m)
            else:
                break
    return

def create_file(filename):
    new_filename = filename
    socket.sendall(filename)
    response = socket.recv(recv_buffer_length)
    # If the name is not free user have 5 attempts to choose another one
    while response != '0':
        new_filename = raw_input('Filename already exists. '
                                 'Choose another name: ')
        socket.send(new_filename)
        response = socket.recv(recv_buffer_length)

    # If the name is free
    if response == '0':
        with open(CLIENT_HOME_PATH + new_filename, 'w+') as new_file:
            # Editing file...

            # Saving file...

            # Sending file to server
            data = new_file.read()
            socket.sendall(data)
        socket.shutdown(SHUT_WR)
        socket.close()
    return

def open_edit_file(chosen_file):
    print "Chosen file is", chosen_file
    # Sending the chosen file to the server
    socket.sendall(chosen_file)
    print "File name sent"
    # Receiving the chosen file
    receive_file(chosen_file)
    print "File received"
    # Editing file...
    return

def proceed_choice(choice):
    socket.sendall(choice)
    if choice == 'Create new file':
        filename = raw_input('Enter the filename: ')
        create_file(filename)
    elif choice == 'Open/Edit file':
        chosen_file = raw_input('Choose file: ')
        open_edit_file(chosen_file)
    elif choice == 'Save file':
        # Save file and continue
        print 'Saving file...'
    elif choice == 'Exit':
        socket.sendall('Terminate')
        print 'Exit'
        socket.shutdown(SHUT_WR)
        socket.close()
    else:
        print 'Socket shutdown'
        socket.shutdown(SHUT_WR)
        socket.close()
    return

if __name__ == '__main__':
    # CHOICE MUST BE ASSIGNED HERE
    print 'Receiving existing files...'
    received_files = socket.recv(recv_buffer_length)
    existing_files = received_files.split(';;;')
    proceed_choice(choice)



