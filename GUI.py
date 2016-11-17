import os
import tkMessageBox
import tkFileDialog
from Tkinter import *
from ScrolledText import *
from socket import AF_INET, SOCK_STREAM, socket, SHUT_WR
from os.path import basename

socket = socket(AF_INET, SOCK_STREAM)
HOME_DIR = os.getcwd()
DESTINATION = ('127.0.0.1', 7777)
BUFFER_LENGTH = 1024
socket.connect(DESTINATION)

# Change this!! + '\n
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

    # # Rewrite an active file
    # def save_command(self):
    #     if self.active_filename is not None:
    #         self.filename_label.config(text='Editing: ' + basename(self.active_filename))
    #         a = self.textPad.get('1.0', END)
    #         f = open(self.active_filename, 'w')
    #         f.write(a)
    #         f.close()

    # Capture delete button click event
    def delete_event(self, event):
        socket.send('0' + ' ' + ' '.join(self.textPad.index(INSERT).split('.')))

    # Capture backspace button click event
    def backspace_event(self, event):
        line, column = self.textPad.index(INSERT).split('.')
        line, column = int(line), int(column) - 1
        socket.send('0' + ' ' + str(line) + ' ' + str(column))

    # Capture a keyboard click event
    def input_event(self, event):
        char = event.char
        if char.isspace() or not char.isalpha() and not char.isdigit():
            return
        socket.send('1' + ' ' + char + ' ' + ' '.join(self.textPad.index(INSERT).split('.')))

    # Exit from tk
    def exit_command(self):
        if tkMessageBox.askokcancel("Quit", "Are you sure?"):
            socket.send('Terminate')
            root.destroy()
            socket.shutdown(1)
            socket.close()

    # Open file
    def open_command(self):
        socket.send('Open/Edit file')
        list_of_files = socket.recv(BUFFER_LENGTH)
        print list_of_files
        # Create a child window
        self.lb = Toplevel(root)
        self.lb.title("Choose a file")
        self.lb.geometry('300x100')

        # Create a listbox
        self.listbox = Listbox(self.lb)

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
            with open(self.active_filename, 'r') as f:
                data = f.read()
                self.textPad.delete('1.0', END)
                self.textPad.insert('1.0', data)
            self.lb.destroy()

        for f in list_of_files.split(';;;'):
            self.listbox.insert("end", f)

        self.lb.bind("<Double-Button-1>", select_file)
        self.listbox.pack(fill='both', expand=True)

    def create_command(self):
        socket.send('Create new file')

        # Create a child window
        self.child = Toplevel(root)
        self.child.title("Create a file")
        self.child.geometry('250x75')

        # Create a label
        Label(self.child, text='Enter a filename',).grid(row=0, padx=5)

        # Create an entry widget for a filename input
        entry_filename = Entry(self.child)
        entry_filename.grid(row=0, column=1)

        def get_filename():
            self.active_filename = entry_filename.get()

            if '.txt' not in self.active_filename:
                self.active_filename += '.txt'

            # If a filename is empty
            if not self.active_filename:
                return

            # Check if a filename is free
            socket.sendall(self.active_filename)
            response = socket.recv(BUFFER_LENGTH)
            if response == '1':
                tkMessageBox.showerror('Filename conflict', "File with a name: " + self.active_filename +
                                        ' is already exists!')
                return
            self.filename_label.config(text='Editing: ' + basename(self.active_filename))
            self.textPad.delete('1.0', END)
            self.child.destroy()

        # Confirm a filename button
        Button(self.child, text='Confirm!', command=get_filename).grid(row=1, column=1, sticky=W, pady=5)

root = Tk()
editor = Editor(root)
root.mainloop()


