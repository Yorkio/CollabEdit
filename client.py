from socket import AF_INET, SOCK_STREAM, socket, SHUT_WR
import os

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


CLIENT_HOME_PATH = os.path.dirname(os.path.abspath(__file__)) + '\\local_files\\'


if __name__ == '__main__':

    ##########################################
    #          Case: Create new file         #
    ##########################################

    choice = 'Open/Edit file'
    socket.sendall(choice)
    if choice == 'Create new file':
        attempts = 5
        filename = raw_input('Enter the filename: ')
        new_filename = filename
        socket.sendall(filename)
        response = socket.recv(recv_buffer_length)
        print 'Response :', response
        # If the name is not free user have 5 attempts to choose another one
        while response != '0' and attempts != 0:
            new_filename = raw_input('Filename already exists. '
                                     'Choose another name: ')
            socket.send(new_filename)
            response = socket.recv(recv_buffer_length)
            print 'Response :', response
            if response == '1' and attempts != 0:
                attempts -= 1

            elif attempts == 0:
                print 'Out of attempts.'
                socket.shutdown(SHUT_WR)
                socket.close()
                break

        # If the name is free
        if response == '0':
            with open(CLIENT_HOME_PATH+new_filename, 'w+') as new_file:
                # Editing file...

                # Saving file...

                # Sending file to server
                data = new_file.read()
                socket.sendall(data)
            socket.shutdown(SHUT_WR)
            socket.close()

    else:
        socket.shutdown(SHUT_WR)
        socket.close()

    ##########################################
    #           Case: Open/Edit file         #
    ##########################################

    # choice = 'Open/Edit file'

    if choice == 'Open/Edit file':

        socket.send(choice)
        # Asking user which file to Open/Edit...
        chosen_file = raw_input('Choose file: ')

        # Sending the chosen file to the server
        socket.send(chosen_file)
        response = socket.recv(recv_buffer_length)
        # If server approved opening the chosen file
        if response == '0':

            # Receiving the chosen file
            receive_file(file)

            # Editing file...

            # Closing socket
            socket.shutdown(SHUT_WR)
            socket.close()

        # If server denied access to the chosen file
        # user has two options: to wait or to leave server
        elif response == '1':
            option = raw_input('Option 0 to wait.'
                               'Option 1 to leave.'
                               'Choose option: ')
            socket.send(option)


    ##########################################
    #             Case: Save file            #
    ##########################################
    # elif choice == 'Save file':
    #     # Save file and continue


