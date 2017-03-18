from tkinter import *
from tkinter import ttk
import json
from tkinter import messagebox
import broadlink
import time

c_title = "KalRemote"
c_btn_set = "Settings"
c_btn_save = "Save"
c_btn_cancel = "Cancel"
c_btn_add_button = "Add Button"
c_w_add_button = "Add Button"
c_w_settings = "Settings"
c_command_name = "Command"
c_btn_ok = "OK"
c_btn_test = "Test"
c_btn_learn = "Learn"
c_btn_device = "Set Device"
c_l_setcat = "Choose Category"
c_l_setdevice = "Device"

selected_category = ""
frame_cmd_main = Frame
frame_cmd_set = Frame
frame_navigate_set = Frame
ind_cmd_main = 0
ind_cmd_set = 0
temp_json = json
entry_name = Entry


def get_button_list( cat):

    #TODO - kalconfig should be input for setting win
    global kal_config
    cat_buttons = list(filter(lambda x: x['name'] == cat, kal_config['categories']))

    if len(cat_buttons) == 0:
        raise Exception('no buttons for ' + cat)

    button_list = []

    for button in cat_buttons[0]['buttons']:
        button_list.append(button['name'])

    print(button_list)

    return button_list


def get_category_list():
    global kal_config
    category_list = []
    categories = kal_config['categories']
    for category in categories:
        category_list.append(category['name'])
    return category_list

class CmdDetail(ttk.Frame):

    def __init__(self, pw, mode = "NEW", cmd_name="", name='cmd_detail'):
        ttk.Frame.__init__(self, name=name)
        self.cmd_name = cmd_name
        self.mode = mode
        self.pack(expand=Y, fill=BOTH)
        # self.master.title(c_title)
        # self._create_widgets()

        w = Toplevel(master=pw)
        w.wm_title(c_w_settings)

        self.build_add_window(w, self.mode, self.cmd_name)

        w.transient(pw)  # only one window in the task bar
        w.grab_set()  # modal
        # #TODO
        pw.wait_window(w)  #

        E1 = Entry

    def build_add_window(self, pw, mode, cmd):
        L1 = Label(pw, text=c_command_name)
        L1.grid(row=0, column=0)  # side=LEFT)
        self.E1 = Entry(pw, bd=5)
        self.E1. insert(0, self.cmd_name)

        self.E1.grid(row=0, column=1)  # side=RIGHT)

        Button(pw, text=c_btn_cancel, command=pw.destroy).grid(row=1, column=0, pady=20, padx=20)
        Button(pw, text=c_btn_ok, command=pw.destroy).grid(row=1, column=1, pady=20, padx=20)
        Button(pw, text=c_btn_test, command=pw.destroy).grid(row=1, column=2, pady=20, padx=20)
        Button(pw, text=c_btn_learn, command=self.learn_command).grid(row=1, column=3, pady=20, padx=20)

    def learn_command(self):
        cmd_name = self.E1.get()
        cmd_code = self.listen_command()

        print(cmd_name + " " + cmd_code)

    def listen_command(self):
        devices = broadlink.discover(timeout=5)
        devices[0].auth()
        devices[0].enter_learning()

        time.sleep(5)

        ir_packet = devices[0].check_data()

        devices[0].send_data(ir_packet)

        print(str(devices))

        return ir_packet

    def cmd_to_string(self,ir_packet ):
        return "123"


    def test_command(self, cmd_code):
        return 1


class GenSettings(ttk.Frame):
    def __init__(self, pw, name='gen_settings'):
        ttk.Frame.__init__(self, name=name)
        self.master.title("SETT")

        w = Toplevel(master=pw)
        w.wm_title(c_w_settings)

        self.build_set_window(w)

        w.transient(pw)  # only one window in the task bar
        w.grab_set()  # modal
        # #TODO
        pw.wait_window(w)  #


    def build_set_window(self, pw):
        global kal_config

        cbp_device = ttk.Labelframe(pw, text=c_l_setdevice)
        cb_device = Button(cbp_device, text=c_btn_device, command=self.set_device_call_back).pack(side=LEFT)
        e_device = Entry(cbp_device, bd=2)
        e_device['state'] = 'disabled'

        e_device.pack(side=RIGHT)
        cbp_device.pack(in_=pw, side=TOP, pady=5, padx=10)

        category_list = get_category_list()

        cbp_cat = ttk.Labelframe(pw, text=c_l_setcat)
        cb_cat = ttk.Combobox(cbp_cat, values=category_list, state='readonly')
        cb_cat.bind("<<ComboboxSelected>>", self.category_selected)
        cb_cat.pack(pady=5, padx=10)

        # position and display
        cbp_cat.pack(in_=pw, side=TOP, pady=5, padx=10)

        ttk.Button(pw, text=c_btn_cancel, command=pw.destroy).pack() # grid(row=1, column=0, pady=20, padx=20)
        ttk.Button(pw, text=c_btn_ok, command=self.ok_settings).pack()  # grid(row=1, column=0, pady=20, padx=20)

    def set_device_call_back(self):
        devices = broadlink.discover(timeout=5)
        devices[0].auth() ###TODO - WHY


    def ok_settings(self, category, cmd_name, cmd_code, mode):
        temp_json[0]['buttons'].append({'code': cmd_code, 'name': cmd_name})

    def add_command(self, category, cmd_name, cmd_code, mode):
        temp_json[0]['buttons'].append({'code': cmd_code, 'name': cmd_name})

    def add_cmd_call_back(self, pw):

        self.edit_cmd(pw, "NEW", "")

    def edit_cmd(self, pw, mode, cmd):

        w_add = CmdDetail(pw, mode, cmd)

    def category_selected(self, event):
        global frame_cmd_set
        global ind_cmd_set
        global frame_navigate_set

        value_of_combo = event.widget.get()

        if ind_cmd_set > 0:
            frame_cmd_set.destroy()
            frame_navigate_set.destroy()
        ind_cmd_set = 1
        frame_cmd_set = Frame(event.widget.master.master)
        frame_cmd_set.pack()

        self.draw_buttons_for_set(frame_cmd_set, value_of_combo)

        print(value_of_combo)
        frame_navigate_set = Frame(event.widget.master.master)

        btn = Button(frame_navigate_set, text=c_btn_add_button, pady=10,
                     command=lambda w=event.widget.master.master: self.add_cmd_call_back(w))

        btn.grid(ipadx=20, padx=10, pady=5, sticky=W + E + N + S)

        frame_navigate_set.pack()

    def draw_buttons_for_set(self, frame, cat):
        buttons_list = get_button_list(cat)
        button_list = get_button_list(cat)
        for button in button_list:
            btn = Button(frame, text=button, pady=10,
                         command=lambda arg1=frame.master, arg2=button: self.set_command_call_back(arg1, arg2))
            # btn.pack(ipadx=20, pady=5)
            btn.grid(ipadx=20, padx=10, pady=5, sticky=W + E + N + S)




class KalRemoteMain(ttk.Frame):
    def __init__(self, name='kalremote'):
        ttk.Frame.__init__(self, name=name)
        self.pack(expand=Y, fill=BOTH)
        self.master.title(c_title)
        self._create_widgets()

    def _create_widgets(self):
        self._create_main_control()

    def _create_main_control(self):
        global selected_category

        main_control = Frame(self)
        # main_control.pack(side=TOP, fill=BOTH, expand=Y)
        main_control.grid()
        category_list = get_category_list()

        # button_area = Frame(self)
        # # button_area.pack(side=TOP, fill=BOTH, expand=Y)
        # button_area.grid(row = 0,column=2 )

        for category in category_list:
            btn = Button(main_control, text=category, pady=10,
                         command=lambda arg=category: self.category_call_back(arg))
            btn.pack(ipadx=20, pady=5)

        control_area = Frame(self)
        # control_area.pack(side=TOP, fill=BOTH, expand=Y)
        control_area.grid(row=2)
        btn_set = Button(control_area, text=c_btn_set, pady=20,
                         command=lambda w=control_area: self.btn_set_call_back(w))
        btn_set.pack(ipadx=20, padx=20, pady=50)

    def btn_set_call_back(self, pw):
        # global ind_cmd_set
        # ind_cmd_set = 0
        # w_set = Toplevel(master=pw)
        # w_set.wm_title(c_w_settings)
        #
        # self.build_set_window(w_set)
        #
        # w_set.transient(pw)  # only one window in the task bar
        # w_set.grab_set()  # modal
        #
        # pw.wait_window(w_set)  #

        w_set = GenSettings(pw)

    def category_call_back(self, category):
        global frame_cmd_main
        global ind_cmd_main

        if ind_cmd_main > 0:
            frame_cmd_main.destroy()
        ind_cmd_main = 1

        frame_cmd_main = Frame(self)
        # button_area.pack(side=TOP, fill=BOTH, expand=Y)
        frame_cmd_main.grid(row=0, column=2)
        self.draw_buttons(frame_cmd_main, category)


    def draw_buttons(self, frame, cat):

        button_list = get_button_list(cat)
        for button in button_list:
            btn = Button(frame, text=button, pady=10,
                         command=lambda arg=button: self.command_call_back(arg))
            # btn.pack(ipadx=20, pady=5)
            btn.grid(ipadx=20, padx=10, pady=5, sticky=W + E + N + S)


    def set_command_call_back(self, pw, command):
        self.edit_cmd(pw, "EXIST", command)



    def command_call_back(self, command):

        messagebox.showinfo("Hello Python", "Command was " + command)


def load_config():
    global kal_config
    # TODO
    with open("config.json", 'r') as f:
        kal_config = json.loads(f.read())


if __name__ == '__main__':
    load_config()
    KalRemoteMain().mainloop()


