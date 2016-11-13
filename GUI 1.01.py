from Tkinter import *
from ScrolledText import *
import tkMessageBox
import tkFileDialog
from os.path import basename

# Specify file extensions to open
FILEOPENOPTIONS = dict(defaultextension='.txt',
                  filetypes=[('Txt file','*.txt')])

class Editor:
    def __init__(self, root):
        self.active_filename = None
        self.filename_label = Label(root, text='No file specified!', fg='purple', font=('times', 18, 'italic'))
        self.filename_label.pack()
        frame = Frame(root)
        frame.pack()
        frame.configure(background='black')
        root.title("Editor")
        # Create a text frame
        self.textPad = ScrolledText(root, width=60, height=30)
        self.textPad.pack()

        # Create an open button
        self.open_button = Button(frame, text='Open', width=15, fg='blue', command=self.open_command)
        self.open_button.pack(padx=5, pady=5, side=LEFT)

        # Create a create button
        self.edit_button = Button(frame, text='Create', width=15, fg='blue', command=self.create_command)
        self.edit_button.pack(padx=5, pady=5, side=LEFT)

        # Create a save button
        self.save_button = Button(frame, text='Save', width=15, fg='blue', command=self.save_command)
        self.save_button.pack(padx=5, pady=5, side=LEFT)

        # Create a close button
        self.close_button = Button(frame, text='Close', width=15, fg='blue', command=self.exit_command)
        self.close_button.pack(padx=5, pady=5, side=LEFT)

    # Rewrite an active file
    def save_command(self):
        if self.active_filename is not None:
            self.filename_label.config(text = 'Editing: ' + basename(self.active_filename))
            a = self.textPad.get('1.0', END)
            f = open(self.active_filename, 'w')
            f.write(a)
            f.close()

    # Exit from tk
    def exit_command(self):
        if tkMessageBox.askokcancel("Quit", "Are you sure?"):
            root.destroy()

    # Open file
    def open_command(self):
            file = tkFileDialog.askopenfile(parent=root, mode='rb', title='Select a file', **FILEOPENOPTIONS)
            if file != None:
                self.active_filename = file.name
                self.filename_label.config(text='Editing: ' + basename(self.active_filename))
                data = file.read()
                self.textPad.delete('1.0', END)
                self.textPad.insert('1.0', data)
                file.close()

    def create_command(self):
        # Create a child window
        self.child = Toplevel(root)
        self.child.title("Create a file")
        self.child.geometry('250x75')
        # Create a label
        Label(self.child, text='Enter a filename', ).grid(row=0, padx=5)

        # Create an entry widget
        entry_filename = Entry(self.child)
        entry_filename.grid(row=0, column=1)

        def get_filename():
            self.active_filename = entry_filename.get()
            if not self.active_filename:
                return
            if '.txt' not in self.active_filename:
                self.active_filename += '.txt'
                self.filename_label.config(text='Editing: ' + basename(self.active_filename))
            self.textPad.delete('1.0', END)
            self.child.destroy()


        # Save a filename button
        Button(self.child, text='Confirm!', command=get_filename).grid(row=1, column=1, sticky=W, pady=5)


root = Tk()
editor = Editor(root)
root.mainloop()


