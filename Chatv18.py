import customtkinter
import tkinter as tk
import socket
import threading
import time
import pickle
from PIL import Image
import os
from custom_hovertip import CustomTooltipLabel
from playsound import playsound
import json




login_username = "default"
my_username = None
client_socket = None
text_to_send = None

message_to_send = None
send_message = False

client_instance = None
chat_instance = None

stop_client_thread = False

server_instance = None
server_thread = None
stop_server_thread = False

is_server = False  # global var to tell if user is server or not, will affect interface

sash_color = "#8BB4DC"

# Keys to read from library text file with JSON
# UITheme
# ChatText
# EntryText
# SendReceiveSounds
# JoinLeaveSounds

# settings library
settings = {}

# read from settings file txt json file
with open('settings.txt', 'r') as settings_file:
     settings = json.loads(settings_file.read())
     #print(settings)

# user settings variables
ui_theme = settings['UITheme']
chat_text_size = int(settings['ChatText'])
entry_text_size = int(settings['EntryText'])
send_receive_sounds_on = settings['SendReceiveSounds']
join_leave_sounds_on = settings['JoinLeaveSounds']

# Get my IP address
MyIP = socket.gethostbyname(socket.gethostname())
#print("Your Computer IP Address is: "+MyIP)
ServerIP = None
chat_user_list = []

customtkinter.set_appearance_mode(settings['UITheme']) # set theme from settings file
customtkinter.set_default_color_theme("dark-blue")



################################################################
# Login UI
################################################################


class LoginUI(customtkinter.CTk):
    """ Class that is an object"""
    global client_instance

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        #window['background']='#363636'
        #window.state('zoomed')
        self.geometry("280x310")
        self.minsize(280,310)
        self.title("Chat")
        self.after(201, lambda :self.wm_iconbitmap('bubble_icon.ico'))  # strange code required to change window icon

        self.help_window = None

        self.frame = customtkinter.CTkFrame(self)
        self.frame.pack(pady=32, padx=30, ipady=8, fill="both", expand=True)

        self.label = customtkinter.CTkLabel(master=self.frame, text="Chat Login", width=180)
        self.label.pack(pady=3, padx=10)

        self.button_server = customtkinter.CTkButton(master=self.frame, text="Server", fg_color=("#8BB4DC"), hover=None, command=self.server)
        self.button_server.pack(pady=3, padx=10, fill="x")

        self.button_client = customtkinter.CTkButton(master=self.frame, text="Client", fg_color=("#8BB4DC"), hover=None, command=self.client)
        self.button_client.pack(pady=3, padx=10, fill="x")

        # spacer
        self.separator = customtkinter.CTkFrame(master=self.frame, height=5)
        self.separator.pack(pady=10, padx=10, fill="x")

        self.entry1 = customtkinter.CTkEntry(master=self.frame, placeholder_text="Username")
        self.entry1.pack(pady=3, padx=10, fill="x")



        #entry2_server = customtkinter.CTkEntry(master=frame, placeholder_text="Password", show="*")
        self.entry2_server = customtkinter.CTkEntry(master=self.frame, placeholder_text="My Local IP:")
        #define entry2_client and login button
        self.entry2_client = customtkinter.CTkEntry(master=self.frame, placeholder_text="Client IP:")

        # frame login and help "?" buttons
        self.entry_login_help_frame = customtkinter.CTkFrame(master=self.frame, fg_color="transparent")
        self.button_login_client = customtkinter.CTkButton(master=self.entry_login_help_frame, text="Login", command=self.login_client)
        self.button_login_server = customtkinter.CTkButton(master=self.entry_login_help_frame, text="Start Server", command=self.login_server)
        self.info_button = customtkinter.CTkButton(master=self.entry_login_help_frame, text="?", width=37, command=self.open_help_window)

        self.entry1.focus_set()
               
        #select default frame (server or client)
        LoginUI.select_frame_by_name(self, "Server")
        self.bind('<Return>', lambda event=None: self.button_login_server.invoke())  # bind enter key to login button



    def login_client(self):
        global login_username
        global client_instance
        global is_server
        global ServerIP
        
        if self.entry1.get() >= str(1) and self.entry2_client.get() >= str(1):
            login_username = self.entry1.get()
            ServerIP = self.entry2_client.get()
            print("Login Client")
            print(self.entry1.get())
            print(self.entry2_client.get())

            is_server = False
            client_instance = StartClient()

            self.change() # destory LoginUI and switch to ChatUI
        else:
            print("Username and Server IP required")

    def login_server(self):
        global login_username
        global client_instance
        global server_thread
        global server_instance
        global is_server

        if self.entry1.get() >= str(1):
            login_username = self.entry1.get()
            #print("Login Server")
            #print(self.entry1.get())
            #print("Server IP is: "+MyIP)

            is_server = True
            server_instance = StartServer()
            client_instance = StartClient()
            self.change() # destory LoginUI and switch to ChatUI

        else:
            print("Username required")

    def server(self):
        self.select_frame_by_name("Server")

    def client(self):
        self.select_frame_by_name("Client")



    def select_frame_by_name(self, name):

        # set button color for selected button
        self.button_server.configure(fg_color=("#3A7EBF") if name == "Server" else "#8BB4DC")   
        self.button_client.configure(fg_color=("#3A7EBF") if name == "Client" else "#8BB4DC")

        # show selected frame
        if name == "Server":
            #entry2 = customtkinter.CTkEntry(master=frame, placeholder_text="Password", show="*")
            self.entry2_server.forget()
            self.entry2_client.forget()
            self.button_login_client.grid_forget()
            self.button_login_server.forget()
            self.info_button.forget()
            self.entry_login_help_frame.forget()
            self.entry2_server = customtkinter.CTkEntry(master=self.frame, placeholder_text="Server Address: "+MyIP)
            self.entry2_server.configure(state="disabled")
            self.entry2_server.pack(pady=3, padx=10, fill="x")
            self.entry_login_help_frame.pack(pady=3, padx=10, fill="x")
            self.entry_login_help_frame.grid_columnconfigure(0, weight=1)
            self.button_login_server.grid(row=0, column=0, sticky=tk.EW)
            self.info_button.grid(row=0, column=1, sticky=tk.E, padx=3)
            # binds
            self.bind('<Return>', lambda event=None: self.button_login_server.invoke())  # bind enter key to login button

        if name == "Client":
            self.entry2_server.forget()
            self.entry2_client.forget()
            self.button_login_server.grid_forget()
            self.button_login_client.forget()
            self.info_button.forget()
            self.entry_login_help_frame.forget()
            self.entry2_client = customtkinter.CTkEntry(master=self.frame, placeholder_text="Connect to IP:")
            self.entry2_client.pack(pady=3, padx=10, fill="x")
            self.entry_login_help_frame.pack(pady=3, padx=10, fill="x")
            self.button_login_client.grid(row=0, column=0, sticky=tk.EW)
            self.info_button.grid(row=0, column=1, sticky=tk.E, padx=3)
            # binds
            self.bind('<Return>', lambda event=None: self.button_login_client.invoke())  # bind enter key to login button


    # change from login window to main chat window
    def change(self):
        global chat_instance

        print("Switching to Chat Interface /n")

        self.withdraw() # hide login window (which is the main Ctk window, only one main window allowed... the rest must be toplevel)

        chat_instance = ChatUI(logout_command=self.show_window) # start chat UI, pass show_window command to ChatUI
        if customtkinter.get_appearance_mode() == "Light":
            chat_instance.sash_color_light()
        if customtkinter.get_appearance_mode() == "Dark":
            chat_instance.sash_color_dark()

    def show_window(self):
        self.deiconify() # show the hidden (withdraw()) login window

    def open_help_window(self):
        if self.help_window is None or not self.help_window.winfo_exists():
            self.help_window = HelpWindow(self)  # create window if its None or destroyed
            self.help_window.focus()
        else:
            self.help_window.focus()  # if window exists focus it
            


#########################
# scrollable frame class
#########################

class ScrollableUserFrame(customtkinter.CTkScrollableFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)

        self.user_list = []
    
    #### methods for updating GUI user list

    def update_user_list(self, item_list):

        if len(self.user_list) > 0:
            self.remove_item()

        self.user_list = []

        for item in item_list:
            self.add_item(item)

    def remove_item(self):
        for label in self.user_list:
            label.destroy()

    def add_item(self, item):
        label = customtkinter.CTkLabel(self, text=item, fg_color=("#8BB4DC", "#8BB4DC"), corner_radius=5)
        label.pack(fill=tk.BOTH, expand=True, anchor=tk.NW, pady=1)
        self.user_list.append(label)

    #############



################################################################
# Chat UI
################################################################


class ChatUI(customtkinter.CTkToplevel):
    def __init__(self, logout_command, *args, **kwargs):
        super().__init__(*args, **kwargs)
        global is_server
        global ServerIP
        global chat_user_list
        global sash_color
        global chat_text_size
        global entry_text_size
        global send_receive_sounds_on
        global join_leave_sounds_on

        self.logout_command = logout_command
        self.geometry("600x400")
        self.frame = customtkinter.CTkFrame(self)
        self.frame.pack(fill=tk.BOTH)
        self.after(201, lambda :self.wm_iconbitmap('bubble_icon.ico'))  # strange code required to change window icon
        self.title("Chat")
        self.protocol("WM_DELETE_WINDOW", self.logout_to_login_window)
        
        # determine if toplevel settings window is open
        self.toplevel_window = None 

        # binds
        self.bind('<Return>', lambda event:self.send_button())

        # create moveable panes
        self.paned_window = tk.PanedWindow(master=self.frame, sashwidth=3, bg=sash_color, bd=0)


        self.list_pane = tk.PanedWindow(master=self.paned_window, orient=tk.HORIZONTAL, sashwidth=0, width=100, bg=sash_color)
        self.paned_window.add(self.list_pane, minsize=109)

        self.chat_pane = tk.PanedWindow(master=self.paned_window, orient=tk.VERTICAL, sashwidth=5, bg=sash_color)
        self.paned_window.add(self.chat_pane, minsize=70)

        self.chat_log_frame = customtkinter.CTkFrame(master=self.chat_pane)
        self.chat_pane.add(self.chat_log_frame, minsize=40)

        self.chat_entry_frame = customtkinter.CTkFrame(master=self.chat_pane)
        self.chat_pane.add(self.chat_entry_frame, minsize=40)

        self.chat_entry = customtkinter.CTkTextbox(master=self.chat_entry_frame, border_width=2, font=('', entry_text_size))
        self.chat_entry.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # configure chat_entry to have note to user to "type here to chat"
        self.chat_entry.bind("<FocusIn>", lambda event:self.clear_type_here())
        self.chat_entry.insert("1.0", text="Type here to chat...")
        self.chat_entry.bind("<FocusOut>", lambda event:self.add_type_here())

        self.chat_send_button = customtkinter.CTkButton(master=self.chat_entry_frame, width=50, text="Send", command=self.send_button)
        self.chat_send_button.pack(side=tk.RIGHT, fill=tk.Y)

        # add frame to left pane for customtkinter
        self.list_frame = customtkinter.CTkFrame(master=self.list_pane, corner_radius=0, width=100)
        self.list_frame.pack(expand=True, fill=tk.BOTH)

        # colors #3A7EBF  #8BB4DC

        # create frame to place list of users as labels
        self.scrollable_user_frame = ScrollableUserFrame(master=self.list_frame, width=20, fg_color="transparent", label_text="Chat Room:")
        self.scrollable_user_frame.pack(fill=tk.BOTH, expand=True, anchor=tk.NW)

        self.user_list = []  # creat list to hold users

        self.logged_in_as_frame = customtkinter.CTkFrame(self.list_frame)
        self.logged_in_as_frame.pack(anchor=tk.SW, padx=5, pady=5)



        ###### custom image
        #load and create icon images
        current_path = os.path.dirname(os.path.realpath(__file__))
        self.user_image = customtkinter.CTkImage(Image.open(current_path + "/user_icon_2.png"))
        self.connector_image = customtkinter.CTkImage(Image.open(current_path + "/connector_icon_2.png"))
        ##############


        # create settings window button
        self.settings_button = customtkinter.CTkButton(self.logged_in_as_frame, text="Settings", command=self.open_settings_window, width=14)
        #self.settings_button.pack(side=tk.LEFT)
        self.settings_button.grid(row = 0, column = 0, pady = 2)

        # create user info button
        self.user_info_button = customtkinter.CTkButton(self.logged_in_as_frame, text=None, width=14, image=self.user_image)
        #self.user_info_button.pack(side=tk.LEFT, padx=1)
        self.user_info_button.grid(row = 0, column = 1, pady = 2)
        self.user_info_tooltip = CustomTooltipLabel(anchor_widget=self.user_info_button, text=("Chatting as:\n"+login_username), hover_delay=5, font=('', 12))

        # create logout button
        self.logout_button = customtkinter.CTkButton(self.logged_in_as_frame, text="Logout", command=self.logout_to_login_window, width=60)
        #self.logout_button.pack(side=tk.BOTTOM)
        self.logout_button.grid(row = 1, column = 0, pady = 2)
      
        
        
        # create connection info button
        if is_server == True:
            self.server_info_button = customtkinter.CTkButton(self.logged_in_as_frame, text=None, image=self.connector_image, width=14)
            self.server_info_button.grid(row = 1, column = 1, pady = 2)
            self.server_tooltip = CustomTooltipLabel(anchor_widget=self.server_info_button, text=("Hosting Server:\n"+MyIP), hover_delay=5, font=('', 12))

        if is_server == False:
            self.server_info_button = customtkinter.CTkButton(self.logged_in_as_frame, text=None, image=self.connector_image, width=14)
            self.server_info_button.grid(row = 1, column = 1, pady = 2)
            self.server_tooltip = CustomTooltipLabel(anchor_widget=self.server_info_button, text=("Connected to: "+ServerIP), hover_delay=5, font=('', 12))
        

        # create chat log text box
        self.chat_log_text = customtkinter.CTkTextbox(master=self.chat_log_frame, height=340, corner_radius=15, font=('', chat_text_size))
        self.chat_log_text.pack(expand=True, fill=tk.BOTH)
        self.chat_log_text.configure(state=tk.DISABLED)


        self.paned_window.pack(anchor=tk.NW, expand=True, fill=tk.BOTH, ipadx=20, ipady=4)

 

    def open_settings_window(self):
        if self.toplevel_window is None or not self.toplevel_window.winfo_exists():
            self.toplevel_window = SettingsWindow(self)  # create window if its None or destroyed
            self.toplevel_window.focus()
        else:
            self.toplevel_window.focus()  # if window exists focus it



    def send_button(self):
        global text_to_send
        global message_to_send
        global send_message

        # check if text is entered by user or the default "Type here to chat..."
        if self.chat_entry.get("1.0", tk.END) >= str(1) and self.chat_entry.get("1.0", tk.END) != str("Type here to chat..."+'\n'):

            # send text to client send thread
            send_message = True
            message_to_send = self.chat_entry.get("1.0", 'end-2c')
            client_instance.write()
            self.chat_entry.delete("1.0", tk.END)
            #print("sent")

        else:
            print("text required")


    def clear_type_here(self):
        # check if text is entered by user or the default "Type here to chat..."
        if self.chat_entry.get("1.0", tk.END) == str("Type here to chat..."+'\n'):
            #print("clearing text")
            self.chat_entry.delete("1.0", tk.END)
        else:
            pass


    def add_type_here(self):
        if self.chat_entry.get("1.0", tk.END) <= str(0):
            self.chat_entry.delete("1.0", tk.END)
            self.chat_entry.insert("1.0", text="Type here to chat...")
            self.chat_entry.configure(takefocus=1)
        else:
            pass

    def receive_text_from_sockets(self, message):
        global send_receive_sounds_on

        self.message = message
        self.chat_log_text.configure(state=tk.NORMAL) # allows textbox to be modified
        self.chat_log_text.insert(tk.END, self.message+'\n')  # "end-2c" is needed to remove the extra return always in a text box, and the second return created from the enter keybinding
        self.chat_log_text.configure(state=tk.DISABLED) # turns off textbox from being modified
        if send_receive_sounds_on is True:
            playsound('Windows Message Nudge.wav', block=False) # play sound when a message is received


    def sash_color_dark(self):
        global sash_color
        sash_color = "#04182F"
        self.paned_window.configure(bg=sash_color)
        self.chat_pane.configure(bg=sash_color)
        self.list_pane.configure(bg=sash_color)

    def sash_color_light(self):
        global sash_color
        sash_color = "#D9D9D9"
        self.paned_window.configure(bg=sash_color)
        self.chat_pane.configure(bg=sash_color)
        self.list_pane.configure(bg=sash_color)

    
    def change_chat_log_text_size(self, size):
        self.chat_log_text.configure(font=('', size))
    
    def change_chat_entry_text_size(self, size):
        self.chat_entry.configure(font=('', size))

    def share_chat_text_size(self):
        self.chat_log_text.cget()
        return


    # method to go back to the login UI
    def logout_to_login_window(self):
        global client_instance
        global server_instance

        # close settings window if open
        try:
            if self.toplevel_window.winfo_exists():
                self.toplevel_window.destroy()
        except:
            pass

        #del client_instance
        client_instance.client_disconnect()
        if is_server == True:
            server_instance.server_disconnect()

        self.frame.destroy()
        self.destroy()
        print("Switching to Login Interface")
        # show the hidden main window (login window)
        window.show_window()





#########################################################
# Help Toplevel Window
#########################################################

class HelpWindow(customtkinter.CTkToplevel):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        global ui_theme
        global chat_text_size
        global entry_text_size
        global send_receive_sounds_on
        global join_leave_sounds_on

        self.geometry(f"325x390+760+340")
        self.resizable(False,False)
        self.after(201, lambda :self.wm_iconbitmap('bubble_icon.ico'))  # strange code required to change window icon
        self.title("Help")
        
        self.main_settings_frame = customtkinter.CTkScrollableFrame(self, label_text="Using Chat")
        self.main_settings_frame.pack(padx=10, pady=10, fill=tk.BOTH, expand=True, anchor=tk.CENTER)

        self.help_text_label = customtkinter.CTkLabel(self.main_settings_frame, justify='left', font=('', 14),
                                                        text="Chat allows you to start a chat server and immediately join the server with a username. You may also join a friend’s server as a client. Chat can essentially be used as a P2P chat, or as one big chat room for friends, family or coworkers.\n\n\nHosting a Server:\n\nStart a server by clicking “Server”, entering a username, and clicking “Start Server”. The server address will show below the username field in the login dialogue, or by hovering your mouse cursor over the connection info button in the chat window next to the logout button. The IP address provided will be your computers local IP address. Share your local IP address with others on your local network to allow them to connect to the server as clients.\n\nIf you would like to host a server and allow clients to connect via the internet you may need to forward port 5555 on your firewall/router to your computers local IP address. Then you will need to share your public IP address with others. A simple web search of “What’s My IP” will display your public IP address.\n\n\nJoining a Server:\n\nIf connecting to a server on a home or office network; ask for the server’s local IP address. If connecting to a server over the internet; ask for the server’s public IP address.\n\nJoin a server as a client by clicking “Client”, entering a username, entering the IP address provided by the server host, and clicking “Login”.\n")
        self.help_text_label.pack()
        self.help_text_label.bind('<Configure>', lambda e: self.help_text_label.configure(wraplength=self.help_text_label.winfo_width()))





#########################################################
# Settings Toplevel Window
#########################################################

class SettingsWindow(customtkinter.CTkToplevel):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        global ui_theme
        global chat_text_size
        global entry_text_size
        global send_receive_sounds_on
        global join_leave_sounds_on

        self.geometry(f"250x315+760+340")
        self.minsize(250, 315)
        self.after(201, lambda :self.wm_iconbitmap('bubble_icon.ico'))  # strange code required to change window icon
        self.title("Settings")
        
        self.main_settings_frame = customtkinter.CTkFrame(self)
        self.main_settings_frame.pack(padx=10, pady=10, fill=tk.BOTH, expand=True, anchor=tk.CENTER)

        self.main_settings_frame.grid_columnconfigure(0, weight=1)
        self.main_settings_frame.grid_rowconfigure(0, weight=1)
        self.main_settings_frame.grid_rowconfigure(1, weight=1)
        self.main_settings_frame.grid_rowconfigure(2, weight=1)

        self.theme_frame = customtkinter.CTkFrame(self.main_settings_frame)
        self.theme_frame.grid(row=0, column=0, sticky=tk.NSEW)

        self.theme_label = customtkinter.CTkLabel(self.theme_frame, text="UI Theme:")
        self.theme_label.pack()
        
        
        self.optionmenu_var = customtkinter.StringVar(value=f"{ui_theme}")  # set initial value
        self.theme_options = customtkinter.CTkOptionMenu(self.theme_frame, values=["Dark Mode", "Light Mode", "System Match"],
                                            command=self.optionmenu_callback, variable=self.optionmenu_var) 
        self.theme_options.pack()

        self.text_frame = customtkinter.CTkFrame(self.main_settings_frame)
        self.text_frame.grid(row=1, column=0, pady=5, sticky=tk.NSEW)
        
        self.log_text_label = customtkinter.CTkLabel(self.text_frame, text=f"Chat Text Size: {chat_text_size}")
        self.log_text_label.pack()
        self.log_text_size_slider = customtkinter.CTkSlider(self.text_frame, from_=5, to=32, number_of_steps=27, command=self.log_text_slider_event)
        self.log_text_size_slider.pack(pady=2)
        self.log_text_size_slider.set(chat_text_size)

        self.entry_text_label = customtkinter.CTkLabel(self.text_frame, text=f"Entry Text Size: {entry_text_size}")
        self.entry_text_label.pack()
        self.entry_text_size_slider = customtkinter.CTkSlider(self.text_frame, from_=5, to=32, number_of_steps=27,command=self.entry_text_slider_event)
        self.entry_text_size_slider.pack(pady=2)
        self.entry_text_size_slider.set(entry_text_size)

        self.sounds_frame = customtkinter.CTkFrame(self.main_settings_frame)
        self.sounds_frame.grid(row=2, column=0, sticky=tk.NSEW)

        self.sounds_label = customtkinter.CTkLabel(self.sounds_frame, text="Sounds:")
        self.sounds_label.grid(row=0, column=0, sticky=tk.W, padx=10)


        self.all_sound_switch = customtkinter.CTkSwitch(self.sounds_frame, text="All", command=self.turn_off_all_sounds)
        self.all_sound_switch.grid(row=1, column=0, sticky=tk.W, padx=10)
        if send_receive_sounds_on and join_leave_sounds_on is True:
            self.all_sound_switch.select(1)
        else:
            self.all_sound_switch.deselect(0)


        self.send_sound_switch = customtkinter.CTkSwitch(self.sounds_frame, text="Send & Receive", command=self.toggle_send_receive_sounds)
        self.send_sound_switch.grid(row=2, column=0, sticky=tk.W, padx=10)
        if send_receive_sounds_on is True:
            self.send_sound_switch.select(1)
        if send_receive_sounds_on is False:
            self.send_sound_switch.deselect(0)


        self.join_sound_switch = customtkinter.CTkSwitch(self.sounds_frame, text="Join & Leave", command=self.toggle_join_leave_sounds)
        self.join_sound_switch.grid(row=3, column=0, sticky=tk.W, padx=10)
        if join_leave_sounds_on is True:
            self.join_sound_switch.select(1)
        if join_leave_sounds_on is False:
            self.join_sound_switch.deselect(0)



    def turn_off_all_sounds(self):
        global send_receive_sounds_on
        global join_leave_sounds_on
        global settings

        if self.all_sound_switch.get() == 0: # check state of switch to control all
            # turn all off
            self.send_sound_switch.deselect(0)
            self.join_sound_switch.deselect(0)
            send_receive_sounds_on = False
            join_leave_sounds_on = False

            # set dict values for settings dictionary to write to file
            settings['SendReceiveSounds'] = send_receive_sounds_on
            settings['JoinLeaveSounds'] = join_leave_sounds_on

            # write settings to json settings txt file
            with open('settings.txt', 'w') as settings_file:
                settings_file.write(json.dumps(settings))


        if self.all_sound_switch.get() == 1:  # check state of switch to control all
            # turn all on
            self.send_sound_switch.select(1)
            self.join_sound_switch.select(1)
            send_receive_sounds_on = True
            join_leave_sounds_on = True

            # set dict values for settings dictionary to write to file
            settings['SendReceiveSounds'] = send_receive_sounds_on
            settings['JoinLeaveSounds'] = join_leave_sounds_on

            # write settings to json settings txt file
            with open('settings.txt', 'w') as settings_file:
                settings_file.write(json.dumps(settings))


    def toggle_send_receive_sounds(self):
        global send_receive_sounds_on
        global settings

        if self.send_sound_switch.get() == 0:
        # turn off sound
            send_receive_sounds_on = False
            self.all_sound_switch.deselect(0)  # turn all sounds switch off

            # set dict values for settings dictionary to write to file
            settings['SendReceiveSounds'] = send_receive_sounds_on

            # write settings to json settings txt file
            with open('settings.txt', 'w') as settings_file:
                settings_file.write(json.dumps(settings))

        if self.send_sound_switch.get() == 1:
        # turn on sound
            send_receive_sounds_on = True

            # set dict values for settings dictionary to write to file
            settings['SendReceiveSounds'] = send_receive_sounds_on

            # write settings to json settings txt file
            with open('settings.txt', 'w') as settings_file:
                settings_file.write(json.dumps(settings))

        if self.send_sound_switch.get() == 1 and self.join_sound_switch.get() == 1:
            self.all_sound_switch.select(1)


    def toggle_join_leave_sounds(self):
        global join_leave_sounds_on
        global settings

        if self.join_sound_switch.get() == 0:
        # turn off sound
            join_leave_sounds_on = False
            self.all_sound_switch.deselect(0)  # turn all sounds switch off

            # set dict values for settings dictionary to write to file
            settings['JoinLeaveSounds'] = join_leave_sounds_on

            # write settings to json settings txt file
            with open('settings.txt', 'w') as settings_file:
                settings_file.write(json.dumps(settings))

        if self.join_sound_switch.get() == 1:
        # turn on sound
            join_leave_sounds_on = True
            
            # set dict values for settings dictionary to write to file
            settings['JoinLeaveSounds'] = join_leave_sounds_on

            # write settings to json settings txt file
            with open('settings.txt', 'w') as settings_file:
                settings_file.write(json.dumps(settings))
        
        if self.send_sound_switch.get() == 1 and self.join_sound_switch.get() == 1:
            # turn all sounds switch to on
            self.all_sound_switch.select(1)

    def optionmenu_callback(self, choice):
        global ui_theme
        global settings

        #print("optionmenu dropdown clicked:", choice)
        if choice == "System Match":
            customtkinter.set_appearance_mode("system")
            if customtkinter.get_appearance_mode() == "Light":
                chat_instance.sash_color_light()

            elif customtkinter.get_appearance_mode() == "Dark":
                chat_instance.sash_color_dark()

            # set UI theme variable
            ui_theme = "System"

            # set dict values for settings dictionary to write to file
            settings['UITheme'] = ui_theme

            # write settings to json settings txt file
            with open('settings.txt', 'w') as settings_file:
                settings_file.write(json.dumps(settings))
        
        if choice == "Dark Mode":
            customtkinter.set_appearance_mode("dark")
            chat_instance.sash_color_dark()

            # set UI theme variable
            ui_theme = "Dark"

            # set dict values for settings dictionary to write to file
            settings['UITheme'] = ui_theme

            # write settings to json settings txt file
            with open('settings.txt', 'w') as settings_file:
                settings_file.write(json.dumps(settings))
                
        if choice == "Light Mode":
            customtkinter.set_appearance_mode("light")
            chat_instance.sash_color_light()

            # set UI theme variable
            ui_theme = "Light"

            # set dict values for settings dictionary to write to file
            settings['UITheme'] = ui_theme

            # write settings to json settings txt file
            with open('settings.txt', 'w') as settings_file:
                settings_file.write(json.dumps(settings))


    def log_text_slider_event(self, value):
        global chat_text_size

        value = self.log_text_size_slider.get()
        chat_instance.change_chat_log_text_size(size=value)
        chat_text_size = int(value)
        self.log_text_label.configure(text=f"Chat Text Size: {chat_text_size}")
        #print(value)

        # set dict values for settings dictionary to write to file
        settings['ChatText'] = chat_text_size

        # write settings to json settings txt file
        with open('settings.txt', 'w') as settings_file:
            settings_file.write(json.dumps(settings))


    def entry_text_slider_event(self, value):
        global entry_text_size

        value = self.entry_text_size_slider.get()
        chat_instance.change_chat_entry_text_size(size=value)
        entry_text_size = int(value)
        self.entry_text_label.configure(text=f"Entry Text Size: {entry_text_size}")
        #print(value)

        # set dict values for settings dictionary to write to file
        settings['EntryText'] = entry_text_size

        # write settings to json settings txt file
        with open('settings.txt', 'w') as settings_file:
            settings_file.write(json.dumps(settings))






############################################################
# server
############################################################


class StartServer():

    def __init__(self):
        global MyIP

        # Connection Data
        self.host = '127.0.0.1'
        self.port = 5555
        ServerIP = MyIP

        # Starting Server
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.bind((MyIP, self.port))
        self.server.listen()

        # Lists For Clients and Their Nicknames
        self.clients = []
        self.nicknames = []


        # start receive thread
        self.server_receive_thread = threading.Thread(target=self.receive, name="Server Receive Thread")
        self.server_receive_thread.start()



    # Sending Messages To All Connected Clients
    def broadcast(self, message):
        self.broadcast_message = message
        msg = pickle.dumps(self.broadcast_message)  #.dumps not .dump
        msg = bytes(f"{len(msg):<{10}}", 'ascii')+msg
        #print("broadcast pickled!", msg)
        for client in self.clients:
            client.send(msg)
            #print("server broadcast message is... ", message)



    # Handling Messages From Clients
    def handle(self, client):
        global stop_server_thread
        HEADERSIZE = 10

        while stop_server_thread == False:
            try:
                message = client.recv(1024)
                
                # de-pickle the incoming message
                message = pickle.loads(message[HEADERSIZE:])
                
                # Broadcasting Messages
                # print("server handle message is... ", message)
                if message != 'UPDATE_CLIENTS' or 'CLIENTS' or 'NICK':
                    self.broadcast(message)

            except:
                # Removing And Closing Clients
                index = self.clients.index(client)
                self.clients.remove(client)
                client.close()
                nickname = self.nicknames[index]
                self.broadcast(['MESSAGE', ['{} left!'.format(nickname)]])
                self.nicknames.remove(nickname)
                time.sleep(.1)
                self.broadcast(['UPDATE_CLIENTS', self.nicknames])
                break



    # Starting a new client connection / Receiving / Listening Function
    def receive(self):
        global stop_server_thread

        HEADERSIZE = 10

        while stop_server_thread == False:
            try:

                # Accept Connection
                client, address = self.server.accept()
                print("Connected with {}".format(str(address)))


                # # sending a list using Pickle
                # this_list = [1, 2, 3]
                # msg = pickle.dumps(this_list)  #.dumps not .dump
                # msg = bytes(f"{len(msg):<{10}}", 'ascii')+msg
                # print("pickled!", msg)
                # client.send(msg)
                # time.sleep(.1)


                # Request And Store Nickname
                msg = pickle.dumps('NICK')  #.dumps not .dump
                msg = bytes(f"{len(msg):<{10}}", 'ascii')+msg
                #print("pickled!", msg)
                client.send(msg)
                nickname = client.recv(1024)
                
                nickname = pickle.loads(nickname[HEADERSIZE:])
                #print(nickname)

                self.nicknames.append(nickname)
                self.clients.append(client)
    

                # Print And Broadcast Nickname
                print("Nickname is {}".format(nickname))
                self.broadcast(['MESSAGE', ["{} joined!".format(nickname)]])                
                self.broadcast(["UPDATE_CLIENTS", self.nicknames])
                time.sleep(.1)


                msg = pickle.dumps(['MESSAGE', ['Connected to server!']])  #.dumps not .dump
                msg = bytes(f"{len(msg):<{10}}", 'ascii')+msg
                #print("pickled!", msg)
                client.send(msg)
                

                # Start Handling Thread For Client
                self.server_handle_thread = threading.Thread(target=self.handle, args=(client,))
                self.server_handle_thread.start()

            except:
                pass



    def server_disconnect(self):
        global stop_server_thread

        for client in self.clients:
            #print("Closing", client)
            client.close()
        stop_server_thread = True
        print("try disconnecting server")
        self.server.close()
        time.sleep(.1)
        self.server_handle_thread.join()
        print("server handle thread == ", self.server_handle_thread.is_alive())
        print("server receive thread == ", self.server_receive_thread.is_alive())
        stop_server_thread = False # reset server thread value to allow user to start server again after closing







############################################################
# client
############################################################

class StartClient():
    global lock_client
    global stop_client_thread
    global send_receive_sounds_on

    def __init__(self):
        global send_message
        global ServerIP

        if is_server:
            ServerIP = MyIP

        # Choosing Nickname
        self.nickname = login_username

        self.user_list = []

        print("starting client")

        # Connecting To Server
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client.connect((ServerIP, 5555))
        print('connecting to:', self.client.getsockopt)

        # start thread that constantly listens for text messages
        self.receive_thread = threading.Thread(target=self.receive, name="receive thread")
        self.receive_thread.start()



    # Listening to Server and Sending Nickname
    def receive(self):
        global stop_client_thread
        global lock_client
        global chat_user_list
        global send_receive_sounds_on
                
        HEADERSIZE = 10

        while stop_client_thread == False:
        
        
            try:
                
                # receive and de-pickle a message
                full_msg = b''
                msg = self.client.recv(1024)
                msglen = int(msg[:HEADERSIZE])

                #print(f"full message length: {msglen}")

                full_msg += msg
                #print("full message> ", full_msg)
                #print("full_msg len == ", len(full_msg))

                if len(full_msg)-HEADERSIZE == msglen:
                    #print("full msg recvd")
                    #print(full_msg[HEADERSIZE:])
                    message_from_server = pickle.loads(full_msg[HEADERSIZE:])
                    #print("message_from_server == ", message_from_server)
                    new_msg = True
                    full_msg = b""

                # Receive Message From Server
                # If 'NICK' Send Nickname
                message = message_from_server
                #print("client receive message is: ", message)
                
                if message == 'NICK':
                    # send nickname using pickle
                    msg = pickle.dumps(self.nickname)  #.dumps not .dump
                    msg = bytes(f"{len(msg):<{10}}", 'ascii')+msg
                    #print("pickled!", msg)
                    self.client.send(msg)
                    continue
                
                
            except:
                #print(message)
                # Close Connection When Error
                print("An error occured!")
                self.client.close()
                break


            try:
                # if a message of text is received, print it in UI
                if message[0] == 'MESSAGE':
                    # print message if there is one
                    print(' '.join(message[1]))
                    chat_instance.receive_text_from_sockets(message=''.join(message[1]))


                # if the server sends updated client list
                elif message[0] == 'UPDATE_CLIENTS':  # when index 0 == UPDATE_CLIENTS, index 1 will contain the list of updated clients
                    #print("Clients are: ", message[1])
                    # send client list to chat UI
                    chat_user_list = message[1]
                    
                    time.sleep(.4)
                    #chat_instance.update_user_list(item_list=message[1])
                    chat_instance.scrollable_user_frame.update_user_list(item_list=message[1])

                    self.user_list = ', '.join(message[1])   # read list of users, starting at index 1 

                    if join_leave_sounds_on is True:
                        playsound('Windows Logoff Sound.wav', block=False)

            except:
                pass



    # Sending Messages To Server
    def write(self):
        global message_to_send
        global send_message

        #print(self.nickname)
        #print("...sending...")
        while send_message == True:
            message = message_to_send

            # sending a message using Pickle
            # message = '{}: {}'.format(self.nickname, message_to_send)
            message = pickle.dumps(("MESSAGE", [self.nickname+": ", message_to_send]))  #.dumps not .dump
            message = bytes(f"{len(message):<{10}}", 'ascii')+message
            #print("pickled!", message)
            self.client.send(message)
            send_message = False


    # set receive event to stop receive thread & close connection
    def client_disconnect(self):
        self.client.close() # close client connection, its a thread class I think
        client_instance.receive_thread.join() # join the receive thread after ending, to resume normal programming
        print("receive thread == ", client_instance.receive_thread)
        print("disconnecting from server")





# mainloop
if __name__ == '__main__':
    window = LoginUI()
    window.mainloop()