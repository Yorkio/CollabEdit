import os
import tkMessageBox
from Tkinter import *
from ScrolledText import *
from socket import AF_INET, SOCK_STREAM, socket, SHUT_WR
from os.path import basename
import threading
from time import sleep
import random
import string

def generate_random_name(length):
    dirname = ''.join(random.choice(string.ascii_lowercase) for i in xrange(length))
    return dirname

socket = socket(AF_INET, SOCK_STREAM)
dirname = generate_random_name(10)
HOME_DIR = os.getcwd() + '\\' + dirname + '\\'

if os.path.isdir(HOME_DIR) == False:
    os.mkdir(dirname)

#DESTINATION = ('192.168.43.27', 7777)
DESTINATION = ('127.0.0.1', 7777)
BUFFER_LENGTH = 1024
socket.connect(DESTINATION)


def edit(tb, fn, message):
    print "Current edition:", message
    if message == 'Finished':
        return
    message = message.split(' ')
    if len(message) > 5:
        return
    if fn != message[0]:
        return
    fn = os.path.join(HOME_DIR, message[0])
    f = None
    try:
        if message[1] == '1':
            element = message[2]
            line = int(message[3]) - 1
            position = int(message[4])
            f = open(fn, 'r')
            lines = f.readlines()
            f.close()
            while line >= len(lines):
                lines.append('\n')
            lines[line] = lines[line][:position] + element + lines[line][position:]
            f = open(fn, 'w')
            for l in lines:
                f.write(l)
            f.close()


        elif message[1] == '0':
            line = int(message[2]) - 1
            position = int(message[3])
            f = open(fn, 'r')
            lines = f.readlines()
            f.close()
            if line < len(lines):
                lines[line] = lines[line][:position] + lines[line][position + 1:]
                f = open(fn, 'w')
                for l in lines:
                    f.write(l)
            f.close()

        elif message[1] == '3':
            element = ' '
            line = int(message[2]) - 1
            position = int(message[3])
            f = open(fn, 'r')
            lines = f.readlines()
            f.close()
            while line >= len(lines):
                lines.append('\n')
            lines[line] = lines[line][:position] + element + lines[line][position:]
            f = open(fn, 'w')
            for l in lines:
                f.write(l)
            f.close()

        elif message[1] == '4':
            element = '\n'
            line = int(message[2]) - 1
            position = int(message[3])
            f = open(fn, 'r')
            lines = f.readlines()
            f.close()
            while line >= len(lines):
                lines.append('\n')
            lines[line] = lines[line][:position] + element + lines[line][position:]
            f = open(fn, 'w')
            for l in lines:
                f.write(l)
            f.close()

    except Exception as e:
        print "Exception:", e

    finally:
        f = open(fn, 'r')
        data = f.read()
        f.close()
        line, column = tb.index(INSERT).split('.')
        line, column = int(line), int(column)
        tb.delete('1.0', END)
        tb.insert('1.0', data)
        tb.mark_set(INSERT, str(line) + '.' + str(column))


def edit_localy(tb, fn, message):
    print "Current edition:", message
    message = message.split(' ')
    f = None
    fn = os.path.join(HOME_DIR, fn)
    try:
        if message[0] == '1':
            element = message[1]
            line = int(message[2]) - 1
            position = int(message[3])
            f = open(fn, 'r')
            lines = f.readlines()
            f.close()
            while line >= len(lines):
                lines.append('\n')
            lines[line] = lines[line][:position] + element + lines[line][position:]
            f = open(fn, 'w')
            for l in lines:
                f.write(l)
            f.close()


        elif message[0] == '0':
            line = int(message[1]) - 1
            position = int(message[2])
            f = open(fn, 'r')
            lines = f.readlines()
            f.close()
            if line < len(lines):
                lines[line] = lines[line][:position] + lines[line][position + 1:]
                f = open(fn, 'w')
                for l in lines:
                    f.write(l)
            f.close()

        elif message[0] == '3':
            element = ' '
            line = int(message[1]) - 1
            position = int(message[2])
            f = open(fn, 'r')
            lines = f.readlines()
            f.close()
            while line >= len(lines):
                lines.append('\n')
            lines[line] = lines[line][:position] + element + lines[line][position:]
            f = open(fn, 'w')
            for l in lines:
                f.write(l)
            f.close()

        elif message[0] == '4':
            element = '\n'
            line = int(message[1]) - 1
            position = int(message[2])
            f = open(fn, 'r')
            lines = f.readlines()
            f.close()
            while line >= len(lines):
                lines.append('\n')
            lines[line] = lines[line][:position] + element + lines[line][position:]
            f = open(fn, 'w')
            for l in lines:
                f.write(l)
            f.close()

    except Exception as e:
        print "Exception:", e


def listen_server(tb, fn):
    m = ''
    while m != 'Terminated' and m != 'Finished':
        m = socket.recv(BUFFER_LENGTH)
        edit(tb, fn, m)


def receive_file(f):
    filename = os.path.join(HOME_DIR, f)
    with open(filename, 'w') as f:
        mess = ''
        while not mess.endswith('\n'):
            m = socket.recv(BUFFER_LENGTH)
            mess += m
        f.write(mess)


class Editor:
    def __init__(self, root):
        self.active_filename = None

        # Create a label that shows the current file editing
        self.filename_label = Label(root, text='No file specified!', fg='dark violet', font=('times', 18, 'italic'))
        self.filename_label.pack()
        frame = Frame(root)
        frame.pack()
        frame.configure(background='black')
        root.title("Editor")
        # Create a text frame
        self.textPad = ScrolledText(root, width=60, height=30)
        self.textPad.pack()

        # Create an open button
        self.open_button = Button(frame, text='Open', width=21, fg='blue', command=self.open_command)
        self.open_button.pack(padx=5, pady=5, side=LEFT)

        # Create a create button
        self.edit_button = Button(frame, text='Create', width=21, fg='blue', command=self.create_command)
        self.edit_button.pack(padx=5, pady=5, side=LEFT)

        # Create a close button
        self.close_button = Button(frame, text='Close', width=21, fg='red', command=self.exit_command)
        self.close_button.pack(padx=5, pady=5, side=LEFT)
        self.textPad.bind('<Key>', self.input_event)
        self.textPad.bind('<BackSpace>', self.backspace_event)
        self.textPad.bind('<Delete>', self.delete_event)
        self.textPad.bind('<space>', self.space_event)
        self.textPad.bind('<Return>', self.enter_event)

    def enter_event(self, event):
        print "To server sent:", '4' + ' ' + ' '.join(self.textPad.index(INSERT).split('.'))
        edition = '4' + ' ' + ' '.join(self.textPad.index(INSERT).split('.'))
        socket.send(edition)
        edit_localy(self.textPad, self.active_filename, edition)
        sleep(1)

    # Capture delete button click event
    def delete_event(self, event):
        print "To server sent:", '0' + ' ' + ' '.join(self.textPad.index(INSERT).split('.'))
        edition = '0' + ' ' + ' '.join(self.textPad.index(INSERT).split('.'))
        socket.send(edition)
        edit_localy(self.textPad, self.active_filename, edition)
        sleep(0.1)

    def space_event(self, event):
        print "To server sent:", '3' + ' ' + ' '.join(self.textPad.index(INSERT).split('.'))
        edition = '3' + ' ' + ' '.join(self.textPad.index(INSERT).split('.'))
        socket.send(edition)
        edit_localy(self.textPad, self.active_filename, edition)
        sleep(0.1)

    # Capture backspace button click event
    def backspace_event(self, event):
        line, column = self.textPad.index(INSERT).split('.')
        line, column = int(line), int(column) - 1
        print "To server sent:", '0' + ' ' + str(line) + ' ' + str(column)
        edition = '0' + ' ' + str(line) + ' ' + str(column)
        socket.send(edition)
        edit_localy(self.textPad, self.active_filename, edition)
        sleep(0.1)


    # Capture a keyboard click event
    def input_event(self, event):
        char = event.char
        special_digits = ['.', ',', '!', '?', '-', ':', ';', '"', "'", "\t", '!', '@', '#', '$', '%',
                          '^', '&', '*', '(', ')', '_', '+', '=', '`', '/', '<', '>', '\\']
        if char.isalpha() or char.isdigit() or char in special_digits:
            print "To server sent:", '1' + ' ' + char + ' ' + ' '.join(self.textPad.index(INSERT).split('.'))
            edition = '1' + ' ' + char + ' ' + ' '.join(self.textPad.index(INSERT).split('.'))
            socket.send(edition)
            edit_localy(self.textPad, self.active_filename, edition)
            sleep(0.1)
        else:
            return

    # Exit from tk
    def exit_command(self):
        if tkMessageBox.askokcancel("Quit", "Are you sure?"):
            socket.send('Terminated')
            root.destroy()
            socket.shutdown(1)
            socket.close()

    # Open file
    def open_command(self):
        print "Open existing file"
        if self.active_filename is not None:
            socket.send('Finished')
        socket.send('Open/Edit file')
        list_of_files = socket.recv(BUFFER_LENGTH)
        if list_of_files == 'empty':
            print 'empty'
            tkMessageBox.showerror('No files on the server yet', "Be the first to create new file!")
            socket.sendall('Finished')
            return

        elif list_of_files == 'Finished':
            print 'finished'
            list_of_files = socket.recv(BUFFER_LENGTH)

        elif ';;;' not in list_of_files and '.txt' not in list_of_files:
            print ';;;'
            list_of_files = socket.recv(BUFFER_LENGTH)

        elif '.txt' not in list_of_files:
            print 'no txt in file'
            list_of_files = socket.recv(BUFFER_LENGTH)
        # Create a child window
        self.lb = Toplevel(root)
        self.lb.title("Choose a file")
        self.lb.geometry('300x100')

        # Create a listbox
        self.listbox = Listbox(self.lb)

        def ret():
            socket.sendall('Finished')
            self.lb.destroy()

        self.lb.protocol("WM_DELETE_WINDOW", ret)

        def select_file(event):
            widget = event.widget
            selection = widget.curselection()
            value = widget.get(selection[0])
            self.active_filename = value

            # Send a filename to download
            socket.sendall(self.active_filename)

            # Download a filename
            receive_file(self.active_filename)
            self.filename_label.config(text='Editing: ' + basename(self.active_filename))

            f = open(os.path.join(HOME_DIR, self.active_filename), 'r')

            data = f.read()
            self.textPad.delete('1.0', END)
            self.textPad.insert('1.0', data)
            f.close()
            self.lb.destroy()

            t = threading.Thread(target=listen_server, args=(self.textPad, self.active_filename, ))
            t.setDaemon(True)
            t.start()

        for f in list_of_files.split(';;;'):
            self.listbox.insert("end", f)

        self.lb.bind("<Double-Button-1>", select_file)
        self.listbox.pack(fill='both', expand=True)


    def create_command(self):
        print "Create new file"

        if self.active_filename is not None:
            socket.sendall('Finished')


        socket.send('Create new file')

        # Create a child window
        self.child = Toplevel(root)
        self.child.title("Create a file")
        self.child.geometry('250x75')

        def ret():
            socket.sendall('Finished')
            self.child.destroy()


        self.child.protocol("WM_DELETE_WINDOW", ret)
        # Create a label
        Label(self.child, text='Enter a filename',).grid(row=0, padx=5)

        # Create an entry widget for a filename input
        entry_filename = Entry(self.child)
        entry_filename.grid(row=0, column=1)

        def get_filename():
            self.active_filename = entry_filename.get()
            if not self.active_filename:
                return

            self.active_filename = self.active_filename.replace(' ', '_')

            if '.txt' not in self.active_filename:
                self.active_filename += '.txt'

            # If a filename is empty
            if not self.active_filename:
                return

            # Check if a filename is free
            print "File name:", self.active_filename
            socket.sendall(self.active_filename)
            response = socket.recv(BUFFER_LENGTH)
            if response == '1':
                tkMessageBox.showerror('Filename conflict', "File with a name: " + self.active_filename +
                                        ' is already exists!')

                self.child.destroy()
                self.active_filename = None
                return
            # Create a file
            open(os.path.join(HOME_DIR, self.active_filename), 'a').close()
            self.filename_label.config(text='Editing: ' + basename(self.active_filename))
            self.textPad.delete('1.0', END)
            self.child.destroy()

            t1 = threading.Thread(target=listen_server, args=(self.textPad, self.active_filename, ))
            t1.setDaemon(True)
            t1.start()

        # Confirm a filename button
        Button(self.child, text='Confirm!', command=get_filename).grid(row=1, column=1, sticky=W, pady=5)

root = Tk()
editor = Editor(root)
root.mainloop()


