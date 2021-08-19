import os.path
import tkinter as tk
from PIL import Image, ImageTk
import textwrap
import random
import json


class ChatBubble:
    """
        Chat bubble containing message

        ...

        Attributes
        ----------
        parent : tk.Canvas
            canvas which holds all chat bubbles
        frame : tk.Frame
            frame which holds chat bubble
        left : boolean
            true if bubble on left side of canvas

        Methods
        -------
        draw_triangle():
            draws bubble stem on canvas
        """
    BUBBLE_PAD_Y = 500
    L_BUBBLE_PAD_X = 90
    R_BUBBLE_PAD_X = 350

    def __init__(self, parent, message, left):
        self.parent = parent
        self.frame = tk.Frame(parent, bg="light grey")
        self.left = left

        if self.left:
            self.i = self.parent.create_window(self.L_BUBBLE_PAD_X, self.BUBBLE_PAD_Y, window=self.frame)
        else:
            self.i = self.parent.create_window(self.R_BUBBLE_PAD_X, self.BUBBLE_PAD_Y, window=self.frame)

        self.lbl_bubble = tk.Label(self.frame, text=message, font=("Helvetica", 9), anchor='w', justify=tk.LEFT, bg="light grey", width=17).pack(fill='both')
        root.update_idletasks()
        self.bubl_tip = self.parent.create_polygon(self.draw_triangle(self.i), fill="light grey", outline="light grey")

    def draw_triangle(self, widget):
        x1, y1, x2, y2 = self.parent.bbox(widget)
        if self.left:
            return x1, y2 - 10, x1 - 15, y2 + 10, x1, y2
        return x2, y2 - 10, x2 + 15, y2 + 10, x2, y2


class ChatCanvas(tk.Canvas):
    """
        Canvas widget containing chat bubbles.

        ...

        Attributes
        ----------
        parent : tk.frame
            frame which holds ChatCanvas
        app : MainApplication
            current instance of MainApplication
        bubbles : list
            list of chat bubbles in canvas

        Methods
        -------
        send_message():
            creates chat bubble and appends to bubbles

        exit_btn():
            creates button that exits program
        """
    def __init__(self, parent, app, *args, **kwargs):
        tk.Canvas.__init__(self, parent, *args, **kwargs)
        self.parent = parent
        self.app = app
        self.bubbles = []

    def send_message(self, message="", left=True):
        """Creates a new msg bubble and updates canvas to fit it."""
        message = textwrap.fill(message, 20)
        temp = ChatBubble(self, message, left)
        x1, y1, x2, y2 = self.bbox(temp.i)

        if self.bubbles:
            for bubble in self.bubbles:
                self.move(bubble.i, 0, 2*(y1-y2))
                self.move(bubble.bubl_tip, 0, 2*(y1-y2))

        self.move(temp.i, 0, y1-y2)
        self.move(temp.bubl_tip, 0, y1-y2)
        self.bubbles.append(temp)
        self.update_scrollregion()

    def update_scrollregion(self):
        box = self.bbox(tk.ALL)
        box = list(box)
        box[1] -= 300    # edit bounding box to add vertical padding
        self.config(scrollregion=box)     #  moves everything to the top
        self.yview_moveto(1)    # scroll to bottom

    def exit_btn(self):
        frame = tk.Frame(self, bg='Blue')
        button = tk.Button(command=self.app.exit, text='Exit Program')
        self.create_window(ChatBubble.L_BUBBLE_PAD_X + 100, ChatBubble.BUBBLE_PAD_Y + 100, window=button)


class TaskWindow(tk.Toplevel):
    """
    The window containing the task list that has been created.

    ...

    Attributes
    ----------
    wdw_root : tk.frame
        frame which holds TaskWindow
    task_list : list
        list of task name strings
    btn_end : tk.button
        Button that destroys TaskWindow and reinstats Main App

    Methods
    -------
    end_tasks():
        destroys TaskWindow and reinstats Main App

    kill_root():
        destroys the root window of the application

    save_state():
        saves tasks to json data file

    rand_color():
        returns random rgb color int
    """

    def __init__(self, wdw_root, task_list, app=None, **kw):
        """
        Constructs attributes and widgets for window.

        :param wdw_root: frame which holds TaskWindow
        :param task_list: list of task name strings
        :param kw: other inherited args
        """
        super().__init__(wdw_root, **kw)
        self.minsize(400, 400)
        self.wdw_root = wdw_root
        self.app = app
        self.bind('<Destroy>', self.kill_root)

        self.task_list = task_list
        for task in self.task_list:
            tk.Label(self, text=task, font=('Ariel', 18, 'bold'), bg=self.rand_color()).pack(fill=tk.BOTH, expand=True)
        self.btn_end = tk.Button(self, text="Tasks Finished", font=('Ariel', 16), bg="Green", command=self.end_tasks)
        self.btn_end.pack()
        self.save_state()

    def end_tasks(self):
        if self.app is None:
            self.app = MainApplication(self.wdw_root)
        self.unbind('<Destroy>')
        self.app.end_day()
        self.destroy()

    def kill_root(self, event):
        if event.widget == self and self.wdw_root.winfo_exists():
            self.wdw_root.destroy()

    def save_state(self):
        with open("rec/data.json", 'w') as data_file:
            json.dump(self.task_list, data_file)

    def rand_color(self):
        r = lambda: random.randint(0, 255)
        return '#%02X%02X%02X' % (r(), r(), r())


# 886 x 646
class MainApplication:
    """
        Manages the main window of the app

        ...

        Attributes
        ----------
        tasks : list
            list of task name strings
        fme_bg : tk.Frame
            frame that holds all widgets in main window
        parent : tk.TK()
            root window of app
        lbl_bg : tk.Label
            label that contains background image
        cnv_chat : ChatCanvas
            ChatCanvas object that holds chat messages
        entry : tk.Entry
            entry for sending messages

        Methods
        -------
        gather_info():
            requests tasks in ChatCanvas

        end_day():
            Sends goodbye message and instants exit button

        exit():
            deletes json data file and exits app

        input_tasks():
            prepares message for sending to ChatCanvas

        create_list():
            instants TaskWindow and hides main window
        """
    def __init__(self, parent):
        self.tasks = []
        self.fme_bg = tk.Frame(parent, bg='#0B29CA')
        self.fme_bg.columnconfigure(1, weight=1)

        parent.geometry("886x676")
        parent.resizable(False, False)
        self.parent = parent

        # setting up robot background image
        self.bg_src = Image.open('rec/mainbg.png')
        self.bg_image = ImageTk.PhotoImage(self.bg_src)
        self.lbl_bg = tk.Label(self.fme_bg, image=self.bg_image, borderwidth=0, highlightthickness=0)

        self.cnv_chat = ChatCanvas(self.fme_bg, self, bg='#0B29CA', borderwidth=0, highlightthickness=0)
        self.vBar = tk.Scrollbar(self.fme_bg, orient=tk.VERTICAL, command=self.cnv_chat.yview)
        self.cnv_chat.configure(yscrollcommand=self.vBar.set)

        self.entry = tk.Entry(self.fme_bg, state='disabled')
        self.entry.bind("<Return>", self.input_tasks)

        self.lbl_bg.grid(row=0, column=0, sticky='w')
        self.cnv_chat.grid(row=0, column=1, sticky='nsew')
        self.vBar.grid(row=0, column=2, sticky="ns")
        self.entry.grid(row=1, columnspan=2, sticky='ew')
        self.fme_bg.pack(fill=tk.BOTH, expand=True)

    def gather_info(self):
        self.cnv_chat.after(4000, self.cnv_chat.send_message("Welcome back!", True))
        self.cnv_chat.after(4000, self.cnv_chat.send_message("Please enter today's tasks, one at a time, entering in nothing when finished.", True))
        self.entry.configure(state='normal')

    def end_day(self):
        self.parent.deiconify()
        self.entry.configure(state='disabled')
        self.cnv_chat.send_message("Another day, another dollar", True)
        self.cnv_chat.send_message("Alright, I'll see ya tomorrow", True)
        self.cnv_chat.exit_btn()

    def exit(self, event=None):
        if os.path.isfile("rec/data.json"):
            os.remove("rec/data.json")
        self.parent.quit()

    def input_tasks(self, event=None):
        if len(self.entry.get()) == 0:  # all tasks have bee entered
            self.create_list()
            self.entry.unbind('<Return>')
            self.entry.configure(state='disabled')
        else:
            self.cnv_chat.send_message(self.entry.get(), False)
            self.tasks.append(self.entry.get())     # max task length and tasks length
            self.entry.delete(0, 'end')

    def create_list(self):
        wdw_tasks = TaskWindow(self.parent, self.tasks, self)
        self.refresh_cnv()
        self.parent.withdraw()

    def refresh_cnv(self):
        self.cnv_chat.delete('all')


if __name__ == '__main__':
    root = tk.Tk()
    if os.path.isfile("rec/data.json"):
        with open("rec/data.json", 'r') as data_file:
            tasks = json.load(data_file)
        root.withdraw()
        TaskWindow(root, tasks)
    else:
        MainApplication(root).gather_info()
    root.mainloop()
