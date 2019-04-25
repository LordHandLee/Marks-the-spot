from tkinter import *
import time
import threading
import random
from queue import Queue
import pyautogui
from tkinter import filedialog
from buttonpressed import *
import win32api

class GuiPart():
    def __init__(self, master, queue, endCommand):
        self.queue = queue
        # Set up the GUI
        console = Button(master, text='Done', command=endCommand)
        console.pack()
        # Add more GUI stuff here depending on your specific needs
        self.master = master
        self.label = Label(master)
        self.v = StringVar()
        self.label = Label(master, textvariable=self.v)
        self.label.pack()


        self.BrowseButton = Button(master, text="Choose file", command=self.open_file)
        self.BrowseButton.pack()
        self.BrowseButton.configure(state=NORMAL)
        self.SaveButton = Button(master, text="Create file", command=self.create_file)
        self.SaveButton.pack()
        self.j = StringVar()
        self.file_label = Label(master, textvariable=self.j)
        self.file_label.pack()


        self.update_label()
        root.protocol("WM_DELETE_WINDOW", self.erase_previously_opened_file_path())

    def update_label(self):
        self.pyposition = pyautogui.position()

        self.fart = ' '.join(map(str, self.pyposition))
        self.v.set(self.pyposition)
        self.label.after(500, self.update_label)

    def open_file(self):
        root.file_name = filedialog.askopenfile(initialdir="/", title="Select file",
                                                filetypes=(("executable files", "*.exe"), ("all files", "*.*")))
        self.filepath = root.file_name
        with open("coordinate save data.txt", 'w+') as new_filepath:
            new_filepath.write(str(self.filepath))

        with open("coordinate save data.txt", 'r') as new_filepath2:
            read_filepath = new_filepath2.read()
        Result = re.search(r'(.:\/.*txt)', read_filepath)
        if Result:
            self.newlabelupdate = Result.group(1)
            self.j.set(self.newlabelupdate)
        self.previously_opened_file()

    def create_file(self):
        f = filedialog.asksaveasfile(mode='w', defaultextension='.txt')
        if f is None:
            return


    def previously_opened_file(self):
        with open("selected_file.txt", 'w+') as f:
            f.write(self.newlabelupdate)
            f.close

    def erase_previously_opened_file_path(self):
        open('selected_file.txt', 'w').close()

    def processIncoming(self):
        """Handle all messages currently in the queue, if any."""
        while self.queue.qsize():

            try:
                msg = self.queue.get(0)
                print(msg)

            except Queue.empty:
                pass

class pressed():

    def left_button_pressed(self):
        state_left = win32api.GetKeyState(0x01)
        self.hey = False
        coordlist = []
        while True:
            #print(self.hey)
            a = win32api.GetKeyState(0x01)
            b = win32api.GetKeyState(0x02)

            if a != state_left:  # Button state changed
                state_left = a
                print(a)
                #print(self.hey)
                if a < 0:
                    #print(self.hey)
                    print('Left Button Pressed')
                    self.hey = True
                    print(self.hey)
                    coord = pyautogui.position()
                    print(coord)
                    newcoord = ','.join(map(str, coord))

                    print(coordlist)
                    print(newcoord)
                    selected_file = "selected_file.txt"
                    with open(selected_file, 'r') as g:
                        previous_path_lock = g.read()
                        print(previous_path_lock)
                        try:
                            with open(previous_path_lock, 'w') as f:
                                if f:
                                    coordlist.append(newcoord)
                                    f.write("\n".join(coordlist))
                                    print(coordlist)
                        except:
                            pass
                else:
                    print('Left Button Released')
                    self.hey = False



class ThreadedClient:
    """
    Launch the main part of the GUI and the worker thread. periodicCall and
    endApplication could reside in the GUI part, but putting them here
    means that you have all the thread controls in a single place.
    """
    def __init__(self, master):
        """
        Start the GUI and the asynchronous threads. We are in the main
        (original) thread of the application, which will later be used by
        the GUI as well. We spawn a new thread for the worker (I/O).
        """
        self.master = master

        # Create the queue
        self.queue = Queue()

        # Set up the GUI part
        self.gui = GuiPart(master, self.queue, self.endApplication)

        # Set up the thread to do asynchronous I/O
        # More threads can also be created and used, if necessary
        self.running = 1
        self.running2 = 1
        self.thread1 = threading.Thread(target=self.workerThread1)
        self.thread1.daemon = True
        self.thread1.start()

        self.thread2 = threading.Thread(target=self.workerThread2)
        self.thread2.daemon = True
        self.thread2.start()


        # Start the periodic call in the GUI to check if the queue contains
        # anything
        self.periodicCall()

    def periodicCall(self):
        """
        Check every 200 ms if there is something new in the queue.
        """
        self.gui.processIncoming()
        self.master.after(200, self.periodicCall)

    def workerThread1(self):
        """
        This is where we handle the asynchronous I/O. For example, it may be
        a 'select(  )'. One important thing to remember is that the thread has
        to yield control pretty regularly, by select or otherwise.
        """
        while self.running:
            self.msg = pressed.left_button_pressed(self)
            self.queue.put(self.msg)

    def endApplication(self):
        self.running = 0


root = Tk()

client = ThreadedClient(root)
root.mainloop()
