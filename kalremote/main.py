import binascii
import json
import time
import traceback
from socket import timeout
from tkinter import *
from tkinter import messagebox
from tkinter import ttk
import broadlink

devices = list

c_title = "KalRemote"
c_btn_set = "Settings"
c_btn_save = "Save"
c_btn_cancel = "Cancel"
c_btn_close = "Close"
c_btn_add_button = "Add Button"
c_w_add_button = "KalRemote Button"
c_w_settings = "KalRemote Settings"
c_command_name = "Command"
c_btn_ok = "OK"
c_btn_test = "Test"
c_btn_learn = "Learn"
c_btn_device = "Discover Device"
c_l_setcat = "Choose Category"
c_l_setdevice = "Device"
t_got_command = "Success in learning the command"
t_learning_in_progress = "Press button on remote..."
t_learning_timeout = "No command recorded. Please try again"

msg_title = "KalRemote"
msg_no_devices = "No devices discovered"
msg_incorrect_device = "Problem with chosen device"
msg_try_again = "Device not responding. Please check device is on and try again"


def decor_for_broadlink(func):
    def wrapper(*args, **kargs):
        for _ in range(0, 3):
            try:
                return func(*args, **kargs)
            except timeout as e:
                pass
            except Exception as e:
                raise e
        messagebox.showerror(msg_title, msg_try_again)
    return wrapper

# You would normally put that on the App class
def show_error(*args):
    err = traceback.format_exception(*args[1:])
    print(''.join(err))
    messagebox.showerror('Exception', ''.join(err))

# but this works too
Tk.report_callback_exception = show_error


class CmdDetail(ttk.Frame):
    def __init__(self, pw, cat, mac, mode="NEW", cmd_name="", name='cmd_detail'):
        ttk.Frame.__init__(self, name=name)
        self.cmd_name = cmd_name
        self.mode = mode
        self.pack(expand=Y, fill=BOTH)
        self.cat = cat
        self.mac = mac
        self.status_string = StringVar()
        self.e_command_name = Entry

        if mode == "EXIST":
            self.cmd_code = get_cmd_code(self.cat, self.cmd_name)
        else:
            self.cmd_code = ""

        self.w = Toplevel(master=pw)
        self.w.wm_title(c_w_settings)

        self.w.update()
        self.w.geometry("+%d+%d" % (self.w.master.winfo_rootx() + 50, self.w.master.winfo_rooty() + 50))

        self.build_add_window(self.w, self.mode, self.cmd_name)

        self.w.transient(pw)  # only one window in the task bar
        self.w.grab_set()  # modal
        # #TODO
        pw.wait_window(self.w)  #

    def build_add_window(self, pw, mode, cmd):

        main_area = Frame(pw)
        l_command_name = Label(main_area, text=c_command_name)
        l_command_name.grid(row=0, column=0)  # side=LEFT)
        self.e_command_name = Entry(main_area, bd=5)
        self.e_command_name.insert(0, self.cmd_name)

        self.e_command_name.grid(row=0, column=1)  # side=RIGHT)


        Button(main_area, text=c_btn_cancel, command=pw.destroy).grid(row=2, column=0, pady=20, padx=20)
        Button(main_area, text=c_btn_ok, command=lambda arg1=pw: self.ok_cmd_details(arg1)).grid(row=2, column=1, pady=20,
                                                                                          padx=20)
        Button(main_area, text=c_btn_test, command=self.test_command).grid(row=2, column=2, pady=20, padx=20)
        Button(main_area, text=c_btn_learn, command=self.learn_command).grid(row=2, column=3, pady=20, padx=20)

        main_area.pack()#grid(row=0, column=0)

        status_area = Frame(pw)

        l_info_string = Label(status_area, textvariable = self.status_string, fg="red", padx=20, pady=10, anchor=NW)
        l_info_string.pack(side=LEFT)

        status_area.pack(side = LEFT)#grid(row = 1, column = 0)


    def learn_command(self):
        cmd_name = self.e_command_name.get()

        self.status_string.set(t_learning_in_progress)

        self.w.update()

        cmd_bytes_code = self.listen_command()

        if cmd_bytes_code != None:
            self.cmd_code = bytes_to_string(cmd_bytes_code)
            print(self.cat + " " + cmd_name + " " + self.cmd_code)
            self.status_string.set(t_got_command)
        else:
            self.status_string.set(t_learning_timeout)

        self.w.update()

    @decor_for_broadlink
    def listen_command(self):
        global devices
        index = get_device_index(self.mac)
        devices[index].auth()
        devices[index].enter_learning()

        for i in range(100):
            ir_packet = devices[index].check_data()
            print ("Testing ..." + str(ir_packet))
            if ir_packet:
                print(str(ir_packet))
                return ir_packet
            time.sleep(0.05)

            if i % 5 == 1:
                self.status_string.set(self.status_string.get() + ".")
                self.w.update()
        return None

    @decor_for_broadlink
    def test_command(self):
        global devices
        index = get_device_index(self.mac)
        devices[index].auth()
        if len(self.cmd_code) > 0:
            devices[index].send_data(string_to_bytes(self.cmd_code))  # TODO - msg if not valid command
        return 1

    def ok_cmd_details(self, w):
        global kal_config

        cat_list = list(filter(lambda x: x['name'] == self.cat, kal_config['categories']))
        if len(cat_list) == 0:
            raise Exception("Missed category '" + self.cat + "'")

        cmd_name = self.e_command_name.get()
        cmd_code = self.cmd_code
        if self.mode == "NEW":
            cat_list[0]['buttons'].append({'code': cmd_code, 'name': cmd_name})
        else:
            for index, cmd in enumerate(cat_list[0]['buttons']):
                if cmd ['name'] == self.cmd_name:
                    cmd['name'] = cmd_name
                    cmd['code'] = cmd_code
                    break
        w.destroy()


class GenSettings(ttk.Frame):
    def __init__(self, pw, name='gen_settings'):
        global kal_config
        ttk.Frame.__init__(self, name=name)
        self.master.title(c_w_settings)
        self.w = Toplevel(master=pw)
        self.w.wm_title(c_w_settings)
        self.ext_fr_cmd_set = Frame(self.w)
        self.build_set_window(self.w)
        self.w.transient(pw)  # only one window in the task bar
        self.w.grab_set()  # modal
        self.w.update()
        self.w.geometry("+%d+%d" % (self.w.master.winfo_rootx() + 50,self.w.master.winfo_rooty() + 50))

        pw.wait_window(self.w)  #
        cb_cat = ttk.Combobox
        cb_device = ttk.Combobox

    def set_device_list(self):
        global kal_config

        device_list = get_device_list()
        self.cb_device['values'] = device_list
        self.cb_device['state'] = 'readonly'
        if kal_config['categories'][0]['device_id'] in self.cb_device['values']:
            index = self.cb_device['values'].index(kal_config['categories'][0]['device_id'])
            self.cb_device.current(index)
            pass
            if len(device_list) == 1:
                self.cb_device['state'] = 'disabled'

    def build_set_window(self, pw):
        global kal_config

        cbp_device = ttk.Labelframe(pw, text=c_l_setdevice)
        Button(cbp_device, text=c_btn_device, command=self.set_device_call_back).pack(side=LEFT)
        self.cb_device = ttk.Combobox(cbp_device, values=[], state='normal')
        self.cb_device.bind("<<ComboboxSelected>>", self.device_selected)
        self.cb_device.pack(pady=5, padx=10, side=RIGHT)

        self.set_device_list()

        cbp_device.pack(in_=pw, side=TOP, pady=5, padx=10)

        category_list = get_category_list()

        cbp_cat = ttk.Labelframe(pw, text=c_l_setcat)
        self.cb_cat = ttk.Combobox(cbp_cat, values=category_list, state='readonly')
        self.cb_cat.bind("<<ComboboxSelected>>", self.category_selected)
        self.cb_cat.pack(pady=5, padx=10)

        # position and display
        cbp_cat.pack(in_=pw, side=TOP, pady=5, padx=10)

        self.ext_fr_cmd_set.pack()

        btn = Button(self.w, text=c_btn_add_button,
                     command=lambda w=self.w: self.add_cmd_call_back(w))

        # btn.grid(ipadx=20, padx=10, pady=5, sticky=W + E + N + S)
        btn.pack(ipadx=20, padx=10, pady=5)

        navigate_area = Frame(pw)
        ttk.Button(navigate_area, text=c_btn_cancel, command=pw.destroy).grid(row=0, column=0, pady=20, padx=20)
        ttk.Button(navigate_area, text=c_btn_ok,
                   command=lambda arg1=pw: self.ok_settings(arg1)).grid(row=0, column=1, pady=20, padx=20)
        navigate_area.pack()


        self.frame_cmd_set = ttk.LabelFrame(self.ext_fr_cmd_set)
        # self.frame_cmd_set.pack()

    def synch_choosen_device(self, macdev):  # TODO - give choice - do not determine index=0
        global kal_config

        index = get_device_index(macdev)
        if not devices[index].auth():
            messagebox.showinfo(msg_title, msg_incorrect_device + " " + macdev)
            return

            # TODO - NOT SUITS MULTIDEVICE
        for i in range(0, len(kal_config['categories'])):
            kal_config['categories'][i]['device_id'] = macdev

    def set_device_call_back(self):
        global kal_config
        global devices

        get_devices()

        self.set_device_list()

        if len(devices) == 0:
            return

        if len(devices) == 1 and self.cb_device.get() != None:
            self.synch_choosen_device(self.cb_device.get())

    def ok_settings(self, w):
        global kal_config

        with open("config.json", 'w') as f:
            f.write(json.dumps(kal_config, sort_keys=True, indent=4, separators=(',', ': ')))
        # TODO check status
        w.destroy()

    def add_cmd_call_back(self, pw):

        self.edit_cmd(pw, "NEW", "")

    def edit_cmd(self, pw, mode, cmd):

        cur_category = self.cb_cat.get()
        w_add = CmdDetail(pw, cur_category, self.cb_device.get(), mode, cmd)
        self.apply_category(self.cb_cat.get())

    def device_selected(self, event):
        value_of_combo = event.widget.get()
        self.synch_choosen_device(value_of_combo)
        pass

    def apply_category(self, cat):

        self.frame_cmd_set.destroy()
        self.frame_cmd_set = ttk.LabelFrame(self.ext_fr_cmd_set, text="Existing Buttons" )#TODO
        self.frame_cmd_set.pack()

        self.draw_buttons_for_set(self.frame_cmd_set, cat)

        print(cat)

    def category_selected(self, event):
        value_of_combo = event.widget.get()
        self.apply_category(value_of_combo)

    def draw_buttons_for_set(self, frame, cat):
        button_list = get_button_list(cat)
        for button in button_list:
            btn = Button(frame, text=button, pady=10,
                         command=lambda arg1=frame.master, arg2=button: self.set_command_call_back(arg1, arg2))
            btn.grid(ipadx=20, padx=10, pady=5, sticky=W + E + N + S)

    def set_command_call_back(self, pw, command):
        self.edit_cmd(pw, "EXIST", command)


class KalRemoteMain(ttk.Frame):
    def __init__(self, name='kalremote'):
        ttk.Frame.__init__(self, name=name)
        self.pack(expand=Y, fill=BOTH)
        self.master.title(c_title)
        self.frame_cmd_main = ttk.Labelframe()
        self.status_string = StringVar()
        self._create_widgets()
        self.selected_category = ''
        self.category_call_back('')
        self.status_string.set("Initializing...")
        self.update()
        get_devices()
        self.status_string.set("Initializing finished")
        self.set_device_status()

    def _create_widgets(self):
        self._create_main_control()

    def _create_main_control(self):

        main_control = Frame(self)
        main_control.grid()

        category_list = get_category_list()

        for category in category_list:
            # boldFont = Font(size=10, weight="bold")

            btn = Button(main_control, text=category, pady=10, width=8,
                         command=lambda arg=category: self.category_call_back(arg))
            btn.pack(ipadx=20, pady=5)


        setting_area = Frame(self)
        setting_area.grid(row=1)
        btn_set = Button(setting_area, text=c_btn_set, pady=20, anchor=CENTER,
                         command=lambda w=self: self.btn_set_call_back(w))
        btn_set.pack(ipadx=20, padx=20, pady=50)

        control_area = Frame(self)
        control_area.grid(row=2)
        Button(control_area, text=c_btn_close, command=self.master.destroy).grid(row=2, column=0, pady=20, padx=20)

        status_area = Frame(self)

        l_info_string = Label(status_area, textvariable = self.status_string, fg="red", padx=20, pady=10, anchor=NW)
        l_info_string.pack(side=LEFT)

        status_area.grid(row=3)#grid(row = 1, column = 0)

    def set_device_status(self):
        if len(devices) == 0 :
            self.status_string.set("No device found")
        else:
            self.status_string.set("Device found")


    def btn_set_call_back(self, pw):
        GenSettings(pw)
        load_config()
        self.set_device_status()

    def category_call_back(self, category):
        self.frame_cmd_main.destroy()
        self.frame_cmd_main = ttk.Labelframe(self, text=category)
        self.frame_cmd_main.grid(row=0, column=2, padx=30)
        self.draw_buttons(self.frame_cmd_main, category)
        self.selected_category = category

    def draw_buttons(self, frame, cat):
        button_list = get_button_list(cat)
        for button in button_list:
            btn = Button(frame, text=button, pady=10,
                         command=lambda arg=button: self.command_call_back(arg))
            btn.grid(ipadx=20, padx=10, pady=5, sticky=W + E + N + S)


    @decor_for_broadlink
    def command_call_back(self, command):

        global devices

        cat_list = list(filter(lambda x: x['name'] == self.selected_category, kal_config['categories']))

        index = get_device_index(cat_list[0]['device_id'])
        devices[index].auth()
        cmd_code = get_cmd_code(self.selected_category, command)
        devices[index].send_data(string_to_bytes(cmd_code))
        return 1


def bytes_to_string(bytes):
    return binascii.b2a_base64(bytes).decode()


def string_to_bytes(istr):
    print(istr)
    return binascii.a2b_base64(istr)


def load_config():
    global kal_config
    # TODO
    with open("config.json", 'r') as f:
        kal_config = json.loads(f.read())


def get_devices():
    global devices
    devices = broadlink.discover(timeout=5)
    if len(devices) == 0:
        messagebox.showinfo(msg_title, msg_no_devices)
        return -1
    return 1


def get_device_list():
    global devices
    device_list = []
    for index, dev in enumerate(devices):
        device_list.append(mac_to_string(devices[index].mac))
    return device_list


def get_device_index(mac):
    global devices

    for index, dev in enumerate(devices):
        if mac_to_string(dev.mac) == mac:
            return index
    return -1


def get_button_list(cat):
    global kal_config

    # TODO - kalconfig should be input for setting win
    cat_buttons = list(filter(lambda x: x['name'] == cat, kal_config['categories']))

    button_list = []

    if len(cat_buttons) == 0:
        #     raise Exception('no buttons for ' + cat)
        return button_list

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


def get_cmd_code(cat, cmd_name):
    cat_list = list(filter(lambda x: x['name'] == cat, kal_config['categories']))
    btn = list(filter(lambda x: x['name'] == cmd_name, cat_list[0]['buttons']))
    cmd_code = btn[0]['code']
    return cmd_code


def mac_to_string(bytes):
    return ':'.join('%02x' % b for b in reversed(bytes))


if __name__ == '__main__':
    load_config()
    KalRemoteMain().mainloop()
