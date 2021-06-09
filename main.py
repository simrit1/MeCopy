"""
MeCopy (Modular Extension Copy) It is a GUI for Robocopy based on independent modules 
in which you can copy, move or delete files on your computer at the same time without 
any module interfering with each other.

Copyright© W4rex / Alejandro Duarte

Github: https://github.com/w4rexx/MeCopy


"""
import sys
import os
import tkinter as tk
import shutil
import errno
import os.path
import posixpath
import fnmatch
import time
import webbrowser
import win32api
import pywintypes
import threading
import glob
import os
import shutil

from fnmatch import _compile_pattern
from configparser import ConfigParser
from tkscrolledframe import ScrolledFrame
from tkinter import ttk
from tkinter import filedialog
from tkinter import messagebox
from os.path import isdir, join
from shutil import copytree
from os import rmdir, walk
from ast import literal_eval
from PIL import ImageTk, Image
from subprocess import call
from ttkbootstrap import Style

# Monkey patch to make fnmatch accept a tuple of patterns.


def filter_patterns(names, pat):
    """Return the subset of the list NAMES that match PAT."""
    result = []
    pats = pat if isinstance(pat, tuple) else (pat,)
    matches = []
    for pat in pats:
        pat = os.path.normcase(pat)
        matches.append(_compile_pattern(pat))
    if os.path is posixpath:
        # normcase on posix is NOP. Optimize it away from the loop.
        for name in names:
            for match in matches:
                if match(name):
                    result.append(name)
                    break
    else:
        for name in names:
            for match in matches:
                if match(os.path.normcase(name)):
                    result.append(name)
                    break
    return result


fnmatch.filter = filter_patterns
# End of monkey patch for fnmatch

try:
    os.makedirs('logs')
except OSError as e:
    if e.errno != errno.EEXIST:
        raise

parser = ConfigParser()
parser.read('config.ini')

Version = ("(v.1.0)")


def raise_frame(frame):
    frame.tkraise()


root = tk.Tk()
root.title("MeCopy")
root.config(bg="#dbdbdb")
root.geometry("1280x670+35+0")
root.resizable(False, False)
root.iconbitmap("icon.ico")

Move_Screen = tk.Frame(root)
Move_Screen.config(bg="#dbdbdb")
Move_Screen.place(x=0, y=0, width=1280, height=667)

Delete_Menu_Screen = tk.Frame(root)
Delete_Menu_Screen.config(bg="#dbdbdb")
Delete_Menu_Screen.place(x=0, y=0, width=1280, height=667)

Move_Frame = tk.Frame(Move_Screen)
Move_Frame.config(bg="#dbdbdb", width=1280, height=667, padx=55, pady=20)
Move_Frame.grid(row=0, column=0)

Delete_Frame = tk.Frame(Delete_Menu_Screen)
Delete_Frame.config(bg="#dbdbdb", width=1280, height=667, padx=55, pady=20)
Delete_Frame.grid(row=0, column=0)

s = ttk.Style(root)
s.theme_use('clam')
s.configure('flat.TButton', padding=1)

estyle = ttk.Style()
estyle.element_create("plain.field", "from", "clam")
estyle.layout("EntryStyle.TEntry",
              [('Entry.plain.field', {'children': [(
                  'Entry.background', {'children': [(
                      'Entry.padding', {'children': [(
                          'Entry.textarea', {'sticky': 'nswe'})],
                          'sticky': 'nswe'})], 'sticky': 'nswe'})],
                  'border': '1', 'sticky': 'nswe'})])

estyle.configure("EntryStyle.TEntry",
                 background="#dbdbdb",
                 foreground="#373636",
                 fieldbackground="grey", relief='flat',
                 highlightthickness=1,
                 highlightbackground="#ec3c3c",
                 selectbackground="#357ebd")

estyle.layout("EntryStyle.TEntry_Paths",
              [('Entry.plain.field', {'children': [(
                  'Entry.background', {'children': [(
                      'Entry.padding', {'children': [(
                          'Entry.textarea', {'sticky': 'nswe'})],
                          'sticky': 'nswe'})], 'sticky': 'nswe'})],
                  'border': '0', 'sticky': 'nswe'})])

estyle.configure("EntryStyle.TEntry_Paths",
                 background="#dbdbdb", foreground="#3671be")

menubar = tk.Menu(root)
root.config(menu=menubar)

filemenu = tk.Menu(menubar, tearoff=0)
filemenu.add_command(label="Exit", command=root.quit)

helpmenu = tk.Menu(menubar, tearoff=0)
helpmenu.add_command(label="About...", command=lambda: [info_window()])

menubar.add_cascade(label="File", menu=filemenu)
menubar.add_cascade(label="Help", menu=helpmenu)


class EntryEx(ttk.Entry):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.menu = tk.Menu(self, tearoff=False)
        self.menu.add_command(label="Copy", command=self.popup_copy)
        self.menu.add_command(label="Cut", command=self.popup_cut)
        self.menu.add_separator()
        self.menu.add_command(label="Paste", command=self.popup_paste)
        self.bind("<Button-3>", self.display_popup)

    def display_popup(self, event):
        self.menu.post(event.x_root, event.y_root)

    def popup_copy(self):
        self.event_generate("<<Copy>>")

    def popup_cut(self):
        self.event_generate("<<Cut>>")

    def popup_paste(self):
        self.event_generate("<<Paste>>")


def callback(url):
    webbrowser.open_new(url)


def callback_2(url):
    webbrowser.open_new(url)


def info_window():
    window = tk.Toplevel(root)
    window.title("MeCopy")
    window.config(bg="#dbdbdb")
    window.geometry("500x200+420+300")
    window.resizable(False, False)
    window.iconbitmap("icon.ico")

    Logo_Img_Open = ImageTk.PhotoImage(Image.open("Images/logo.png"))
    Logo = tk.Label(window, bg="#dbdbdb", image=Logo_Img_Open)
    Logo.place(x=10, y=120)
    Logo.image = Logo_Img_Open

    link1 = tk.Label(window, text="Contact", fg="blue",
                     bg="#dbdbdb", cursor="hand2")
    link1.place(x=22, y=10)
    link1.bind(
        "<Button-1>", lambda e: callback_2(" https://github.com/w4rexx"))

    Info_Version = tk.Label(window, bg="#dbdbdb", fg="#382d2b",
                            text="MeCopy " + Version).place(x=204, y=20)
    Info_Description = tk.Label(window, bg="#dbdbdb", fg="#382d2b",
                                text="MeCopy (Modular Extension Copy) It is a GUI for Robocopy based on independent modules in which you can copy, move or delete files on your computer at the same time without any module interfering with each other.", wraplength=350).place(x=85, y=55)
    Info_Dev = tk.Label(window, bg="#dbdbdb", fg="#382d2b",
                        text="Copyright© W4rex / Alejandro Duarte").place(x=290, y=177)
    Exit_Button = ttk.Button(window, text="Close",
                             command=window.destroy).place(x=210, y=140)


# MOVE_MODULES_TITLE
Move_Module_Name_1 = tk.StringVar()
Entry_Path_1 = EntryEx(Move_Frame, font="Helvetica 10 bold", width=27,
                       style="EntryStyle.TEntry_Paths", textvariable=Move_Module_Name_1).place(x=165, y=0)
Move_Module_Name_1.set(parser.get("Path_Names", "path_name_1"))

Move_Module_Name_2 = tk.StringVar()
Entry_Path_2 = EntryEx(Move_Frame, font="Helvetica 10 bold", width=27,
                       style="EntryStyle.TEntry_Paths", textvariable=Move_Module_Name_2).place(x=165, y=112)
Move_Module_Name_2.set(parser.get("Path_Names", "path_name_2"))

Move_Module_Name_3 = tk.StringVar()
Entry_Path_3 = EntryEx(Move_Frame, font="Helvetica 10 bold", width=27,
                       style="EntryStyle.TEntry_Paths", textvariable=Move_Module_Name_3).place(x=165, y=225)
Move_Module_Name_3.set(parser.get("Path_Names", "path_name_3"))

Move_Module_Name_4 = tk.StringVar()
Entry_Path_4 = EntryEx(Move_Frame, font="Helvetica 10 bold", width=27,
                       style="EntryStyle.TEntry_Paths", textvariable=Move_Module_Name_4).place(x=165, y=345)
Move_Module_Name_4.set(parser.get("Path_Names", "path_name_4"))

Move_Module_Name_5 = tk.StringVar()
Entry_Path_5 = EntryEx(Move_Frame, font="Helvetica 10 bold", width=27,
                       style="EntryStyle.TEntry_Paths", textvariable=Move_Module_Name_5).place(x=165, y=462)
Move_Module_Name_5.set(parser.get("Path_Names", "path_name_5"))

Move_Module_Name_6 = tk.StringVar()
Entry_Path_6 = EntryEx(Move_Frame, font="Helvetica 10 bold", width=27,
                       style="EntryStyle.TEntry_Paths", textvariable=Move_Module_Name_6).place(x=755, y=0)
Move_Module_Name_6.set(parser.get("Path_Names", "path_name_6"))

Move_Module_Name_7 = tk.StringVar()
Entry_Path_7 = EntryEx(Move_Frame, font="Helvetica 10 bold", width=27,
                       style="EntryStyle.TEntry_Paths", textvariable=Move_Module_Name_7).place(x=755, y=112)
Move_Module_Name_7.set(parser.get("Path_Names", "path_name_7"))

Move_Module_Name_8 = tk.StringVar()
Entry_Path_8 = EntryEx(Move_Frame, font="Helvetica 10 bold", width=27,
                       style="EntryStyle.TEntry_Paths", textvariable=Move_Module_Name_8).place(x=755, y=225)
Move_Module_Name_8.set(parser.get("Path_Names", "path_name_8"))

Move_Module_Name_9 = tk.StringVar()
Entry_Path_9 = EntryEx(Move_Frame, font="Helvetica 10 bold", width=27,
                       style="EntryStyle.TEntry_Paths", textvariable=Move_Module_Name_9).place(x=755, y=345)
Move_Module_Name_9.set(parser.get("Path_Names", "path_name_9"))

Move_Module_Name_10 = tk.StringVar()
Entry_Path_10 = EntryEx(Move_Frame, font="Helvetica 10 bold", width=27,
                        style="EntryStyle.TEntry_Paths", textvariable=Move_Module_Name_10).place(x=755, y=462)
Move_Module_Name_10.set(parser.get("Path_Names", "path_name_10"))
# MOVE_MODULES_TITLE_END

# MOVE_MODULES_SRC_PETITION


def Get_Src_Path_1():
    Src_Path_1_Selected = filedialog.askdirectory()
    Src_Path_1.set(Src_Path_1_Selected)


Src_Path_1 = tk.StringVar()
Src_Path_1.set(parser.get("Paths_Src", "path_1"))


def Get_Src_Path_2():
    Src_Path_2_Selected = filedialog.askdirectory()
    Src_Path_2.set(Src_Path_2_Selected)


Src_Path_2 = tk.StringVar()
Src_Path_2.set(parser.get("Paths_Src", "path_2"))


def Get_Src_Path_3():
    Src_Path_3_Selected = filedialog.askdirectory()
    Src_Path_3.set(Src_Path_3_Selected)


Src_Path_3 = tk.StringVar()
Src_Path_3.set(parser.get("Paths_Src", "path_3"))


def Get_Src_Path_4():
    Src_Path_4_Selected = filedialog.askdirectory()
    Src_Path_4.set(Src_Path_4_Selected)


Src_Path_4 = tk.StringVar()
Src_Path_4.set(parser.get("Paths_Src", "path_4"))


def Get_Src_Path_5():
    Src_Path_5_Selected = filedialog.askdirectory()
    Src_Path_5.set(Src_Path_5_Selected)


Src_Path_5 = tk.StringVar()
Src_Path_5.set(parser.get("Paths_Src", "path_5"))


def Get_Src_Path_6():
    Src_Path_6_Selected = filedialog.askdirectory()
    Src_Path_6.set(Src_Path_6_Selected)


Src_Path_6 = tk.StringVar()
Src_Path_6.set(parser.get("Paths_Src", "path_6"))


def Get_Src_Path_7():
    Src_Path_7_Selected = filedialog.askdirectory()
    Src_Path_7.set(Src_Path_7_Selected)


Src_Path_7 = tk.StringVar()
Src_Path_7.set(parser.get("Paths_Src", "path_7"))


def Get_Src_Path_8():
    Src_Path_8_Selected = filedialog.askdirectory()
    Src_Path_8.set(Src_Path_8_Selected)


Src_Path_8 = tk.StringVar()
Src_Path_8.set(parser.get("Paths_Src", "path_8"))


def Get_Src_Path_9():
    Src_Path_9_Selected = filedialog.askdirectory()
    Src_Path_9.set(Src_Path_9_Selected)


Src_Path_9 = tk.StringVar()
Src_Path_9.set(parser.get("Paths_Src", "path_9"))


def Get_Src_Path_10():
    Src_Path_10_Selected = filedialog.askdirectory()
    Src_Path_10.set(Src_Path_10_Selected)


Src_Path_10 = tk.StringVar()
Src_Path_10.set(parser.get("Paths_Src", "path_10"))

Src_Title_1 = tk.Label(Move_Frame, text="Search in:", fg="#382d2b",
                       bg="#dbdbdb", font=("Arial", "12", "bold")).place(x=64, y=19)
Patch_1_Entry = EntryEx(Move_Frame, style="EntryStyle.TEntry",
                        textvariable=Src_Path_1).place(x=155, y=22)
btnFind_Path_1 = ttk.Button(Move_Frame, text="Search",
                            style="flat.TButton", command=Get_Src_Path_1).place(x=282, y=21)

Src_Title_2 = tk.Label(Move_Frame, text="Search in:", fg="#382d2b",
                       bg="#dbdbdb", font=("Arial", "12", "bold")).place(x=64, y=130)
Patch_2_Entry = EntryEx(Move_Frame, style="EntryStyle.TEntry",
                        textvariable=Src_Path_2).place(x=155, y=133)
btnFind_Path_2 = ttk.Button(Move_Frame, text="Search",
                            style="flat.TButton", command=Get_Src_Path_2).place(x=282, y=132)

Src_Title_3 = tk.Label(Move_Frame, text="Search in:", fg="#382d2b",
                       bg="#dbdbdb", font=("Arial", "12", "bold")).place(x=64, y=247)
Patch_3_Entry = EntryEx(Move_Frame, style="EntryStyle.TEntry",
                        textvariable=Src_Path_3).place(x=155, y=250)
btnFind_Path_3 = ttk.Button(Move_Frame, text="Search",
                            style="flat.TButton", command=Get_Src_Path_3).place(x=282, y=249)

Src_Title_4 = tk.Label(Move_Frame, text="Search in:", fg="#382d2b",
                       bg="#dbdbdb", font=("Arial", "12", "bold")).place(x=64, y=365)
Patch_4_Entry = EntryEx(Move_Frame, style="EntryStyle.TEntry",
                        textvariable=Src_Path_4).place(x=155, y=369)
btnFind_Path_4 = ttk.Button(Move_Frame, text="Search",
                            style="flat.TButton", command=Get_Src_Path_4).place(x=282, y=368)

Src_Title_5 = tk.Label(Move_Frame, text="Search in:", fg="#382d2b",
                       bg="#dbdbdb", font=("Arial", "12", "bold")).place(x=64, y=481)
Patch_5_Entry = EntryEx(Move_Frame, style="EntryStyle.TEntry",
                        textvariable=Src_Path_5).place(x=155, y=485)
btnFind_Path_5 = ttk.Button(Move_Frame, text="Search",
                            style="flat.TButton", command=Get_Src_Path_5).place(x=282, y=484)

Src_Title_6 = tk.Label(Move_Frame, text="Search in:", fg="#382d2b",
                       bg="#dbdbdb", font=("Arial", "12", "bold")).place(x=654, y=19)
Patch_6_Entry = EntryEx(Move_Frame, style="EntryStyle.TEntry",
                        textvariable=Src_Path_6).place(x=746, y=22)
btnFind_Path_6 = ttk.Button(Move_Frame, text="Search",
                            style="flat.TButton", command=Get_Src_Path_6).place(x=873, y=21)

Src_Title_7 = tk.Label(Move_Frame, text="Search in:", fg="#382d2b",
                       bg="#dbdbdb", font=("Arial", "12", "bold")).place(x=654, y=130)
Patch_7_Entry = EntryEx(Move_Frame, style="EntryStyle.TEntry",
                        textvariable=Src_Path_7).place(x=746, y=133)
btnFind_Path_7 = ttk.Button(Move_Frame, text="Search",
                            style="flat.TButton", command=Get_Src_Path_7).place(x=873, y=132)

Src_Title_8 = tk.Label(Move_Frame, text="Search in:", fg="#382d2b",
                       bg="#dbdbdb", font=("Arial", "12", "bold")).place(x=654, y=247)
Patch_8_Entry = EntryEx(Move_Frame, style="EntryStyle.TEntry",
                        textvariable=Src_Path_8).place(x=746, y=250)
btnFind_Path_8 = ttk.Button(Move_Frame, text="Search",
                            style="flat.TButton", command=Get_Src_Path_8).place(x=873, y=249)

Src_Title_9 = tk.Label(Move_Frame, text="Search in:", fg="#382d2b",
                       bg="#dbdbdb", font=("Arial", "12", "bold")).place(x=654, y=365)
Patch_9_Entry = EntryEx(Move_Frame, style="EntryStyle.TEntry",
                        textvariable=Src_Path_9).place(x=746, y=369)
btnFind_Path_9 = ttk.Button(Move_Frame, text="Search",
                            style="flat.TButton", command=Get_Src_Path_9).place(x=873, y=368)

Src_Title_10 = tk.Label(Move_Frame, text="Search in:", fg="#382d2b",
                        bg="#dbdbdb", font=("Arial", "12", "bold")).place(x=654, y=481)
Patch_10_Entry = EntryEx(Move_Frame, style="EntryStyle.TEntry",
                         textvariable=Src_Path_10).place(x=746, y=485)
btnFind_Path_10 = ttk.Button(
    Move_Frame, text="Search", style="flat.TButton", command=Get_Src_Path_10).place(x=873, y=484)
# MOVE_MODULES_SRC_PETITION_END

# MOVE_MODULES_DST_PETITION


def Get_Dst_Path_1():
    folder_selected1 = filedialog.askdirectory()
    Dst_Path_1.set(folder_selected1)


Dst_Path_1 = tk.StringVar()
Dst_Path_1.set(parser.get("Paths_Dst", "path_1"))


def Get_Dst_Path_2():
    folder_selected2 = filedialog.askdirectory()
    Dst_Path_2.set(folder_selected2)


Dst_Path_2 = tk.StringVar()
Dst_Path_2.set(parser.get("Paths_Dst", "path_2"))


def Get_Dst_Path_3():
    folder_selected3 = filedialog.askdirectory()
    Dst_Path_3.set(folder_selected3)


Dst_Path_3 = tk.StringVar()
Dst_Path_3.set(parser.get("Paths_Dst", "path_3"))


def Get_Dst_Path_4():
    folder_selected4 = filedialog.askdirectory()
    Dst_Path_4.set(folder_selected4)


Dst_Path_4 = tk.StringVar()
Dst_Path_4.set(parser.get("Paths_Dst", "path_4"))


def Get_Dst_Path_5():
    folder_selected5 = filedialog.askdirectory()
    Dst_Path_5.set(folder_selected5)


Dst_Path_5 = tk.StringVar()
Dst_Path_5.set(parser.get("Paths_Dst", "path_5"))


def Get_Dst_Path_6():
    folder_selected6 = filedialog.askdirectory()
    Dst_Path_6.set(folder_selected6)


Dst_Path_6 = tk.StringVar()
Dst_Path_6.set(parser.get("Paths_Dst", "path_6"))


def Get_Dst_Path_7():
    folder_selected7 = filedialog.askdirectory()
    Dst_Path_7.set(folder_selected7)


Dst_Path_7 = tk.StringVar()
Dst_Path_7.set(parser.get("Paths_Dst", "path_7"))


def Get_Dst_Path_8():
    folder_selected8 = filedialog.askdirectory()
    Dst_Path_8.set(folder_selected8)


Dst_Path_8 = tk.StringVar()
Dst_Path_8.set(parser.get("Paths_Dst", "path_8"))


def Get_Dst_Path_9():
    folder_selected9 = filedialog.askdirectory()
    Dst_Path_9.set(folder_selected9)


Dst_Path_9 = tk.StringVar()
Dst_Path_9.set(parser.get("Paths_Dst", "path_9"))


def Get_Dst_Path_10():
    folder_selected10 = filedialog.askdirectory()
    Dst_Path_10.set(folder_selected10)


Dst_Path_10 = tk.StringVar()
Dst_Path_10.set(parser.get("Paths_Dst", "path_10"))

Search_1_Path = tk.Label(Move_Frame, text="Send to:", fg="#382d2b",
                         bg="#dbdbdb", font=("Arial", "12", "bold")).place(x=77, y=46)
E2 = EntryEx(Move_Frame, style="EntryStyle.TEntry",
             textvariable=Dst_Path_1).place(x=155, y=50)
btnFind2 = ttk.Button(Move_Frame, text="Search", style="flat.TButton",
                      command=Get_Dst_Path_1).place(x=282, y=49)

Search_2_Path = tk.Label(Move_Frame, text="Send to:", fg="#382d2b",
                         bg="#dbdbdb", font=("Arial", "12", "bold")).place(x=77, y=158)
E3 = EntryEx(Move_Frame, style="EntryStyle.TEntry",
             textvariable=Dst_Path_2).place(x=155, y=162)
btnFind3 = ttk.Button(Move_Frame, text="Search", style="flat.TButton",
                      command=Get_Dst_Path_2).place(x=282, y=162)

Search_3_Path = tk.Label(Move_Frame, text="Send to:", fg="#382d2b",
                         bg="#dbdbdb", font=("Arial", "12", "bold")).place(x=77, y=274)
E4 = EntryEx(Move_Frame, style="EntryStyle.TEntry",
             textvariable=Dst_Path_3).place(x=155, y=278)
btnFind4 = ttk.Button(Move_Frame, text="Search", style="flat.TButton",
                      command=Get_Dst_Path_3).place(x=282, y=277)

Search_4_Path = tk.Label(Move_Frame, text="Send to:", fg="#382d2b",
                         bg="#dbdbdb", font=("Arial", "12", "bold")).place(x=77, y=393)
E4 = EntryEx(Move_Frame, style="EntryStyle.TEntry",
             textvariable=Dst_Path_4).place(x=155, y=397)
btnFind4 = ttk.Button(Move_Frame, text="Search", style="flat.TButton",
                      command=Get_Dst_Path_4).place(x=282, y=396)

Search_5_Path = tk.Label(Move_Frame, text="Send to:", fg="#382d2b",
                         bg="#dbdbdb", font=("Arial", "12", "bold")).place(x=77, y=508)
E5 = EntryEx(Move_Frame, style="EntryStyle.TEntry",
             textvariable=Dst_Path_5).place(x=155, y=512)
btnFind5 = ttk.Button(Move_Frame, text="Search", style="flat.TButton",
                      command=Get_Dst_Path_5).place(x=282, y=511)

Search_6_Path = tk.Label(Move_Frame, text="Send to:", fg="#382d2b",
                         bg="#dbdbdb", font=("Arial", "12", "bold")).place(x=670, y=47)
E6 = EntryEx(Move_Frame, style="EntryStyle.TEntry",
             textvariable=Dst_Path_6).place(x=746, y=50)
btnFind6 = ttk.Button(Move_Frame, text="Search", style="flat.TButton",
                      command=Get_Dst_Path_6).place(x=873, y=49)

Search_7_Path = tk.Label(Move_Frame, text="Send to:", fg="#382d2b",
                         bg="#dbdbdb", font=("Arial", "12", "bold")).place(x=670, y=158)
E7 = EntryEx(Move_Frame, style="EntryStyle.TEntry",
             textvariable=Dst_Path_7).place(x=746, y=162)
btnFind7 = ttk.Button(Move_Frame, text="Search", style="flat.TButton",
                      command=Get_Dst_Path_7).place(x=873, y=162)

Search_8_Path = tk.Label(Move_Frame, text="Send to:", fg="#382d2b",
                         bg="#dbdbdb", font=("Arial", "12", "bold")).place(x=670, y=274)
E8 = EntryEx(Move_Frame, style="EntryStyle.TEntry",
             textvariable=Dst_Path_8).place(x=746, y=278)
btnFind8 = ttk.Button(Move_Frame, text="Search", style="flat.TButton",
                      command=Get_Dst_Path_8).place(x=873, y=277)

Search_9_Path = tk.Label(Move_Frame, text="Send to:", fg="#382d2b",
                         bg="#dbdbdb", font=("Arial", "12", "bold")).place(x=670, y=393)
E9 = EntryEx(Move_Frame, style="EntryStyle.TEntry",
             textvariable=Dst_Path_9).place(x=746, y=397)
btnFind9 = ttk.Button(Move_Frame, text="Search", style="flat.TButton",
                      command=Get_Dst_Path_9).place(x=873, y=396)

Search_10_Path = tk.Label(Move_Frame, text="Send to:", fg="#382d2b",
                          bg="#dbdbdb", font=("Arial", "12", "bold")).place(x=670, y=508)
E10 = EntryEx(Move_Frame, style="EntryStyle.TEntry",
              textvariable=Dst_Path_10).place(x=746, y=512)
btnFind10 = ttk.Button(Move_Frame, text="Search", style="flat.TButton",
                       command=Get_Dst_Path_10).place(x=873, y=511)
# MOVE_MODULES_DST_PETITION_END

# MOVE_MODULES_EXTENTIONS_REQUEST
Module_1_Extensions = tk.StringVar()
Ext_Search_1 = tk.Label(Move_Frame, text="Extensions", fg="#382d2b",
                        bg="#dbdbdb", font=("Arial", "12", "bold")).place(x=380, y=12)
Entry_File_1_Extensions = EntryEx(
    Move_Frame, style="EntryStyle.TEntry", textvariable=Module_1_Extensions).place(x=370, y=37)
Module_1_Extensions.set(parser.get("Extensions", "Search_1"))

Module_2_Extensions = tk.StringVar()
Ext_Search_2 = tk.Label(Move_Frame, text="Extensions", fg="#382d2b",
                        bg="#dbdbdb", font=("Arial", "12", "bold")).place(x=380, y=123)
Entry_File_2_Extensions = EntryEx(
    Move_Frame, style="EntryStyle.TEntry", textvariable=Module_2_Extensions).place(x=370, y=150)
Module_2_Extensions.set(parser.get("Extensions", "Search_2"))

Module_3_Extensions = tk.StringVar()
Ext_Search_3 = tk.Label(Move_Frame, text="Extensions", fg="#382d2b",
                        bg="#dbdbdb", font=("Arial", "12", "bold")).place(x=380, y=241)
Entry_File_3_Extensions = EntryEx(
    Move_Frame, style="EntryStyle.TEntry", textvariable=Module_3_Extensions).place(x=370, y=268)
Module_3_Extensions.set(parser.get("Extensions", "Search_3"))

Module_4_Extensions = tk.StringVar()
Ext_Search_4 = tk.Label(Move_Frame, text="Extensions", fg="#382d2b",
                        bg="#dbdbdb", font=("Arial", "12", "bold")).place(x=380, y=358)
Entry_File_4_Extensions = EntryEx(
    Move_Frame, style="EntryStyle.TEntry", textvariable=Module_4_Extensions).place(x=370, y=384)
Module_4_Extensions.set(parser.get("Extensions", "Search_4"))

Module_5_Extensions = tk.StringVar()
Ext_Search_5 = tk.Label(Move_Frame, text="Extensions", fg="#382d2b",
                        bg="#dbdbdb", font=("Arial", "12", "bold")).place(x=380, y=475)
Entry_File_5_Extensions = EntryEx(
    Move_Frame, style="EntryStyle.TEntry", textvariable=Module_5_Extensions).place(x=370, y=500)
Module_5_Extensions.set(parser.get("Extensions", "Search_5"))

Module_6_Extensions = tk.StringVar()
Ext_Search_6 = tk.Label(Move_Frame, text="Extensions", fg="#382d2b",
                        bg="#dbdbdb", font=("Arial", "12", "bold")).place(x=970, y=12)
Entry_File_6_Extensions = EntryEx(
    Move_Frame, style="EntryStyle.TEntry", textvariable=Module_6_Extensions).place(x=960, y=37)
Module_6_Extensions.set(parser.get("Extensions", "Search_6"))

Module_7_Extensions = tk.StringVar()
Ext_Search_7 = tk.Label(Move_Frame, text="Extensions", fg="#382d2b",
                        bg="#dbdbdb", font=("Arial", "12", "bold")).place(x=970, y=123)
Entry_File_7_Extensions = EntryEx(
    Move_Frame, style="EntryStyle.TEntry", textvariable=Module_7_Extensions).place(x=960, y=150)
Module_7_Extensions.set(parser.get("Extensions", "Search_7"))

Module_8_Extensions = tk.StringVar()
Ext_Search_8 = tk.Label(Move_Frame, text="Extensions", fg="#382d2b",
                        bg="#dbdbdb", font=("Arial", "12", "bold")).place(x=970, y=241)
Entry_File_8_Extensions = EntryEx(
    Move_Frame, style="EntryStyle.TEntry", textvariable=Module_8_Extensions).place(x=960, y=268)
Module_8_Extensions.set(parser.get("Extensions", "Search_8"))

Module_9_Extensions = tk.StringVar()
Ext_Search_9 = tk.Label(Move_Frame, text="Extensions", fg="#382d2b",
                        bg="#dbdbdb", font=("Arial", "12", "bold")).place(x=970, y=358)
Entry_File_9_Extensions = EntryEx(
    Move_Frame, style="EntryStyle.TEntry", textvariable=Module_9_Extensions).place(x=960, y=384)
Module_9_Extensions.set(parser.get("Extensions", "Search_9"))

Module_10_Extensions = tk.StringVar()
Ext_Search_10 = tk.Label(Move_Frame, text="Extensions", fg="#382d2b",
                         bg="#dbdbdb", font=("Arial", "12", "bold")).place(x=970, y=475)
Entry_File_10_Extensions = EntryEx(
    Move_Frame, style="EntryStyle.TEntry", textvariable=Module_10_Extensions).place(x=960, y=500)
Module_10_Extensions.set(parser.get("Extensions", "Search_10"))
# MOVE_MODULES_EXTENTIONS_REQUEST_END

# TRANSFERING_TYPES
RadioValue_1 = tk.IntVar()
Copy_Files_Option_1 = tk.Radiobutton(
    Move_Frame, text="Copy", bg="#dbdbdb", variable=RadioValue_1, value=0).place(x=500, y=35)
Move_Files_Option_1 = tk.Radiobutton(
    Move_Frame, text="Move", bg="#dbdbdb", variable=RadioValue_1, value=1).place(x=560, y=35)

RadioValue_2 = tk.IntVar()
Copy_Files_Option_2 = tk.Radiobutton(
    Move_Frame, text="Copy", bg="#dbdbdb", variable=RadioValue_2, value=0).place(x=500, y=148)
Move_Files_Option_2 = tk.Radiobutton(
    Move_Frame, text="Move", bg="#dbdbdb", variable=RadioValue_2, value=1).place(x=560, y=148)

RadioValue_3 = tk.IntVar()
Copy_Files_Option_3 = tk.Radiobutton(
    Move_Frame, text="Copy", bg="#dbdbdb", variable=RadioValue_3, value=0).place(x=500, y=261)
Move_Files_Option_3 = tk.Radiobutton(
    Move_Frame, text="Move", bg="#dbdbdb", variable=RadioValue_3, value=1).place(x=560, y=261)

RadioValue_4 = tk.IntVar()
Copy_Files_Option_4 = tk.Radiobutton(
    Move_Frame, text="Copy", bg="#dbdbdb", variable=RadioValue_4, value=0).place(x=500, y=374)
Move_Files_Option_4 = tk.Radiobutton(
    Move_Frame, text="Move", bg="#dbdbdb", variable=RadioValue_4, value=1).place(x=560, y=374)

RadioValue_5 = tk.IntVar()
Copy_Files_Option_5 = tk.Radiobutton(
    Move_Frame, text="Copy", bg="#dbdbdb", variable=RadioValue_5, value=0).place(x=500, y=487)
Move_Files_Option_5 = tk.Radiobutton(
    Move_Frame, text="Move", bg="#dbdbdb", variable=RadioValue_5, value=1).place(x=560, y=487)

RadioValue_6 = tk.IntVar()
Copy_Files_Option_6 = tk.Radiobutton(
    Move_Frame, text="Copy", bg="#dbdbdb", variable=RadioValue_6, value=0).place(x=1088, y=35)
Move_Files_Option_6 = tk.Radiobutton(
    Move_Frame, text="Move", bg="#dbdbdb", variable=RadioValue_6, value=1).place(x=1148, y=35)

RadioValue_7 = tk.IntVar()
Copy_Files_Option_7 = tk.Radiobutton(
    Move_Frame, text="Copy", bg="#dbdbdb", variable=RadioValue_7, value=0).place(x=1088, y=148)
Move_Files_Option_7 = tk.Radiobutton(
    Move_Frame, text="Move", bg="#dbdbdb", variable=RadioValue_7, value=1).place(x=1148, y=148)

RadioValue_8 = tk.IntVar()
Copy_Files_Option_8 = tk.Radiobutton(
    Move_Frame, text="Copy", bg="#dbdbdb", variable=RadioValue_8, value=0).place(x=1088, y=261)
Move_Files_Option_8 = tk.Radiobutton(
    Move_Frame, text="Move", bg="#dbdbdb", variable=RadioValue_8, value=1).place(x=1148, y=261)

RadioValue_9 = tk.IntVar()
Copy_Files_Option_9 = tk.Radiobutton(
    Move_Frame, text="Copy", bg="#dbdbdb", variable=RadioValue_9, value=0).place(x=1088, y=374)
Move_Files_Option_9 = tk.Radiobutton(
    Move_Frame, text="Move", bg="#dbdbdb", variable=RadioValue_9, value=1).place(x=1148, y=374)

RadioValue_10 = tk.IntVar()
Copy_Files_Option_10 = tk.Radiobutton(
    Move_Frame, text="Copy", bg="#dbdbdb", variable=RadioValue_10, value=0).place(x=1088, y=487)
Move_Files_Option_10 = tk.Radiobutton(
    Move_Frame, text="Move", bg="#dbdbdb", variable=RadioValue_10, value=1).place(x=1148, y=487)

# TRANSFERING_TYPES_END

# LOGS_GENERATING


def Log_Copy_1():

    Module_Name = Move_Module_Name_1.get()
    window_Log = tk.Toplevel(root)
    window_Log.title(Module_Name + " - Copy [Module 1] LOG")
    window_Log.config(bg="#dbdbdb")
    window_Log.geometry("810x500+270+110")
    window_Log.resizable(False, False)
    window_Log.iconbitmap("icon.ico")

    scroll = tk.Scrollbar(window_Log)
    scroll.pack(side=tk.RIGHT, fill=tk.Y)

    with open(r"logs\Log_Copy_1_" + Move_Module_Name_1.get() + ".txt", "r") as Log_Open:
        Log = tk.Text(window_Log, yscrollcommand=scroll.set,
                      height=800, width=500)
        Log.pack()
        Log.insert(tk.END, Log_Open.read())
        Log.config(state=tk.DISABLED)
        scroll.config(command=Log.yview)


def Log_Move_1():

    Module_Name = Move_Module_Name_1.get()
    window_Log = tk.Toplevel(root)
    window_Log.title(Module_Name + " - Move [Module 1] LOG")
    window_Log.config(bg="#dbdbdb")
    window_Log.geometry("810x500+270+110")
    window_Log.resizable(False, False)
    window_Log.iconbitmap("icon.ico")

    scroll = tk.Scrollbar(window_Log)
    scroll.pack(side=tk.RIGHT, fill=tk.Y)

    with open(r"logs\Log_Move_1_" + Move_Module_Name_1.get() + ".txt", "r") as Log_Open:
        Log = tk.Text(window_Log, yscrollcommand=scroll.set,
                      height=800, width=500)
        Log.pack()
        Log.insert(tk.END, Log_Open.read())
        Log.config(state=tk.DISABLED)
        scroll.config(command=Log.yview)


def Log_Copy_2():

    Module_Name = Move_Module_Name_2.get()
    window_Log = tk.Toplevel(root)
    window_Log.title(Module_Name + " - Copy [Module 2] LOG")
    window_Log.config(bg="#dbdbdb")
    window_Log.geometry("810x500+270+110")
    window_Log.resizable(False, False)
    window_Log.iconbitmap("icon.ico")

    scroll = tk.Scrollbar(window_Log)
    scroll.pack(side=tk.RIGHT, fill=tk.Y)

    with open(r"logs\Log_Copy_2_" + Move_Module_Name_2.get() + ".txt", "r") as Log_Open:
        Log = tk.Text(window_Log, yscrollcommand=scroll.set,
                      height=800, width=500)
        Log.pack()
        Log.insert(tk.END, Log_Open.read())
        Log.config(state=tk.DISABLED)
        scroll.config(command=Log.yview)


def Log_Move_2():

    Module_Name = Move_Module_Name_2.get()
    window_Log = tk.Toplevel(root)
    window_Log.title(Module_Name + " - Move [Module 2] LOG")
    window_Log.config(bg="#dbdbdb")
    window_Log.geometry("810x500+270+110")
    window_Log.resizable(False, False)
    window_Log.iconbitmap("icon.ico")

    scroll = tk.Scrollbar(window_Log)
    scroll.pack(side=tk.RIGHT, fill=tk.Y)

    with open(r"logs\Log_Move_2_" + Move_Module_Name_2.get() + ".txt", "r") as Log_Open:
        Log = tk.Text(window_Log, yscrollcommand=scroll.set,
                      height=800, width=500)
        Log.pack()
        Log.insert(tk.END, Log_Open.read())
        Log.config(state=tk.DISABLED)
        scroll.config(command=Log.yview)


def Log_Copy_3():

    Module_Name = Move_Module_Name_3.get()
    window_Log = tk.Toplevel(root)
    window_Log.title(Module_Name + " - Copy [Module 3] LOG")
    window_Log.config(bg="#dbdbdb")
    window_Log.geometry("810x500+270+110")
    window_Log.resizable(False, False)
    window_Log.iconbitmap("icon.ico")

    scroll = tk.Scrollbar(window_Log)
    scroll.pack(side=tk.RIGHT, fill=tk.Y)

    with open(r"logs\Log_Copy_3_" + Move_Module_Name_3.get() + ".txt", "r") as Log_Open:
        Log = tk.Text(window_Log, yscrollcommand=scroll.set,
                      height=800, width=500)
        Log.pack()
        Log.insert(tk.END, Log_Open.read())
        Log.config(state=tk.DISABLED)
        scroll.config(command=Log.yview)


def Log_Move_3():

    Module_Name = Move_Module_Name_3.get()
    window_Log = tk.Toplevel(root)
    window_Log.title(Module_Name + " - Move [Module 3] LOG")
    window_Log.config(bg="#dbdbdb")
    window_Log.geometry("810x500+270+110")
    window_Log.resizable(False, False)
    window_Log.iconbitmap("icon.ico")

    scroll = tk.Scrollbar(window_Log)
    scroll.pack(side=tk.RIGHT, fill=tk.Y)

    with open(r"logs\Log_Move_3_" + Move_Module_Name_3.get() + ".txt", "r") as Log_Open:
        Log = tk.Text(window_Log, yscrollcommand=scroll.set,
                      height=800, width=500)
        Log.pack()
        Log.insert(tk.END, Log_Open.read())
        Log.config(state=tk.DISABLED)
        scroll.config(command=Log.yview)


def Log_Copy_4():

    Module_Name = Move_Module_Name_4.get()
    window_Log = tk.Toplevel(root)
    window_Log.title(Module_Name + " - Copy [Module 4] LOG")
    window_Log.config(bg="#dbdbdb")
    window_Log.geometry("810x500+270+110")
    window_Log.resizable(False, False)
    window_Log.iconbitmap("icon.ico")

    scroll = tk.Scrollbar(window_Log)
    scroll.pack(side=tk.RIGHT, fill=tk.Y)

    with open(r"logs\Log_Copy_4_" + Move_Module_Name_4.get() + ".txt", "r") as Log_Open:
        Log = tk.Text(window_Log, yscrollcommand=scroll.set,
                      height=800, width=500)
        Log.pack()
        Log.insert(tk.END, Log_Open.read())
        Log.config(state=tk.DISABLED)
        scroll.config(command=Log.yview)


def Log_Move_4():

    Module_Name = Move_Module_Name_4.get()
    window_Log = tk.Toplevel(root)
    window_Log.title(Module_Name + " - Move [Module 4] LOG")
    window_Log.config(bg="#dbdbdb")
    window_Log.geometry("810x500+270+110")
    window_Log.resizable(False, False)
    window_Log.iconbitmap("icon.ico")

    scroll = tk.Scrollbar(window_Log)
    scroll.pack(side=tk.RIGHT, fill=tk.Y)

    with open(r"logs\Log_Move_4_" + Move_Module_Name_4.get() + ".txt", "r") as Log_Open:
        Log = tk.Text(window_Log, yscrollcommand=scroll.set,
                      height=800, width=500)
        Log.pack()
        Log.insert(tk.END, Log_Open.read())
        Log.config(state=tk.DISABLED)
        scroll.config(command=Log.yview)


def Log_Copy_5():

    Module_Name = Move_Module_Name_5.get()
    window_Log = tk.Toplevel(root)
    window_Log.title(Module_Name + " - Copy [Module 5] LOG")
    window_Log.config(bg="#dbdbdb")
    window_Log.geometry("810x500+270+110")
    window_Log.resizable(False, False)
    window_Log.iconbitmap("icon.ico")

    scroll = tk.Scrollbar(window_Log)
    scroll.pack(side=tk.RIGHT, fill=tk.Y)

    with open(r"logs\Log_Copy_5_" + Move_Module_Name_5.get() + ".txt", "r") as Log_Open:
        Log = tk.Text(window_Log, yscrollcommand=scroll.set,
                      height=800, width=500)
        Log.pack()
        Log.insert(tk.END, Log_Open.read())
        Log.config(state=tk.DISABLED)
        scroll.config(command=Log.yview)


def Log_Move_5():

    Module_Name = Move_Module_Name_5.get()
    window_Log = tk.Toplevel(root)
    window_Log.title(Module_Name + " - Move [Module 5] LOG")
    window_Log.config(bg="#dbdbdb")
    window_Log.geometry("810x500+270+110")
    window_Log.resizable(False, False)
    window_Log.iconbitmap("icon.ico")

    scroll = tk.Scrollbar(window_Log)
    scroll.pack(side=tk.RIGHT, fill=tk.Y)

    with open(r"logs\Log_Move_5_" + Move_Module_Name_5.get() + ".txt", "r") as Log_Open:
        Log = tk.Text(window_Log, yscrollcommand=scroll.set,
                      height=800, width=500)
        Log.pack()
        Log.insert(tk.END, Log_Open.read())
        Log.config(state=tk.DISABLED)
        scroll.config(command=Log.yview)


def Log_Copy_6():

    Module_Name = Move_Module_Name_6.get()
    window_Log = tk.Toplevel(root)
    window_Log.title(Module_Name + " - Copy [Module 6] LOG")
    window_Log.config(bg="#dbdbdb")
    window_Log.geometry("810x500+270+110")
    window_Log.resizable(False, False)
    window_Log.iconbitmap("icon.ico")

    scroll = tk.Scrollbar(window_Log)
    scroll.pack(side=tk.RIGHT, fill=tk.Y)

    with open(r"logs\Log_Copy_6_" + Move_Module_Name_6.get() + ".txt", "r") as Log_Open:
        Log = tk.Text(window_Log, yscrollcommand=scroll.set,
                      height=800, width=500)
        Log.pack()
        Log.insert(tk.END, Log_Open.read())
        Log.config(state=tk.DISABLED)
        scroll.config(command=Log.yview)


def Log_Move_6():

    Module_Name = Move_Module_Name_6.get()
    window_Log = tk.Toplevel(root)
    window_Log.title(Module_Name + " - Move [Module 6] LOG")
    window_Log.config(bg="#dbdbdb")
    window_Log.geometry("810x500+270+110")
    window_Log.resizable(False, False)
    window_Log.iconbitmap("icon.ico")

    scroll = tk.Scrollbar(window_Log)
    scroll.pack(side=tk.RIGHT, fill=tk.Y)

    with open(r"logs\Log_Move_6_" + Move_Module_Name_6.get() + ".txt", "r") as Log_Open:
        Log = tk.Text(window_Log, yscrollcommand=scroll.set,
                      height=800, width=500)
        Log.pack()
        Log.insert(tk.END, Log_Open.read())
        Log.config(state=tk.DISABLED)
        scroll.config(command=Log.yview)


def Log_Copy_7():

    Module_Name = Move_Module_Name_7.get()
    window_Log = tk.Toplevel(root)
    window_Log.title(Module_Name + " - Copy [Module 7] LOG")
    window_Log.config(bg="#dbdbdb")
    window_Log.geometry("810x500+270+110")
    window_Log.resizable(False, False)
    window_Log.iconbitmap("icon.ico")

    scroll = tk.Scrollbar(window_Log)
    scroll.pack(side=tk.RIGHT, fill=tk.Y)

    with open(r"logs\Log_Copy_7_" + Move_Module_Name_7.get() + ".txt", "r") as Log_Open:
        Log = tk.Text(window_Log, yscrollcommand=scroll.set,
                      height=800, width=500)
        Log.pack()
        Log.insert(tk.END, Log_Open.read())
        Log.config(state=tk.DISABLED)
        scroll.config(command=Log.yview)


def Log_Move_7():

    Module_Name = Move_Module_Name_7.get()
    window_Log = tk.Toplevel(root)
    window_Log.title(Module_Name + " - Move [Module 7] LOG")
    window_Log.config(bg="#dbdbdb")
    window_Log.geometry("810x500+270+110")
    window_Log.resizable(False, False)
    window_Log.iconbitmap("icon.ico")

    scroll = tk.Scrollbar(window_Log)
    scroll.pack(side=tk.RIGHT, fill=tk.Y)

    with open(r"logs\Log_Move_7_" + Move_Module_Name_7.get() + ".txt", "r") as Log_Open:
        Log = tk.Text(window_Log, yscrollcommand=scroll.set,
                      height=800, width=500)
        Log.pack()
        Log.insert(tk.END, Log_Open.read())
        Log.config(state=tk.DISABLED)
        scroll.config(command=Log.yview)


def Log_Copy_8():

    Module_Name = Move_Module_Name_8.get()
    window_Log = tk.Toplevel(root)
    window_Log.title(Module_Name + " - Copy [Module 8] LOG")
    window_Log.config(bg="#dbdbdb")
    window_Log.geometry("810x500+270+110")
    window_Log.resizable(False, False)
    window_Log.iconbitmap("icon.ico")

    scroll = tk.Scrollbar(window_Log)
    scroll.pack(side=tk.RIGHT, fill=tk.Y)

    with open(r"logs\Log_Copy_8_" + Move_Module_Name_8.get() + ".txt", "r") as Log_Open:
        Log = tk.Text(window_Log, yscrollcommand=scroll.set,
                      height=800, width=500)
        Log.pack()
        Log.insert(tk.END, Log_Open.read())
        Log.config(state=tk.DISABLED)
        scroll.config(command=Log.yview)


def Log_Move_8():

    Module_Name = Move_Module_Name_8.get()
    window_Log = tk.Toplevel(root)
    window_Log.title(Module_Name + " - Move [Module 8] LOG")
    window_Log.config(bg="#dbdbdb")
    window_Log.geometry("810x500+270+110")
    window_Log.resizable(False, False)
    window_Log.iconbitmap("icon.ico")

    scroll = tk.Scrollbar(window_Log)
    scroll.pack(side=tk.RIGHT, fill=tk.Y)

    with open(r"logs\Log_Move_8_" + Move_Module_Name_8.get() + ".txt", "r") as Log_Open:
        Log = tk.Text(window_Log, yscrollcommand=scroll.set,
                      height=800, width=500)
        Log.pack()
        Log.insert(tk.END, Log_Open.read())
        Log.config(state=tk.DISABLED)
        scroll.config(command=Log.yview)


def Log_Copy_9():

    Module_Name = Move_Module_Name_9.get()
    window_Log = tk.Toplevel(root)
    window_Log.title(Module_Name + " - Copy [Module 9] LOG")
    window_Log.config(bg="#dbdbdb")
    window_Log.geometry("810x500+270+110")
    window_Log.resizable(False, False)
    window_Log.iconbitmap("icon.ico")

    scroll = tk.Scrollbar(window_Log)
    scroll.pack(side=tk.RIGHT, fill=tk.Y)

    with open(r"logs\Log_Copy_9_" + Move_Module_Name_9.get() + ".txt", "r") as Log_Open:
        Log = tk.Text(window_Log, yscrollcommand=scroll.set,
                      height=800, width=500)
        Log.pack()
        Log.insert(tk.END, Log_Open.read())
        Log.config(state=tk.DISABLED)
        scroll.config(command=Log.yview)


def Log_Move_9():

    Module_Name = Move_Module_Name_9.get()
    window_Log = tk.Toplevel(root)
    window_Log.title(Module_Name + " - Move [Module 9] LOG")
    window_Log.config(bg="#dbdbdb")
    window_Log.geometry("810x500+270+110")
    window_Log.resizable(False, False)
    window_Log.iconbitmap("icon.ico")

    scroll = tk.Scrollbar(window_Log)
    scroll.pack(side=tk.RIGHT, fill=tk.Y)

    with open(r"logs\Log_Move_9_" + Move_Module_Name_9.get() + ".txt", "r") as Log_Open:
        Log = tk.Text(window_Log, yscrollcommand=scroll.set,
                      height=800, width=500)
        Log.pack()
        Log.insert(tk.END, Log_Open.read())
        Log.config(state=tk.DISABLED)
        scroll.config(command=Log.yview)


def Log_Copy_10():

    Module_Name = Move_Module_Name_10.get()
    window_Log = tk.Toplevel(root)
    window_Log.title(Module_Name + " - Copy [Module 10] LOG")
    window_Log.config(bg="#dbdbdb")
    window_Log.geometry("810x500+270+110")
    window_Log.resizable(False, False)
    window_Log.iconbitmap("icon.ico")

    scroll = tk.Scrollbar(window_Log)
    scroll.pack(side=tk.RIGHT, fill=tk.Y)

    with open(r"logs\Log_Copy_10_" + Move_Module_Name_10.get() + ".txt", "r") as Log_Open:
        Log = tk.Text(window_Log, yscrollcommand=scroll.set,
                      height=800, width=500)
        Log.pack()
        Log.insert(tk.END, Log_Open.read())
        Log.config(state=tk.DISABLED)
        scroll.config(command=Log.yview)


def Log_Move_10():

    Module_Name = Move_Module_Name_10.get()
    window_Log = tk.Toplevel(root)
    window_Log.title(Module_Name + " - Move [Module 10] LOG")
    window_Log.config(bg="#dbdbdb")
    window_Log.geometry("810x500+270+110")
    window_Log.resizable(False, False)
    window_Log.iconbitmap("icon.ico")

    scroll = tk.Scrollbar(window_Log)
    scroll.pack(side=tk.RIGHT, fill=tk.Y)

    with open(r"logs\Log_Move_10_" + Move_Module_Name_10.get() + ".txt", "r") as Log_Open:
        Log = tk.Text(window_Log, yscrollcommand=scroll.set,
                      height=800, width=500)
        Log.pack()
        Log.insert(tk.END, Log_Open.read())
        Log.config(state=tk.DISABLED)
        scroll.config(command=Log.yview)

# LOGS_GENERATING_END

# TRANSFER_MODULE


def Transfer_Module_1():

    parser.set("Paths_Src", "path_1", Src_Path_1.get())
    parser.set("Paths_Dst", "path_1", Dst_Path_1.get())
    parser.set("Extensions", "Search_1", Module_1_Extensions.get())
    parser.set("Path_Names", "path_name_1", Move_Module_Name_1.get())

    with open('config.ini', 'w') as myconfig:
        parser.write(myconfig)

    try:

        Src = win32api.GetShortPathName(Src_Path_1.get())
        Dst = win32api.GetShortPathName(Dst_Path_1.get())
        Files_Extensions_Read = parser.get(
            "Extensions", "Search_1").split(" ")

        if parser.get("Paths_Src", "path_1") == parser.get("Paths_Dst", "path_1"):

            messagebox.showwarning(message="ATTENTION: Origin and Destination are the same in (" +
                                   parser.get("Path_Names", "path_name_1")+")", title="MeCopy")
            sys.exit(0)

        if parser.get("Paths_Src", "path_1") == ("C:/"):

            Alert_Path = tk.messagebox.askyesno(title="MeCopy", message="ATTENTION: You have chosen as source path C: in (" + parser.get("Path_Names", "path_name_1") +
                                                ") This may cause problems when copying your files and some files may not be able to be copied and the operation may take a long time. We recommend that you choose more specific paths. Do you want to continue?")

            if Alert_Path is False:
                sys.exit(0)

        progressbar = ttk.Progressbar(mode="indeterminate")
        progressbar.place(x=439, y=82, width=100)
        progressbar.start(10)

        Transfer_InProcress = tk.Label(
            Move_Frame, bg="#dbdbdb", fg="#382d2b", text="Transfering...")
        Transfer_InProcress.place(x=490, y=60)

        if RadioValue_1.get() == 0:
            
            Call_Move = ["robocopy", Src, Dst, "/S",
                         "/ZB", "/XJ", "/R:0", "/W:0","/TEE", "/COPYALL", r"/log:logs\Log_Copy_1_" + Move_Module_Name_1.get() + ".txt"]
            Call_Move.extend(Files_Extensions_Read)
            call(Call_Move)
            Log_Copy_1()

        if RadioValue_1.get() == 1:

            Call_Move = ["robocopy", Src, Dst, "/S",
                         "/ZB", "/XJ", "/R:0", "/W:0","/TEE", "/MOVE", r"/log:logs\Log_Move_1_" + Move_Module_Name_1.get() + ".txt"]
            Call_Move.extend(Files_Extensions_Read)
            call(Call_Move)
            Log_Move_1()

        progressbar.destroy()
        Transfer_InProcress.destroy()

        Transfer_Completed = tk.Label(
            Move_Frame, bg="#dbdbdb", fg="#382d2b", text="Transfer completed at " + time.strftime("%H:%M:%S"))
        Transfer_Completed.place(x=340, y=80)

    except WindowsError:
        pass
    except SyntaxError:
        pass
    except ValueError:
        pass
    except TypeError:
        pass
    except FileNotFoundError:
        Path_Error = messagebox.showwarning(
            message="Path cannot be found (" + Src + ")", title="MeCopy")
        pass
    except pywintypes.error:
        Path_Error = messagebox.showwarning(message="The source path or destination of "+parser.get(
            "Path_Names", "path_name_1")+" is misspelled or do not exist.", title="MeCopy")
        pass


def Transfer_Module_2():

    parser.set("Paths_Src", "path_2", Src_Path_2.get())
    parser.set("Paths_Dst", "path_2", Dst_Path_2.get())
    parser.set("Extensions", "Search_2", Module_2_Extensions.get())
    parser.set("Path_Names", "path_name_2", Move_Module_Name_2.get())

    with open('config.ini', 'w') as myconfig:
        parser.write(myconfig)

    try:

        Src = win32api.GetShortPathName(Src_Path_2.get())
        Dst = win32api.GetShortPathName(Dst_Path_2.get())
        Files_Extensions_Read = parser.get(
            "Extensions", "Search_2").split(" ")

        if parser.get("Paths_Src", "path_2") == parser.get("Paths_Dst", "path_2"):

            messagebox.showwarning(message="ATTENTION: Origin and Destination are the same in (" +
                                   parser.get("Path_Names", "path_name_2")+")", title="MeCopy")
            sys.exit(0)

        if parser.get("Paths_Src", "path_2") == ("C:/"):

            Alert_Path = tk.messagebox.askyesno(title="MeCopy", message="ATTENTION: You have chosen as source path C: in (" + parser.get("Path_Names", "path_name_2") +
                                                ") This may cause problems when copying your files and some files may not be able to be copied and the operation may take a long time. We recommend that you choose more specific paths. Do you want to continue?")

            if Alert_Path is False:
                sys.exit(0)

        progressbar = ttk.Progressbar(mode="indeterminate")
        progressbar.place(x=439, y=195, width=100)
        progressbar.start(10)

        Transfer_InProcress = tk.Label(
            Move_Frame, bg="#dbdbdb", fg="#382d2b", text="Transfering...")
        Transfer_InProcress.place(x=490, y=174)

        if RadioValue_2.get() == 0:
            Call_Move = ["robocopy", Src, Dst, "/S",
                         "/ZB", "/XJ", "/R:0", "/W:0","/TEE", "/COPYALL", r"/log:logs\Log_Copy_2_" + Move_Module_Name_2.get() + ".txt"]
            Call_Move.extend(Files_Extensions_Read)
            call(Call_Move)
            Log_Copy_2()

        if RadioValue_2.get() == 1:

            Call_Move = ["robocopy", Src, Dst, "/S",
                         "/ZB", "/XJ", "/R:0", "/W:0","/TEE", "/MOVE", r"/log:logs\Log_Move_2_" + Move_Module_Name_2.get() + ".txt"]
            Call_Move.extend(Files_Extensions_Read)
            call(Call_Move)
            Log_Move_2()

        progressbar.destroy()
        Transfer_InProcress.destroy()

        Transfer_Completed = tk.Label(
            Move_Frame, bg="#dbdbdb", fg="#382d2b", text="Transfer completed at " + time.strftime("%H:%M:%S"))
        Transfer_Completed.place(x=340, y=193)

    except WindowsError:
        pass
    except SyntaxError:
        pass
    except ValueError:
        pass
    except TypeError:
        pass
    except FileNotFoundError:
        Path_Error = messagebox.showwarning(
            message="Path cannot be found (" + Src + ")", title="MeCopy")
        pass
    except pywintypes.error:
        Path_Error = messagebox.showwarning(message="The source path or destination of "+parser.get(
            "Path_Names", "path_name_2")+" is misspelled or do not exist.", title="MeCopy")
        pass


def Transfer_Module_3():

    parser.set("Paths_Src", "path_3", Src_Path_3.get())
    parser.set("Paths_Dst", "path_3", Dst_Path_3.get())
    parser.set("Extensions", "Search_3", Module_3_Extensions.get())
    parser.set("Path_Names", "path_name_3", Move_Module_Name_3.get())

    with open('config.ini', 'w') as myconfig:
        parser.write(myconfig)

    try:

        Src = win32api.GetShortPathName(Src_Path_3.get())
        Dst = win32api.GetShortPathName(Dst_Path_3.get())
        Files_Extensions_Read = parser.get(
            "Extensions", "Search_3").split(" ")

        if parser.get("Paths_Src", "path_3") == parser.get("Paths_Dst", "path_3"):

            messagebox.showwarning(message="ATTENTION: Origin and Destination are the same in (" +
                                   parser.get("Path_Names", "path_name_3")+")", title="MeCopy")
            sys.exit(0)

        if parser.get("Paths_Src", "path_3") == ("C:/"):

            Alert_Path = tk.messagebox.askyesno(title="MeCopy", message="ATTENTION: You have chosen as source path C: in (" + parser.get("Path_Names", "path_name_3") +
                                                ") This may cause problems when copying your files and some files may not be able to be copied and the operation may take a long time. We recommend that you choose more specific paths. Do you want to continue?")

            if Alert_Path is False:
                sys.exit(0)

        progressbar = ttk.Progressbar(mode="indeterminate")
        progressbar.place(x=439, y=313, width=100)
        progressbar.start(10)

        Transfer_InProcress = tk.Label(
            Move_Frame, bg="#dbdbdb", fg="#382d2b", text="Transfering...")
        Transfer_InProcress.place(x=490, y=290)

        if RadioValue_3.get() == 0:
            Call_Move = ["robocopy", Src, Dst, "/S",
                         "/ZB", "/XJ", "/R:0", "/W:0","/TEE", "/COPYALL", r"/log:logs\Log_Copy_3_" + Move_Module_Name_3.get() + ".txt"]
            Call_Move.extend(Files_Extensions_Read)
            call(Call_Move)
            Log_Copy_3()

        if RadioValue_3.get() == 1:

            Call_Move = ["robocopy", Src, Dst, "/S",
                         "/ZB", "/XJ", "/R:0", "/W:0","/TEE", "/MOVE", r"/log:logs\Log_Move_3_" + Move_Module_Name_3.get() + ".txt"]
            Call_Move.extend(Files_Extensions_Read)
            call(Call_Move)
            Log_Move_3()

        progressbar.destroy()
        Transfer_InProcress.destroy()

        Transfer_Completed = tk.Label(
            Move_Frame, bg="#dbdbdb", fg="#382d2b", text="Transfer completed at " + time.strftime("%H:%M:%S"))
        Transfer_Completed.place(x=340, y=309)

    except WindowsError:
        pass
    except SyntaxError:
        pass
    except ValueError:
        pass
    except TypeError:
        pass
    except FileNotFoundError:
        Path_Error = messagebox.showwarning(
            message="Path cannot be found (" + Src + ")", title="MeCopy")
        pass
    except pywintypes.error:
        Path_Error = messagebox.showwarning(message="The source path or destination of "+parser.get(
            "Path_Names", "path_name_3")+" is misspelled or do not exist.", title="MeCopy")
        pass


def Transfer_Module_4():

    parser.set("Paths_Src", "path_4", Src_Path_4.get())
    parser.set("Paths_Dst", "path_4", Dst_Path_4.get())
    parser.set("Extensions", "Search_4", Module_4_Extensions.get())
    parser.set("Path_Names", "path_name_4", Move_Module_Name_4.get())

    with open('config.ini', 'w') as myconfig:
        parser.write(myconfig)

    try:

        Src = win32api.GetShortPathName(Src_Path_4.get())
        Dst = win32api.GetShortPathName(Dst_Path_4.get())
        Files_Extensions_Read = parser.get(
            "Extensions", "Search_4").split(" ")

        if parser.get("Paths_Src", "path_4") == parser.get("Paths_Dst", "path_4"):

            messagebox.showwarning(message="ATTENTION: Origin and Destination are the same in (" +
                                   parser.get("Path_Names", "path_name_4")+")", title="MeCopy")
            sys.exit(0)

        if parser.get("Paths_Src", "path_4") == ("C:/"):

            Alert_Path = tk.messagebox.askyesno(title="MeCopy", message="ATTENTION: You have chosen as source path C: in (" + parser.get("Path_Names", "path_name_4") +
                                                ") This may cause problems when copying your files and some files may not be able to be copied and the operation may take a long time. We recommend that you choose more specific paths. Do you want to continue?")

            if Alert_Path is False:
                sys.exit(0)

        progressbar = ttk.Progressbar(mode="indeterminate")
        progressbar.place(x=439, y=429, width=100)
        progressbar.start(10)

        Transfer_InProcress = tk.Label(
            Move_Frame, bg="#dbdbdb", fg="#382d2b", text="Transfering...")
        Transfer_InProcress.place(x=490, y=406)

        if RadioValue_4.get() == 0:
            Call_Move = ["robocopy", Src, Dst, "/S",
                         "/ZB", "/XJ", "/R:0", "/W:0","/TEE", "/COPYALL", r"/log:logs\Log_Copy_4_" + Move_Module_Name_4.get() + ".txt"]
            Call_Move.extend(Files_Extensions_Read)
            call(Call_Move)
            Log_Copy_4()

        if RadioValue_4.get() == 1:

            Call_Move = ["robocopy", Src, Dst, "/S",
                         "/ZB", "/XJ", "/R:0", "/W:0","/TEE", "/MOVE", r"/log:logs\Log_Move_4_" + Move_Module_Name_4.get() + ".txt"]
            Call_Move.extend(Files_Extensions_Read)
            call(Call_Move)
            Log_Move_4()

        progressbar.destroy()
        Transfer_InProcress.destroy()

        Transfer_Completed = tk.Label(
            Move_Frame, bg="#dbdbdb", fg="#382d2b", text="Transfer completed at " + time.strftime("%H:%M:%S"))
        Transfer_Completed.place(x=340, y=428)

    except WindowsError:
        pass
    except SyntaxError:
        pass
    except ValueError:
        pass
    except TypeError:
        pass
    except FileNotFoundError:
        Path_Error = messagebox.showwarning(
            message="Path cannot be found (" + Src + ")", title="MeCopy")
        pass
    except pywintypes.error:
        Path_Error = messagebox.showwarning(message="The source path or destination of "+parser.get(
            "Path_Names", "path_name_4")+" is misspelled or do not exist.", title="MeCopy")
        pass


def Transfer_Module_5():

    parser.set("Paths_Src", "path_5", Src_Path_5.get())
    parser.set("Paths_Dst", "path_5", Dst_Path_5.get())
    parser.set("Extensions", "Search_5", Module_5_Extensions.get())
    parser.set("Path_Names", "path_name_5", Move_Module_Name_5.get())

    with open('config.ini', 'w') as myconfig:
        parser.write(myconfig)

    try:

        Src = win32api.GetShortPathName(Src_Path_5.get())
        Dst = win32api.GetShortPathName(Dst_Path_5.get())
        Files_Extensions_Read = parser.get(
            "Extensions", "Search_5").split(" ")

        if parser.get("Paths_Src", "path_5") == parser.get("Paths_Dst", "path_5"):

            messagebox.showwarning(message="ATTENTION: Origin and Destination are the same in (" +
                                   parser.get("Path_Names", "path_name_5")+")", title="MeCopy")
            sys.exit(0)

        if parser.get("Paths_Src", "path_5") == ("C:/"):

            Alert_Path = tk.messagebox.askyesno(title="MeCopy", message="ATTENTION: You have chosen as source path C: in (" + parser.get("Path_Names", "path_name_5") +
                                                ") This may cause problems when copying your files and some files may not be able to be copied and the operation may take a long time. We recommend that you choose more specific paths. Do you want to continue?")

            if Alert_Path is False:
                sys.exit(0)

        progressbar = ttk.Progressbar(mode="indeterminate")
        progressbar.place(x=439, y=545, width=100)
        progressbar.start(10)

        Transfer_InProcress = tk.Label(
            Move_Frame, bg="#dbdbdb", fg="#382d2b", text="Transfering...")
        Transfer_InProcress.place(x=490, y=522)

        if RadioValue_5.get() == 0:
            Call_Move = ["robocopy", Src, Dst, "/S",
                         "/ZB", "/XJ", "/R:0", "/W:0","/TEE", "/COPYALL", r"/log:logs\Log_Copy_5_" + Move_Module_Name_5.get() + ".txt"]
            Call_Move.extend(Files_Extensions_Read)
            call(Call_Move)
            Log_Copy_5()

        if RadioValue_5.get() == 1:

            Call_Move = ["robocopy", Src, Dst, "/S",
                         "/ZB", "/XJ", "/R:0", "/W:0","/TEE", "/MOVE", r"/log:logs\Log_Move_5_" + Move_Module_Name_5.get() + ".txt"]
            Call_Move.extend(Files_Extensions_Read)
            call(Call_Move)
            Log_Move_5()

        progressbar.destroy()
        Transfer_InProcress.destroy()

        Transfer_Completed = tk.Label(
            Move_Frame, bg="#dbdbdb", fg="#382d2b", text="Transfer completed at " + time.strftime("%H:%M:%S"))
        Transfer_Completed.place(x=340, y=545)

    except WindowsError:
        pass
    except SyntaxError:
        pass
    except ValueError:
        pass
    except TypeError:
        pass
    except FileNotFoundError:
        Path_Error = messagebox.showwarning(
            message="Path cannot be found (" + Src + ")", title="MeCopy")
        pass
    except pywintypes.error:
        Path_Error = messagebox.showwarning(message="The source path or destination of "+parser.get(
            "Path_Names", "path_name_5")+" is misspelled or do not exist.", title="MeCopy")
        pass


def Transfer_Module_6():

    parser.set("Paths_Src", "path_6", Src_Path_6.get())
    parser.set("Paths_Dst", "path_6", Dst_Path_6.get())
    parser.set("Extensions", "Search_6", Module_6_Extensions.get())
    parser.set("Path_Names", "path_name_6", Move_Module_Name_6.get())

    with open('config.ini', 'w') as myconfig:
        parser.write(myconfig)

    try:

        Src = win32api.GetShortPathName(Src_Path_6.get())
        Dst = win32api.GetShortPathName(Dst_Path_6.get())
        Files_Extensions_Read = parser.get(
            "Extensions", "Search_6").split(" ")

        if parser.get("Paths_Src", "path_6") == parser.get("Paths_Dst", "path_6"):

            messagebox.showwarning(message="ATTENTION: Origin and Destination are the same in (" +
                                   parser.get("Path_Names", "path_name_6")+")", title="MeCopy")
            sys.exit(0)

        if parser.get("Paths_Src", "path_6") == ("C:/"):

            Alert_Path = tk.messagebox.askyesno(title="MeCopy", message="ATTENTION: You have chosen as source path C: in (" + parser.get("Path_Names", "path_name_6") +
                                                ") This may cause problems when copying your files and some files may not be able to be copied and the operation may take a long time. We recommend that you choose more specific paths. Do you want to continue?")

            if Alert_Path is False:
                sys.exit(0)

        progressbar = ttk.Progressbar(mode="indeterminate")
        progressbar.place(x=1027, y=82, width=100)
        progressbar.start(10)

        Transfer_InProcress = tk.Label(
            Move_Frame, bg="#dbdbdb", fg="#382d2b", text="Transfering...")
        Transfer_InProcress.place(x=1080, y=60)

        if RadioValue_6.get() == 0:
            Call_Move = ["robocopy", Src, Dst, "/S",
                         "/ZB", "/XJ", "/R:0", "/W:0","/TEE", "/COPYALL", r"/log:logs\Log_Copy_6_" + Move_Module_Name_6.get() + ".txt"]
            Call_Move.extend(Files_Extensions_Read)
            call(Call_Move)
            Log_Copy_6()

        if RadioValue_6.get() == 1:

            Call_Move = ["robocopy", Src, Dst, "/S",
                         "/ZB", "/XJ", "/R:0", "/W:0","/TEE", "/MOVE", r"/log:logs\Log_Move_6_" + Move_Module_Name_6.get() + ".txt"]
            Call_Move.extend(Files_Extensions_Read)
            call(Call_Move)
            Log_Move_6()

        progressbar.destroy()
        Transfer_InProcress.destroy()

        Transfer_Completed = tk.Label(
            Move_Frame, bg="#dbdbdb", fg="#382d2b", text="Transfer completed at " + time.strftime("%H:%M:%S"))
        Transfer_Completed.place(x=930, y=80)

    except WindowsError:
        pass
    except SyntaxError:
        pass
    except ValueError:
        pass
    except TypeError:
        pass
    except FileNotFoundError:
        Path_Error = messagebox.showwarning(
            message="Path cannot be found (" + Src + ")", title="MeCopy")
        pass
    except pywintypes.error:
        Path_Error = messagebox.showwarning(message="The source path or destination of "+parser.get(
            "Path_Names", "path_name_6")+" is misspelled or do not exist.", title="MeCopy")
        pass


def Transfer_Module_7():

    parser.set("Paths_Src", "path_7", Src_Path_7.get())
    parser.set("Paths_Dst", "path_7", Dst_Path_7.get())
    parser.set("Extensions", "Search_7", Module_7_Extensions.get())
    parser.set("Path_Names", "path_name_7", Move_Module_Name_7.get())

    with open('config.ini', 'w') as myconfig:
        parser.write(myconfig)

    try:

        Src = win32api.GetShortPathName(Src_Path_7.get())
        Dst = win32api.GetShortPathName(Dst_Path_7.get())
        Files_Extensions_Read = parser.get(
            "Extensions", "Search_7").split(" ")

        if parser.get("Paths_Src", "path_7") == parser.get("Paths_Dst", "path_7"):

            messagebox.showwarning(message="ATTENTION: Origin and Destination are the same in (" +
                                   parser.get("Path_Names", "path_name_7")+")", title="MeCopy")
            sys.exit(0)

        if parser.get("Paths_Src", "path_7") == ("C:/"):

            Alert_Path = tk.messagebox.askyesno(title="MeCopy", message="ATTENTION: You have chosen as source path C: in (" + parser.get("Path_Names", "path_name_7") +
                                                ") This may cause problems when copying your files and some files may not be able to be copied and the operation may take a long time. We recommend that you choose more specific paths. Do you want to continue?")

            if Alert_Path is False:
                sys.exit(0)

        progressbar = ttk.Progressbar(mode="indeterminate")
        progressbar.place(x=1027, y=195, width=100)
        progressbar.start(10)

        Transfer_InProcress = tk.Label(
            Move_Frame, bg="#dbdbdb", fg="#382d2b", text="Transfering...")
        Transfer_InProcress.place(x=1080, y=174)

        if RadioValue_7.get() == 0:
            Call_Move = ["robocopy", Src, Dst, "/S",
                         "/ZB", "/XJ", "/R:0", "/W:0","/TEE", "/COPYALL", r"/log:logs\Log_Copy_7_" + Move_Module_Name_7.get() + ".txt"]
            Call_Move.extend(Files_Extensions_Read)
            call(Call_Move)
            Log_Copy_7()

        if RadioValue_7.get() == 1:

            Call_Move = ["robocopy", Src, Dst, "/S",
                         "/ZB", "/XJ", "/R:0", "/W:0","/TEE", "/MOVE", r"/log:logs\Log_Move_7_" + Move_Module_Name_7.get() + ".txt"]
            Call_Move.extend(Files_Extensions_Read)
            call(Call_Move)
            Log_Move_7()

        progressbar.destroy()
        Transfer_InProcress.destroy()

        Transfer_Completed = tk.Label(
            Move_Frame, bg="#dbdbdb", fg="#382d2b", text="Transfer completed at " + time.strftime("%H:%M:%S"))
        Transfer_Completed.place(x=930, y=193)

    except WindowsError:
        pass
    except SyntaxError:
        pass
    except ValueError:
        pass
    except TypeError:
        pass
    except FileNotFoundError:
        Path_Error = messagebox.showwarning(
            message="Path cannot be found (" + Src + ")", title="MeCopy")
        pass
    except pywintypes.error:
        Path_Error = messagebox.showwarning(message="The source path or destination of "+parser.get(
            "Path_Names", "path_name_7")+" is misspelled or do not exist.", title="MeCopy")
        pass


def Transfer_Module_8():

    parser.set("Paths_Src", "path_8", Src_Path_8.get())
    parser.set("Paths_Dst", "path_8", Dst_Path_8.get())
    parser.set("Extensions", "Search_8", Module_8_Extensions.get())
    parser.set("Path_Names", "path_name_8", Move_Module_Name_8.get())

    with open('config.ini', 'w') as myconfig:
        parser.write(myconfig)

    try:

        Src = win32api.GetShortPathName(Src_Path_8.get())
        Dst = win32api.GetShortPathName(Dst_Path_8.get())
        Files_Extensions_Read = parser.get(
            "Extensions", "Search_8").split(" ")

        if parser.get("Paths_Src", "path_8") == parser.get("Paths_Dst", "path_8"):

            messagebox.showwarning(message="ATTENTION: Origin and Destination are the same in (" +
                                   parser.get("Path_Names", "path_name_8")+")", title="MeCopy")
            sys.exit(0)

        if parser.get("Paths_Src", "path_8") == ("C:/"):

            Alert_Path = tk.messagebox.askyesno(title="MeCopy", message="ATTENTION: You have chosen as source path C: in (" + parser.get("Path_Names", "path_name_8") +
                                                ") This may cause problems when copying your files and some files may not be able to be copied and the operation may take a long time. We recommend that you choose more specific paths. Do you want to continue?")

            if Alert_Path is False:
                sys.exit(0)

        progressbar = ttk.Progressbar(mode="indeterminate")
        progressbar.place(x=1027, y=313, width=100)
        progressbar.start(10)

        Transfer_InProcress = tk.Label(
            Move_Frame, bg="#dbdbdb", fg="#382d2b", text="Transfering...")
        Transfer_InProcress.place(x=1080, y=290)

        if RadioValue_8.get() == 0:
            Call_Move = ["robocopy", Src, Dst, "/S",
                         "/ZB", "/XJ", "/R:0", "/W:0","/TEE", "/COPYALL", r"/log:logs\Log_Copy_8_" + Move_Module_Name_8.get() + ".txt"]
            Call_Move.extend(Files_Extensions_Read)
            call(Call_Move)
            Log_Copy_8()

        if RadioValue_8.get() == 1:

            Call_Move = ["robocopy", Src, Dst, "/S",
                         "/ZB", "/XJ", "/R:0", "/W:0", "/TEE","/MOVE", r"/log:logs\Log_Move_8_" + Move_Module_Name_8.get() + ".txt"]
            Call_Move.extend(Files_Extensions_Read)
            call(Call_Move)
            Log_Move_8()

        progressbar.destroy()
        Transfer_InProcress.destroy()

        Transfer_Completed = tk.Label(
            Move_Frame, bg="#dbdbdb", fg="#382d2b", text="Transfer completed at " + time.strftime("%H:%M:%S"))
        Transfer_Completed.place(x=930, y=309)

    except WindowsError:
        pass
    except SyntaxError:
        pass
    except ValueError:
        pass
    except TypeError:
        pass
    except FileNotFoundError:
        Path_Error = messagebox.showwarning(
            message="Path cannot be found (" + Src + ")", title="MeCopy")
        pass
    except pywintypes.error:
        Path_Error = messagebox.showwarning(message="The source path or destination of "+parser.get(
            "Path_Names", "path_name_8")+" is misspelled or do not exist.", title="MeCopy")
        pass


def Transfer_Module_9():

    parser.set("Paths_Src", "path_9", Src_Path_9.get())
    parser.set("Paths_Dst", "path_9", Dst_Path_9.get())
    parser.set("Extensions", "Search_9", Module_9_Extensions.get())
    parser.set("Path_Names", "path_name_9", Move_Module_Name_9.get())

    with open('config.ini', 'w') as myconfig:
        parser.write(myconfig)

    try:

        Src = win32api.GetShortPathName(Src_Path_9.get())
        Dst = win32api.GetShortPathName(Dst_Path_9.get())
        Files_Extensions_Read = parser.get(
            "Extensions", "Search_9").split(" ")

        if parser.get("Paths_Src", "path_9") == parser.get("Paths_Dst", "path_9"):

            messagebox.showwarning(message="ATTENTION: Origin and Destination are the same in (" +
                                   parser.get("Path_Names", "path_name_9")+")", title="MeCopy")
            sys.exit(0)

        if parser.get("Paths_Src", "path_9") == ("C:/"):

            Alert_Path = tk.messagebox.askyesno(title="MeCopy", message="ATTENTION: You have chosen as source path C: in (" + parser.get("Path_Names", "path_name_9") +
                                                ") This may cause problems when copying your files and some files may not be able to be copied and the operation may take a long time. We recommend that you choose more specific paths. Do you want to continue?")

            if Alert_Path is False:
                sys.exit(0)

        progressbar = ttk.Progressbar(mode="indeterminate")
        progressbar.place(x=1027, y=429, width=100)
        progressbar.start(10)

        Transfer_InProcress = tk.Label(
            Move_Frame, bg="#dbdbdb", fg="#382d2b", text="Transfering...")
        Transfer_InProcress.place(x=1080, y=406)

        if RadioValue_9.get() == 0:
            Call_Move = ["robocopy", Src, Dst, "/S",
                         "/ZB", "/XJ", "/R:0", "/W:0","/TEE", "/COPYALL", r"/log:logs\Log_Copy_9_" + Move_Module_Name_9.get() + ".txt"]
            Call_Move.extend(Files_Extensions_Read)
            call(Call_Move)
            Log_Copy_9()

        if RadioValue_9.get() == 1:

            Call_Move = ["robocopy", Src, Dst, "/S",
                         "/ZB", "/XJ", "/R:0", "/W:0","/TEE", "/MOVE", r"/log:logs\Log_Move_9_" + Move_Module_Name_9.get() + ".txt"]
            Call_Move.extend(Files_Extensions_Read)
            call(Call_Move)
            Log_Move_9()

        progressbar.destroy()
        Transfer_InProcress.destroy()

        Transfer_Completed = tk.Label(
            Move_Frame, bg="#dbdbdb", fg="#382d2b", text="Transfer completed at " + time.strftime("%H:%M:%S"))
        Transfer_Completed.place(x=930, y=428)

    except WindowsError:
        pass
    except SyntaxError:
        pass
    except ValueError:
        pass
    except TypeError:
        pass
    except FileNotFoundError:
        Path_Error = messagebox.showwarning(
            message="Path cannot be found (" + Src + ")", title="MeCopy")
        pass
    except pywintypes.error:
        Path_Error = messagebox.showwarning(message="The source path or destination of "+parser.get(
            "Path_Names", "path_name_9")+" is misspelled or do not exist.", title="MeCopy")
        pass


def Transfer_Module_10():

    parser.set("Paths_Src", "path_10", Src_Path_10.get())
    parser.set("Paths_Dst", "path_10", Dst_Path_10.get())
    parser.set("Extensions", "Search_10", Module_10_Extensions.get())
    parser.set("Path_Names", "path_name_10", Move_Module_Name_10.get())

    with open('config.ini', 'w') as myconfig:
        parser.write(myconfig)

    try:

        Src = win32api.GetShortPathName(Src_Path_10.get())
        Dst = win32api.GetShortPathName(Dst_Path_10.get())
        Files_Extensions_Read = parser.get(
            "Extensions", "Search_10").split(" ")

        if parser.get("Paths_Src", "path_10") == parser.get("Paths_Dst", "path_10"):

            messagebox.showwarning(message="ATTENTION: Origin and Destination are the same in (" +
                                   parser.get("Path_Names", "path_name_10")+")", title="MeCopy")
            sys.exit(0)

        if parser.get("Paths_Src", "path_10") == ("C:/"):

            Alert_Path = tk.messagebox.askyesno(title="MeCopy", message="ATTENTION: You have chosen as source path C: in (" + parser.get("Path_Names", "path_name_10") +
                                                ") This may cause problems when copying your files and some files may not be able to be copied and the operation may take a long time. We recommend that you choose more specific paths. Do you want to continue?")

            if Alert_Path is False:
                sys.exit(0)

        progressbar = ttk.Progressbar(mode="indeterminate")
        progressbar.place(x=1027, y=545, width=100)
        progressbar.start(10)

        Transfer_InProcress = tk.Label(
            Move_Frame, bg="#dbdbdb", fg="#382d2b", text="Transfering...")
        Transfer_InProcress.place(x=1080, y=522)

        if RadioValue_10.get() == 0:
            Call_Move = ["robocopy", Src, Dst, "/S",
                         "/ZB", "/XJ", "/R:0", "/W:0","/TEE", "/COPYALL", r"/log:logs\Log_Copy_10_" + Move_Module_Name_10.get() + ".txt"]
            Call_Move.extend(Files_Extensions_Read)
            call(Call_Move)
            Log_Copy_10()

        if RadioValue_10.get() == 1:

            Call_Move = ["robocopy", Src, Dst, "/S",
                         "/ZB", "/XJ", "/R:0", "/W:0","/TEE", "/MOVE", r"/log:logs\Log_Move_10_" + Move_Module_Name_10.get() + ".txt"]
            Call_Move.extend(Files_Extensions_Read)
            call(Call_Move)
            Log_Move_10()

        progressbar.destroy()
        Transfer_InProcress.destroy()

        Transfer_Completed = tk.Label(
            Move_Frame, bg="#dbdbdb", fg="#382d2b", text="Transfer completed at " + time.strftime("%H:%M:%S"))
        Transfer_Completed.place(x=930, y=545)

    except WindowsError:
        pass
    except SyntaxError:
        pass
    except ValueError:
        pass
    except TypeError:
        pass
    except FileNotFoundError:
        Path_Error = messagebox.showwarning(
            message="Path cannot be found (" + Src + ")", title="MeCopy")
        pass
    except pywintypes.error:
        Path_Error = messagebox.showwarning(message="The source path or destination of "+parser.get(
            "Path_Names", "path_name_10")+" is misspelled or do not exist.", title="MeCopy")
        pass


# START_MOVE_THREADS


def schedule_check(Patch_1_Thread):
    root.after(1000, check_if_done, Patch_1_Thread)


def check_if_done(Patch_1_Thread):
    if not Patch_1_Thread.is_alive():
        Btn_Move_1["state"] = "normal"
        btnFind5["state"] = "normal"
    else:
        schedule_check(Patch_1_Thread)


def Move_1_Thread():
    Btn_Move_1["state"] = "disabled"
    btnFind5["state"] = "disabled"
    Patch_1_Thread = threading.Thread(target=Transfer_Module_1)
    Patch_1_Thread.start()
    schedule_check(Patch_1_Thread)


def schedule_check_2(Patch_2_Thread):
    root.after(1000, check_if_done_2, Patch_2_Thread)


def check_if_done_2(Patch_2_Thread):
    if not Patch_2_Thread.is_alive():
        Btn_Move_2["state"] = "normal"
        btnFind5["state"] = "normal"
    else:
        schedule_check_2(Patch_2_Thread)


def Move_2_Thread():
    Btn_Move_2["state"] = "disabled"
    btnFind5["state"] = "disabled"
    Patch_2_Thread = threading.Thread(target=Transfer_Module_2)
    Patch_2_Thread.start()
    schedule_check_2(Patch_2_Thread)


def schedule_check_3(Patch_3_Thread):
    root.after(1000, check_if_done_3, Patch_3_Thread)


def check_if_done_3(Patch_3_Thread):
    if not Patch_3_Thread.is_alive():
        Btn_Move_3["state"] = "normal"
        btnFind5["state"] = "normal"
    else:
        schedule_check_3(Patch_3_Thread)


def Move_3_Thread():
    Btn_Move_3["state"] = "disabled"
    btnFind5["state"] = "disabled"
    Patch_3_Thread = threading.Thread(target=Transfer_Module_3)
    Patch_3_Thread.start()
    schedule_check_3(Patch_3_Thread)


def schedule_check_4(Patch_4_Thread):
    root.after(1000, check_if_done_4, Patch_4_Thread)


def check_if_done_4(Patch_4_Thread):
    if not Patch_4_Thread.is_alive():
        Btn_Move_4["state"] = "normal"
        btnFind5["state"] = "normal"
    else:
        schedule_check_4(Patch_4_Thread)


def Move_4_Thread():
    Btn_Move_4["state"] = "disabled"
    btnFind5["state"] = "disabled"
    Patch_4_Thread = threading.Thread(target=Transfer_Module_4)
    Patch_4_Thread.start()
    schedule_check_4(Patch_4_Thread)


def schedule_check_5(Patch_5_Thread):
    root.after(1000, check_if_done_5, Patch_5_Thread)


def check_if_done_5(Patch_5_Thread):
    if not Patch_5_Thread.is_alive():
        Btn_Move_5["state"] = "normal"
        btnFind5["state"] = "normal"
    else:
        schedule_check_5(Patch_5_Thread)


def Move_5_Thread():
    Btn_Move_5["state"] = "disabled"
    btnFind5["state"] = "disabled"
    Patch_5_Thread = threading.Thread(target=Transfer_Module_5)
    Patch_5_Thread.start()
    schedule_check_5(Patch_5_Thread)


def schedule_check_6(Patch_6_Thread):
    root.after(1000, check_if_done_6, Patch_6_Thread)


def check_if_done_6(Patch_6_Thread):
    if not Patch_6_Thread.is_alive():
        Btn_Move_6["state"] = "normal"
        btnFind5["state"] = "normal"
    else:
        schedule_check_6(Patch_6_Thread)


def Move_6_Thread():
    Btn_Move_6["state"] = "disabled"
    btnFind5["state"] = "disabled"
    Patch_6_Thread = threading.Thread(target=Transfer_Module_6)
    Patch_6_Thread.start()
    schedule_check_6(Patch_6_Thread)


def schedule_check_7(Patch_7_Thread):
    root.after(1000, check_if_done_7, Patch_7_Thread)


def check_if_done_7(Patch_7_Thread):
    if not Patch_7_Thread.is_alive():
        Btn_Move_7["state"] = "normal"
        btnFind5["state"] = "normal"
    else:
        schedule_check_7(Patch_7_Thread)


def Move_7_Thread():
    Btn_Move_7["state"] = "disabled"
    btnFind5["state"] = "disabled"
    Patch_7_Thread = threading.Thread(target=Transfer_Module_7)
    Patch_7_Thread.start()
    schedule_check_7(Patch_7_Thread)


def schedule_check_8(Patch_8_Thread):
    root.after(1000, check_if_done_8, Patch_8_Thread)


def check_if_done_8(Patch_8_Thread):
    if not Patch_8_Thread.is_alive():
        Btn_Move_8["state"] = "normal"
        btnFind5["state"] = "normal"
    else:
        schedule_check_8(Patch_8_Thread)


def Move_8_Thread():
    Btn_Move_8["state"] = "disabled"
    btnFind5["state"] = "disabled"
    Patch_8_Thread = threading.Thread(target=Transfer_Module_8)
    Patch_8_Thread.start()
    schedule_check_8(Patch_8_Thread)


def schedule_check_9(Patch_9_Thread):
    root.after(1000, check_if_done_9, Patch_9_Thread)


def check_if_done_9(Patch_9_Thread):
    if not Patch_9_Thread.is_alive():
        Btn_Move_9["state"] = "normal"
        btnFind5["state"] = "normal"
    else:
        schedule_check_9(Patch_9_Thread)


def Move_9_Thread():
    Btn_Move_9["state"] = "disabled"
    btnFind5["state"] = "disabled"
    Patch_9_Thread = threading.Thread(target=Transfer_Module_9)
    Patch_9_Thread.start()
    schedule_check_9(Patch_9_Thread)


def schedule_check_10(Patch_10_Thread):
    root.after(1000, check_if_done_10, Patch_10_Thread)


def check_if_done_10(Patch_10_Thread):
    if not Patch_10_Thread.is_alive():
        Btn_Move_10["state"] = "normal"
        btnFind5["state"] = "normal"
    else:
        schedule_check_10(Patch_10_Thread)


def Move_10_Thread():
    Btn_Move_10["state"] = "disabled"
    btnFind5["state"] = "disabled"
    Patch_10_Thread = threading.Thread(target=Transfer_Module_10)
    Patch_10_Thread.start()
    schedule_check_10(Patch_10_Thread)
# END_MOVE_THREADS



# DEL_SRC_REQUEST_START


def Get_Src_Del_1():
    Src_Del_Path_Selected = filedialog.askdirectory()
    Src_Del_Path.set(Src_Del_Path_Selected)


Src_Del_Path = tk.StringVar()
Del_Extensions_1 = tk.StringVar()
Path_Name_Del_1 = tk.StringVar()

Src_Del_Path.set(parser.get("Paths_Src_2", "path_1"))

Src_Title_Del_1 = tk.Label(Delete_Frame, text="Search in:", fg="#382d2b",
                           bg="#dbdbdb", font=("Arial", "12", "bold")).place(x=64, y=19)

Patch_Del_Entry_1 = EntryEx(
    Delete_Frame, style="EntryStyle.TEntry", textvariable=Src_Del_Path).place(x=155, y=22)
Button_Search_Path_Del_1 = ttk.Button(
    Delete_Frame, text="Search", style="flat.TButton", command=Get_Src_Del_1).place(x=282, y=21)

Path_Name_Del_1.set(parser.get("Path_Names_2", "path_name_1"))
Del_Extensions_1.set(parser.get("Extensions_2", "Search_1"))

Entry_Path_Del_1 = EntryEx(Delete_Frame, font="Helvetica 10 bold", width=27,
                           style="EntryStyle.TEntry_Paths", textvariable=Path_Name_Del_1).place(x=165, y=0)

Ext_Search_Del_1 = tk.Label(Delete_Frame, text="Extensions", fg="#382d2b",
                            bg="#dbdbdb", font=("Arial", "12", "bold")).place(x=380, y=0)

Entry_Del_Extensions_1 = EntryEx(
    Delete_Frame, style="EntryStyle.TEntry", textvariable=Del_Extensions_1).place(x=370, y=22)


def Get_Src_Del_2():
    Src_Del_Path_Selected_2 = filedialog.askdirectory()
    Src_Del_Path_2.set(Src_Del_Path_Selected_2)


Src_Del_Path_2 = tk.StringVar()
Del_Extensions_2 = tk.StringVar()
Path_Name_Del_2 = tk.StringVar()

Src_Del_Path_2.set(parser.get("Paths_Src_2", "path_2"))

Src_Title_Del_2 = tk.Label(Delete_Frame, text="Search in:", fg="#382d2b",
                           bg="#dbdbdb", font=("Arial", "12", "bold")).place(x=64, y=130)

Patch_Del_Entry_2 = EntryEx(Delete_Frame, style="EntryStyle.TEntry",
                            textvariable=Src_Del_Path_2).place(x=155, y=133)

Button_Search_Path_Del_2 = ttk.Button(
    Delete_Frame, text="Search", style="flat.TButton", command=Get_Src_Del_2).place(x=282, y=132)

Path_Name_Del_2.set(parser.get("Path_Names_2", "path_name_2"))
Del_Extensions_2.set(parser.get("Extensions_2", "Search_2"))

Entry_Path_Del_2 = EntryEx(Delete_Frame, font="Helvetica 10 bold", width=27,
                           style="EntryStyle.TEntry_Paths", textvariable=Path_Name_Del_2).place(x=165, y=112)

Ext_Search_Del_2 = tk.Label(Delete_Frame, text="Extensions", fg="#382d2b",
                            bg="#dbdbdb", font=("Arial", "12", "bold")).place(x=380, y=110)

Entry_Del_Extensions_2 = EntryEx(
    Delete_Frame, style="EntryStyle.TEntry", textvariable=Del_Extensions_2).place(x=370, y=133)


def Get_Src_Del_3():
    Src_Del_Path_Selected_3 = filedialog.askdirectory()
    Src_Del_Path_3.set(Src_Del_Path_Selected_3)


Src_Del_Path_3 = tk.StringVar()
Del_Extensions_3 = tk.StringVar()
Path_Name_Del_3 = tk.StringVar()

Src_Del_Path_3.set(parser.get("Paths_Src_2", "path_3"))

Src_Title_Del_3 = tk.Label(Delete_Frame, text="Search in:", fg="#382d2b",
                           bg="#dbdbdb", font=("Arial", "12", "bold")).place(x=64, y=247)

Patch_Del_Entry_3 = EntryEx(Delete_Frame, style="EntryStyle.TEntry",
                            textvariable=Src_Del_Path_3).place(x=155, y=250)

Button_Search_Path_Del_3 = ttk.Button(
    Delete_Frame, text="Search", style="flat.TButton", command=Get_Src_Del_3).place(x=282, y=249)

Path_Name_Del_3.set(parser.get("Path_Names_2", "path_name_3"))
Del_Extensions_3.set(parser.get("Extensions_2", "Search_3"))

Entry_Path_Del_3 = EntryEx(Delete_Frame, font="Helvetica 10 bold", width=27,
                           style="EntryStyle.TEntry_Paths", textvariable=Path_Name_Del_3).place(x=165, y=225)

Ext_Search_Del_3 = tk.Label(Delete_Frame, text="Extensions", fg="#382d2b",
                            bg="#dbdbdb", font=("Arial", "12", "bold")).place(x=380, y=228)

Entry_Del_Extensions_3 = EntryEx(
    Delete_Frame, style="EntryStyle.TEntry", textvariable=Del_Extensions_3).place(x=370, y=251)


def Get_Src_Del_4():
    Src_Del_Path_Selected_4 = filedialog.askdirectory()
    Src_Del_Path_4.set(Src_Del_Path_Selected_4)


Src_Del_Path_4 = tk.StringVar()
Del_Extensions_4 = tk.StringVar()
Path_Name_Del_4 = tk.StringVar()

Src_Del_Path_4.set(parser.get("Paths_Src_2", "path_4"))

Src_Title_Del_4 = tk.Label(Delete_Frame, text="Search in:", fg="#382d2b",
                           bg="#dbdbdb", font=("Arial", "12", "bold")).place(x=64, y=365)

Patch_Del_Entry_4 = EntryEx(Delete_Frame, style="EntryStyle.TEntry",
                            textvariable=Src_Del_Path_4).place(x=155, y=369)

Button_Search_Path_Del_4 = ttk.Button(
    Delete_Frame, text="Search", style="flat.TButton", command=Get_Src_Del_4).place(x=282, y=368)

Path_Name_Del_4.set(parser.get("Path_Names_2", "path_name_4"))
Del_Extensions_4.set(parser.get("Extensions_2", "Search_4"))

Entry_Path_Del_4 = EntryEx(Delete_Frame, font="Helvetica 10 bold", width=27,
                           style="EntryStyle.TEntry_Paths", textvariable=Path_Name_Del_4).place(x=165, y=345)

Ext_Search_Del_4 = tk.Label(Delete_Frame, text="Extensions", fg="#382d2b",
                            bg="#dbdbdb", font=("Arial", "12", "bold")).place(x=380, y=347)

Entry_Del_Extensions_4 = EntryEx(
    Delete_Frame, style="EntryStyle.TEntry", textvariable=Del_Extensions_4).place(x=370, y=369)


def Get_Src_Del_5():
    Src_Del_Path_Selected_5 = filedialog.askdirectory()
    Src_Del_Path_5.set(Src_Del_Path_Selected_5)


Src_Del_Path_5 = tk.StringVar()
Del_Extensions_5 = tk.StringVar()
Path_Name_Del_5 = tk.StringVar()

Src_Del_Path_5.set(parser.get("Paths_Src_2", "path_5"))

Src_Title_Del_5 = tk.Label(Delete_Frame, text="Search in:", fg="#382d2b",
                           bg="#dbdbdb", font=("Arial", "12", "bold")).place(x=64, y=481)

Patch_Del_Entry_5 = EntryEx(Delete_Frame, style="EntryStyle.TEntry",
                            textvariable=Src_Del_Path_5).place(x=155, y=485)

Button_Search_Path_Del_5 = ttk.Button(
    Delete_Frame, text="Search", style="flat.TButton", command=Get_Src_Del_5).place(x=282, y=484)

Path_Name_Del_5.set(parser.get("Path_Names_2", "path_name_5"))
Del_Extensions_5.set(parser.get("Extensions_2", "Search_5"))

Entry_Path_Del_5 = EntryEx(Delete_Frame, font="Helvetica 10 bold", width=27,
                           style="EntryStyle.TEntry_Paths", textvariable=Path_Name_Del_5).place(x=165, y=462)

Ext_Search_Del_5 = tk.Label(Delete_Frame, text="Extensions", fg="#382d2b",
                            bg="#dbdbdb", font=("Arial", "12", "bold")).place(x=380, y=463)

Entry_Del_Extensions_5 = EntryEx(
    Delete_Frame, style="EntryStyle.TEntry", textvariable=Del_Extensions_5).place(x=370, y=486)


def Get_Src_Del_6():
    Src_Del_Path_Selected_6 = filedialog.askdirectory()
    Src_Del_Path_6.set(Src_Del_Path_Selected_6)


Src_Del_Path_6 = tk.StringVar()
Del_Extensions_6 = tk.StringVar()
Path_Name_Del_6 = tk.StringVar()

Src_Del_Path_6.set(parser.get("Paths_Src_2", "path_6"))

Src_Title_Del_6 = tk.Label(Delete_Frame, text="Search in:", fg="#382d2b",
                           bg="#dbdbdb", font=("Arial", "12", "bold")).place(x=654, y=19)

Patch_Del_Entry_6 = EntryEx(Delete_Frame, style="EntryStyle.TEntry",
                            textvariable=Src_Del_Path_6).place(x=746, y=22)

Button_Search_Path_Del_6 = ttk.Button(
    Delete_Frame, text="Search", style="flat.TButton", command=Get_Src_Del_6).place(x=873, y=21)

Path_Name_Del_6.set(parser.get("Path_Names_2", "path_name_6"))
Del_Extensions_6.set(parser.get("Extensions_2", "Search_6"))

Entry_Path_Del_6 = EntryEx(Delete_Frame, font="Helvetica 10 bold", width=27,
                           style="EntryStyle.TEntry_Paths", textvariable=Path_Name_Del_6).place(x=755, y=0)

Ext_Search_Del_6 = tk.Label(Delete_Frame, text="Extensions", fg="#382d2b",
                            bg="#dbdbdb", font=("Arial", "12", "bold")).place(x=970, y=0)

Entry_Del_Extensions_6 = EntryEx(
    Delete_Frame, style="EntryStyle.TEntry", textvariable=Del_Extensions_6).place(x=960, y=23)


def Get_Src_Del_7():
    Src_Del_Path_Selected_7 = filedialog.askdirectory()
    Src_Del_Path_7.set(Src_Del_Path_Selected_7)


Src_Del_Path_7 = tk.StringVar()
Del_Extensions_7 = tk.StringVar()
Path_Name_Del_7 = tk.StringVar()

Src_Del_Path_7.set(parser.get("Paths_Src_2", "path_7"))

Src_Title_Del_7 = tk.Label(Delete_Frame, text="Search in:", fg="#382d2b",
                           bg="#dbdbdb", font=("Arial", "12", "bold")).place(x=654, y=130)

Patch_Del_Entry_7 = EntryEx(Delete_Frame, style="EntryStyle.TEntry",
                            textvariable=Src_Del_Path_7).place(x=746, y=133)

Button_Search_Path_Del_7 = ttk.Button(
    Delete_Frame, text="Search", style="flat.TButton", command=Get_Src_Del_7).place(x=873, y=132)

Path_Name_Del_7.set(parser.get("Path_Names_2", "path_name_7"))
Del_Extensions_7.set(parser.get("Extensions_2", "Search_7"))

Entry_Path_Del_7 = EntryEx(Delete_Frame, font="Helvetica 10 bold", width=27,
                           style="EntryStyle.TEntry_Paths", textvariable=Path_Name_Del_7).place(x=755, y=112)

Ext_Search_Del_7 = tk.Label(Delete_Frame, text="Extensions", fg="#382d2b",
                            bg="#dbdbdb", font=("Arial", "12", "bold")).place(x=970, y=110)

Entry_Del_Extensions_7 = EntryEx(
    Delete_Frame, style="EntryStyle.TEntry", textvariable=Del_Extensions_7).place(x=960, y=134)


def Get_Src_Del_8():
    Src_Del_Path_Selected_8 = filedialog.askdirectory()
    Src_Del_Path_8.set(Src_Del_Path_Selected_8)


Src_Del_Path_8 = tk.StringVar()
Del_Extensions_8 = tk.StringVar()
Path_Name_Del_8 = tk.StringVar()

Src_Del_Path_8.set(parser.get("Paths_Src_2", "path_8"))

Src_Title_Del_8 = tk.Label(Delete_Frame, text="Search in:", fg="#382d2b",
                           bg="#dbdbdb", font=("Arial", "12", "bold")).place(x=654, y=247)

Patch_Del_Entry_8 = EntryEx(Delete_Frame, style="EntryStyle.TEntry",
                            textvariable=Src_Del_Path_8).place(x=746, y=250)

Button_Search_Path_Del_8 = ttk.Button(
    Delete_Frame, text="Search", style="flat.TButton", command=Get_Src_Del_8).place(x=873, y=249)

Path_Name_Del_8.set(parser.get("Path_Names_2", "path_name_8"))
Del_Extensions_8.set(parser.get("Extensions_2", "Search_8"))

Entry_Path_Del_8 = EntryEx(Delete_Frame, font="Helvetica 10 bold", width=27,
                           style="EntryStyle.TEntry_Paths", textvariable=Path_Name_Del_8).place(x=755, y=225)

Ext_Search_Del_8 = tk.Label(Delete_Frame, text="Extensions", fg="#382d2b",
                            bg="#dbdbdb", font=("Arial", "12", "bold")).place(x=970, y=228)

Entry_Del_Extensions_8 = EntryEx(
    Delete_Frame, style="EntryStyle.TEntry", textvariable=Del_Extensions_8).place(x=960, y=251)


def Get_Src_Del_9():
    Src_Del_Path_Selected_9 = filedialog.askdirectory()
    Src_Del_Path_9.set(Src_Del_Path_Selected_9)


Src_Del_Path_9 = tk.StringVar()
Del_Extensions_9 = tk.StringVar()
Path_Name_Del_9 = tk.StringVar()

Src_Del_Path_9.set(parser.get("Paths_Src_2", "path_9"))

Src_Title_Del_9 = tk.Label(Delete_Frame, text="Search in:", fg="#382d2b",
                           bg="#dbdbdb", font=("Arial", "12", "bold")).place(x=654, y=365)

Patch_Del_Entry_9 = EntryEx(Delete_Frame, style="EntryStyle.TEntry",
                            textvariable=Src_Del_Path_9).place(x=746, y=369)

Button_Search_Path_Del_9 = ttk.Button(
    Delete_Frame, text="Search", style="flat.TButton", command=Get_Src_Del_9).place(x=873, y=368)


Path_Name_Del_9.set(parser.get("Path_Names_2", "path_name_9"))
Del_Extensions_9.set(parser.get("Extensions_2", "Search_9"))

Entry_Path_Del_9 = EntryEx(Delete_Frame, font="Helvetica 10 bold", width=27,
                           style="EntryStyle.TEntry_Paths", textvariable=Path_Name_Del_9).place(x=755, y=345)

Ext_Search_Del_9 = tk.Label(Delete_Frame, text="Extensions", fg="#382d2b",
                            bg="#dbdbdb", font=("Arial", "12", "bold")).place(x=970, y=347)

Entry_Del_Extensions_9 = EntryEx(
    Delete_Frame, style="EntryStyle.TEntry", textvariable=Del_Extensions_9).place(x=960, y=370)


def Get_Src_Del_10():
    Src_Del_Path_Selected_10 = filedialog.askdirectory()
    Src_Del_Path_10.set(Src_Del_Path_Selected_10)


Src_Del_Path_10 = tk.StringVar()
Del_Extensions_10 = tk.StringVar()
Path_Name_Del_10 = tk.StringVar()

Src_Del_Path_10.set(parser.get("Paths_Src_2", "path_10"))

Src_Title_Del_10 = tk.Label(Delete_Frame, text="Search in:", fg="#382d2b",
                            bg="#dbdbdb", font=("Arial", "12", "bold")).place(x=654, y=481)

Patch_Del_Entry_10 = EntryEx(Delete_Frame, style="EntryStyle.TEntry",
                             textvariable=Src_Del_Path_10).place(x=746, y=485)

Button_Search_Path_Del_10 = ttk.Button(
    Delete_Frame, text="Search", style="flat.TButton", command=Get_Src_Del_10).place(x=873, y=484)

Path_Name_Del_10.set(parser.get("Path_Names_2", "path_name_10"))
Del_Extensions_10.set(parser.get("Extensions_2", "Search_10"))

Entry_Path_Del_10 = EntryEx(Delete_Frame, font="Helvetica 10 bold", width=27,
                            style="EntryStyle.TEntry_Paths", textvariable=Path_Name_Del_10).place(x=755, y=462)

Ext_Search_Del_10 = tk.Label(Delete_Frame, text="Extensions", fg="#382d2b",
                             bg="#dbdbdb", font=("Arial", "12", "bold")).place(x=970, y=462)

Entry_Del_Extensions_10 = EntryEx(
    Delete_Frame, style="EntryStyle.TEntry", textvariable=Del_Extensions_10).place(x=960, y=486)
#DEL_SRC_REQUEST_END


#DEL_MODULES_START


def Delete_Module_1():

    try:
        parser.set("Paths_Src_2", "path_1", Src_Del_Path.get())
        parser.set("Extensions_2", "Search_1", Del_Extensions_1.get())
        parser.set("Path_Names_2", "path_name_1", Path_Name_Del_1.get())

        with open('config.ini', 'w') as myconfig:
            parser.write(myconfig)

        Src = win32api.GetShortPathName(Src_Del_Path.get())
        Del_Extension_Read = literal_eval(parser.get("Extensions_2", "Search_1"))

        messagebox.showwarning(message="ATTENTION: All the specified files will be erased with this option (" + parser.get("Path_Names_2", "path_name_1") +
                               ") and will not be sent to recycle bin. If you select 'yes' in the  next tab, there is no turning back.", title="MeCopy")

        Alert_Del = tk.messagebox.askyesno(title="MeCopy", message="Are you sure you want to delete "+parser.get(
            "Path_Names_2", "path_name_1")+"? There is no turning back after this. ")

        if Alert_Del is True:

            try:

                progressbar = ttk.Progressbar(mode="indeterminate")
                progressbar.place(x=435, y=67, width=100)
                progressbar.start(10)

                Transfer_InProcress = tk.Label(
                    Delete_Frame, bg="#dbdbdb", fg="#382d2b", text="Removing...")
                Transfer_InProcress.place(x=487, y=45)

                for rootDir, subdirs, filenames in os.walk(Src):
                    for filename in fnmatch.filter(filenames, Del_Extension_Read):
                        try:
                            os.remove(os.path.join(rootDir, filename))
                        except OSError:
                            pass

            except WindowsError:
                pass

            progressbar.destroy()
            Transfer_InProcress.destroy()

            Deleting_Completed = tk.Label(
                Delete_Frame, bg="#dbdbdb", fg="#382d2b", text="Files deleted at  " + time.strftime("%H:%M:%S"))
            Deleting_Completed.place(x=340, y=67)

    except SyntaxError:
        pass
    except ValueError:
        pass
    except TypeError:
        pass
    except FileNotFoundError:
        Path_Error = messagebox.showwarning(
            message="Path cannot be found (" + Src + ")", title="MeCopy")
        pass
    except pywintypes.error:
        Path_Error = messagebox.showwarning(message="Path "+parser.get(
            "Path_Names_2", "path_name_1")+" is misspelled or do not exist.", title="MeCopy")
        pass


def Delete_Module_2():

    try:
        parser.set("Paths_Src_2", "path_2", Src_Del_Path_2.get())
        parser.set("Extensions_2", "Search_2", Del_Extensions_2.get())
        parser.set("Path_Names_2", "path_name_2", Path_Name_Del_2.get())

        with open('config.ini', 'w') as myconfig:
            parser.write(myconfig)

        Src = win32api.GetShortPathName(Src_Del_Path_2.get())
        Del_Extension_Read = literal_eval(
            parser.get("Extensions_2", "Search_2"))

        messagebox.showwarning(message="ATTENTION: All the specified files will be erased with this option (" + parser.get("Path_Names_2", "path_name_2") +
                               ") and will not be sent to recycle bin. If you select 'yes' in the  next tab, there is no turning back.", title="MeCopy")

        Alert_Del = tk.messagebox.askyesno(title="MeCopy", message="Are you sure you want to delete "+parser.get(
            "Path_Names_2", "path_name_2")+"? There is no turning back after this. ")

        if Alert_Del is True:

            try:

                progressbar = ttk.Progressbar(mode="indeterminate")
                progressbar.place(x=435, y=178, width=100)
                progressbar.start(10)

                Transfer_InProcress = tk.Label(
                    Delete_Frame, bg="#dbdbdb", fg="#382d2b", text="Removing...")
                Transfer_InProcress.place(x=487, y=157)

                for rootDir, subdirs, filenames in os.walk(Src):
                    for filename in fnmatch.filter(filenames, Del_Extension_Read):
                        try:
                            os.remove(os.path.join(rootDir, filename))
                        except OSError:
                            pass

            except WindowsError:
                pass

            Deleting_Completed = tk.Label(
                Delete_Frame, bg="#dbdbdb", fg="#382d2b", text="Files deleted at  " + time.strftime("%H:%M:%S"))
            Deleting_Completed.place(x=340, y=178)

            progressbar.destroy()
            Transfer_InProcress.destroy()

    except SyntaxError:
        pass
    except ValueError:
        pass
    except TypeError:
        pass
    except FileNotFoundError:
        Path_Error = messagebox.showwarning(
            message="Path cannot be found (" + Src + ")", title="MeCopy")
        pass
    except pywintypes.error:
        Path_Error = messagebox.showwarning(message="Path "+parser.get(
            "Path_Names_2", "path_name_2")+" is misspelled or do not exist.", title="MeCopy")
        pass


def Delete_Module_3():

    try:
        parser.set("Paths_Src_2", "path_3", Src_Del_Path_3.get())
        parser.set("Extensions_2", "Search_3", Del_Extensions_3.get())
        parser.set("Path_Names_2", "path_name_3", Path_Name_Del_3.get())

        with open('config.ini', 'w') as myconfig:
            parser.write(myconfig)

        Src = win32api.GetShortPathName(Src_Del_Path_3.get())
        Del_Extension_Read = literal_eval(
            parser.get("Extensions_2", "Search_3"))

        messagebox.showwarning(message="ATTENTION: All the specified files will be erased with this option (" + parser.get("Path_Names_2", "path_name_3") +
                               ") and will not be sent to recycle bin. If you select 'yes' in the  next tab, there is no turning back.", title="MeCopy")

        Alert_Del = tk.messagebox.askyesno(title="MeCopy", message="Are you sure you want to delete "+parser.get(
            "Path_Names_2", "path_name_3")+"? There is no turning back after this. ")

        if Alert_Del is True:

            try:

                progressbar = ttk.Progressbar(mode="indeterminate")
                progressbar.place(x=435, y=296, width=100)
                progressbar.start(10)

                Transfer_InProcress = tk.Label(
                    Delete_Frame, bg="#dbdbdb", fg="#382d2b", text="Removing...")
                Transfer_InProcress.place(x=487, y=275)

                for rootDir, subdirs, filenames in os.walk(Src):
                    for filename in fnmatch.filter(filenames, Del_Extension_Read):
                        try:
                            os.remove(os.path.join(rootDir, filename))
                        except OSError:
                            pass

            except WindowsError:
                pass

            progressbar.destroy()
            Transfer_InProcress.destroy()
            Deleting_Completed = tk.Label(
                Delete_Frame, bg="#dbdbdb", fg="#382d2b", text="Files deleted at  " + time.strftime("%H:%M:%S"))
            Deleting_Completed.place(x=340, y=296)

    except SyntaxError:
        pass
    except ValueError:
        pass
    except TypeError:
        pass
    except FileNotFoundError:
        Path_Error = messagebox.showwarning(
            message="Path cannot be found (" + Src + ")", title="MeCopy")
        pass
    except pywintypes.error:
        Path_Error = messagebox.showwarning(message="Path "+parser.get(
            "Path_Names_2", "path_name_3")+" is misspelled or do not exist.", title="MeCopy")
        pass


def Delete_Module_4():

    try:
        parser.set("Paths_Src_2", "path_4", Src_Del_Path_4.get())
        parser.set("Extensions_2", "Search_4", Del_Extensions_4.get())
        parser.set("Path_Names_2", "path_name_4", Path_Name_Del_4.get())

        with open('config.ini', 'w') as myconfig:
            parser.write(myconfig)

        Src = win32api.GetShortPathName(Src_Del_Path_4.get())
        Del_Extension_Read = literal_eval(
            parser.get("Extensions_2", "Search_4"))

        messagebox.showwarning(message="ATTENTION: All the specified files will be erased with this option (" + parser.get("Path_Names_2", "path_name_4") +
                               ") and will not be sent to recycle bin. If you select 'yes' in the  next tab, there is no turning back.", title="MeCopy")

        Alert_Del = tk.messagebox.askyesno(title="MeCopy", message="Are you sure you want to delete "+parser.get(
            "Path_Names_2", "path_name_4")+"? There is no turning back after this. ")

        if Alert_Del is True:

            try:

                progressbar = ttk.Progressbar(mode="indeterminate")
                progressbar.place(x=435, y=414, width=100)
                progressbar.start(10)

                Transfer_InProcress = tk.Label(
                    Delete_Frame, bg="#dbdbdb", fg="#382d2b", text="Removing...")
                Transfer_InProcress.place(x=487, y=393)

                for rootDir, subdirs, filenames in os.walk(Src):
                    for filename in fnmatch.filter(filenames, Del_Extension_Read):
                        try:
                            os.remove(os.path.join(rootDir, filename))
                        except OSError:
                            pass

            except WindowsError:
                pass

            Deleting_Completed = tk.Label(
                Delete_Frame, bg="#dbdbdb", fg="#382d2b", text="Files deleted at  " + time.strftime("%H:%M:%S"))
            Deleting_Completed.place(x=340, y=414)
            progressbar.destroy()
            Transfer_InProcress.destroy()

    except SyntaxError:
        pass
    except ValueError:
        pass
    except TypeError:
        pass
    except FileNotFoundError:
        Path_Error = messagebox.showwarning(
            message="Path cannot be found (" + Src + ")", title="MeCopy")
        pass
    except pywintypes.error:
        Path_Error = messagebox.showwarning(message="Path "+parser.get(
            "Path_Names_2", "path_name_4")+" is misspelled or do not exist.", title="MeCopy")
        pass


def Delete_Module_5():

    try:
        parser.set("Paths_Src_2", "path_5", Src_Del_Path_5.get())
        parser.set("Extensions_2", "Search_5", Del_Extensions_5.get())
        parser.set("Path_Names_2", "path_name_5", Path_Name_Del_5.get())

        with open('config.ini', 'w') as myconfig:
            parser.write(myconfig)

        Src = win32api.GetShortPathName(Src_Del_Path_5.get())
        Del_Extension_Read = literal_eval(
            parser.get("Extensions_2", "Search_5"))

        messagebox.showwarning(message="ATTENTION: All the specified files will be erased with this option (" + parser.get("Path_Names_2", "path_name_5") +
                               ") and will not be sent to recycle bin. If you select 'yes' in the  next tab, there is no turning back.", title="MeCopy")

        Alert_Del = tk.messagebox.askyesno(title="MeCopy", message="Are you sure you want to delete "+parser.get(
            "Path_Names_2", "path_name_5")+"? There is no turning back after this. ")

        if Alert_Del is True:

            try:

                progressbar = ttk.Progressbar(mode="indeterminate")
                progressbar.place(x=435, y=531, width=100)
                progressbar.start(10)

                Transfer_InProcress = tk.Label(
                    Delete_Frame, bg="#dbdbdb", fg="#382d2b", text="Removing...")
                Transfer_InProcress.place(x=487, y=510)

                for rootDir, subdirs, filenames in os.walk(Src):
                    for filename in fnmatch.filter(filenames, Del_Extension_Read):
                        try:
                            os.remove(os.path.join(rootDir, filename))
                        except OSError:
                            pass

            except WindowsError:
                pass

            Deleting_Completed = tk.Label(
                Delete_Frame, bg="#dbdbdb", fg="#382d2b", text="Files deleted at  " + time.strftime("%H:%M:%S"))
            Deleting_Completed.place(x=340, y=531)
            progressbar.destroy()
            Transfer_InProcress.destroy()

    except SyntaxError:
        pass
    except ValueError:
        pass
    except TypeError:
        pass
    except FileNotFoundError:
        Path_Error = messagebox.showwarning(
            message="Path cannot be found (" + Src + ")", title="MeCopy")
        pass
    except pywintypes.error:
        Path_Error = messagebox.showwarning(message="Path "+parser.get(
            "Path_Names_2", "path_name_5")+" is misspelled or do not exist.", title="MeCopy")
        pass


def Delete_Module_6():

    try:
        parser.set("Paths_Src_2", "path_6", Src_Del_Path_6.get())
        parser.set("Extensions_2", "Search_6", Del_Extensions_6.get())
        parser.set("Path_Names_2", "path_name_6", Path_Name_Del_6.get())

        with open('config.ini', 'w') as myconfig:
            parser.write(myconfig)

        Src = win32api.GetShortPathName(Src_Del_Path_6.get())
        Del_Extension_Read = literal_eval(
            parser.get("Extensions_2", "Search_6"))

        messagebox.showwarning(message="ATTENTION: All the specified files will be erased with this option (" + parser.get("Path_Names_2", "path_name_6") +
                               ") and will not be sent to recycle bin. If you select 'yes' in the  next tab, there is no turning back.", title="MeCopy")

        Alert_Del = tk.messagebox.askyesno(title="MeCopy", message="Are you sure you want to delete "+parser.get(
            "Path_Names_2", "path_name_6")+"? There is no turning back after this. ")

        if Alert_Del is True:

            try:

                progressbar = ttk.Progressbar(mode="indeterminate")
                progressbar.place(x=1029, y=67, width=100)
                progressbar.start(10)

                Transfer_InProcress = tk.Label(
                    Delete_Frame, bg="#dbdbdb", fg="#382d2b", text="Removing...")
                Transfer_InProcress.place(x=1080, y=45)

                for rootDir, subdirs, filenames in os.walk(Src):
                    for filename in fnmatch.filter(filenames, Del_Extension_Read):
                        try:
                            os.remove(os.path.join(rootDir, filename))
                        except OSError:
                            pass

            except WindowsError:
                pass

            Deleting_Completed = tk.Label(
                Delete_Frame, bg="#dbdbdb", fg="#382d2b", text="Files deleted at  " + time.strftime("%H:%M:%S"))
            Deleting_Completed.place(x=950, y=67)
            progressbar.destroy()
            Transfer_InProcress.destroy()

    except SyntaxError:
        pass
    except ValueError:
        pass
    except TypeError:
        pass
    except FileNotFoundError:
        Path_Error = messagebox.showwarning(
            message="Path cannot be found (" + Src + ")", title="MeCopy")
        pass
    except pywintypes.error:
        Path_Error = messagebox.showwarning(message="Path "+parser.get(
            "Path_Names_2", "path_name_6")+" is misspelled or do not exist.", title="MeCopy")
        pass


def Delete_Module_7():

    try:
        parser.set("Paths_Src_2", "path_7", Src_Del_Path_7.get())
        parser.set("Extensions_2", "Search_7", Del_Extensions_7.get())
        parser.set("Path_Names_2", "path_name_7", Path_Name_Del_7.get())

        with open('config.ini', 'w') as myconfig:
            parser.write(myconfig)

        Src = win32api.GetShortPathName(Src_Del_Path_7.get())
        Del_Extension_Read = literal_eval(
            parser.get("Extensions_2", "Search_7"))

        messagebox.showwarning(message="ATTENTION: All the specified files will be erased with this option (" + parser.get("Path_Names_2", "path_name_7") +
                               ") and will not be sent to recycle bin. If you select 'yes' in the  next tab, there is no turning back.", title="MeCopy")

        Alert_Del = tk.messagebox.askyesno(title="MeCopy", message="Are you sure you want to delete "+parser.get(
            "Path_Names_2", "path_name_7")+"? There is no turning back after this. ")

        if Alert_Del is True:

            try:

                progressbar = ttk.Progressbar(mode="indeterminate")
                progressbar.place(x=1029, y=178, width=100)
                progressbar.start(10)

                Transfer_InProcress = tk.Label(
                    Delete_Frame, bg="#dbdbdb", fg="#382d2b", text="Removing...")
                Transfer_InProcress.place(x=1080, y=157)

                for rootDir, subdirs, filenames in os.walk(Src):
                    for filename in fnmatch.filter(filenames, Del_Extension_Read):
                        try:
                            os.remove(os.path.join(rootDir, filename))
                        except OSError:
                            pass

            except WindowsError:
                pass

            Deleting_Completed = tk.Label(
                Delete_Frame, bg="#dbdbdb", fg="#382d2b", text="Files deleted at  " + time.strftime("%H:%M:%S"))
            Deleting_Completed.place(x=950, y=178)
            progressbar.destroy()
            Transfer_InProcress.destroy()

    except SyntaxError:
        pass
    except ValueError:
        pass
    except TypeError:
        pass
    except FileNotFoundError:
        Path_Error = messagebox.showwarning(
            message="Path cannot be found (" + Src + ")", title="MeCopy")
        pass
    except pywintypes.error:
        Path_Error = messagebox.showwarning(message="Path "+parser.get(
            "Path_Names_2", "path_name_7")+" is misspelled or do not exist.", title="MeCopy")
        pass


def Delete_Module_8():

    try:
        parser.set("Paths_Src_2", "path_8", Src_Del_Path_8.get())
        parser.set("Extensions_2", "Search_8", Del_Extensions_8.get())
        parser.set("Path_Names_2", "path_name_8", Path_Name_Del_8.get())

        with open('config.ini', 'w') as myconfig:
            parser.write(myconfig)

        Src = win32api.GetShortPathName(Src_Del_Path_8.get())
        Del_Extension_Read = literal_eval(
            parser.get("Extensions_2", "Search_8"))

        messagebox.showwarning(message="ATTENTION: All the specified files will be erased with this option (" + parser.get("Path_Names_2", "path_name_8") +
                               ") and will not be sent to recycle bin. If you select 'yes' in the  next tab, there is no turning back.", title="MeCopy")

        Alert_Del = tk.messagebox.askyesno(title="MeCopy", message="Are you sure you want to delete "+parser.get(
            "Path_Names_2", "path_name_8")+"? There is no turning back after this. ")

        if Alert_Del is True:

            try:

                progressbar = ttk.Progressbar(mode="indeterminate")
                progressbar.place(x=1029, y=296, width=100)
                progressbar.start(10)

                Transfer_InProcress = tk.Label(
                    Delete_Frame, bg="#dbdbdb", fg="#382d2b", text="Removing...")
                Transfer_InProcress.place(x=1080, y=275)

                for rootDir, subdirs, filenames in os.walk(Src):
                    for filename in fnmatch.filter(filenames, Del_Extension_Read):
                        try:
                            os.remove(os.path.join(rootDir, filename))
                        except OSError:
                            pass

            except WindowsError:
                pass

            Deleting_Completed = tk.Label(
                Delete_Frame, bg="#dbdbdb", fg="#382d2b", text="Files deleted at  " + time.strftime("%H:%M:%S"))
            Deleting_Completed.place(x=950, y=296)
            progressbar.destroy()
            Transfer_InProcress.destroy()

    except SyntaxError:
        pass
    except ValueError:
        pass
    except TypeError:
        pass
    except FileNotFoundError:
        Path_Error = messagebox.showwarning(
            message="Path cannot be found (" + Src + ")", title="MeCopy")
        pass
    except pywintypes.error:
        Path_Error = messagebox.showwarning(message="Path "+parser.get(
            "Path_Names_2", "path_name_8")+" is misspelled or do not exist.", title="MeCopy")
        pass


def Delete_Module_9():

    try:
        parser.set("Paths_Src_2", "path_9", Src_Del_Path_9.get())
        parser.set("Extensions_2", "Search_9", Del_Extensions_9.get())
        parser.set("Path_Names_2", "path_name_9", Path_Name_Del_9.get())

        with open('config.ini', 'w') as myconfig:
            parser.write(myconfig)

        Src = win32api.GetShortPathName(Src_Del_Path_9.get())
        Del_Extension_Read = literal_eval(
            parser.get("Extensions_2", "Search_9"))

        messagebox.showwarning(message="ATTENTION: All the specified files will be erased with this option (" + parser.get("Path_Names_2", "path_name_9") +
                               ") and will not be sent to recycle bin. If you select 'yes' in the  next tab, there is no turning back.", title="MeCopy")

        Alert_Del = tk.messagebox.askyesno(title="MeCopy", message="Are you sure you want to delete "+parser.get(
            "Path_Names_2", "path_name_9")+"? There is no turning back after this. ")

        if Alert_Del is True:

            try:

                progressbar = ttk.Progressbar(mode="indeterminate")
                progressbar.place(x=1029, y=414, width=100)
                progressbar.start(10)

                Transfer_InProcress = tk.Label(
                    Delete_Frame, bg="#dbdbdb", fg="#382d2b", text="Removing...")
                Transfer_InProcress.place(x=1080, y=393)

                for rootDir, subdirs, filenames in os.walk(Src):
                    for filename in fnmatch.filter(filenames, Del_Extension_Read):
                        try:
                            os.remove(os.path.join(rootDir, filename))
                        except OSError:
                            pass

            except WindowsError:
                pass

            Deleting_Completed = tk.Label(
                Delete_Frame, bg="#dbdbdb", fg="#382d2b", text="Files deleted at  " + time.strftime("%H:%M:%S"))
            Deleting_Completed.place(x=950, y=414)
            progressbar.destroy()
            Transfer_InProcress.destroy()

    except SyntaxError:
        pass
    except ValueError:
        pass
    except TypeError:
        pass
    except FileNotFoundError:
        Path_Error = messagebox.showwarning(
            message="Path cannot be found (" + Src + ")", title="MeCopy")
        pass
    except pywintypes.error:
        Path_Error = messagebox.showwarning(message="Path "+parser.get(
            "Path_Names_2", "path_name_9")+" is misspelled or do not exist.", title="MeCopy")
        pass


def Delete_Module_10():

    try:
        parser.set("Paths_Src_2", "path_10", Src_Del_Path_10.get())
        parser.set("Extensions_2", "Search_10", Del_Extensions_10.get())
        parser.set("Path_Names_2", "path_name_10", Path_Name_Del_10.get())

        with open('config.ini', 'w') as myconfig:
            parser.write(myconfig)

        Src = win32api.GetShortPathName(Src_Del_Path_10.get())
        Del_Extension_Read = literal_eval(
            parser.get("Extensions_2", "Search_10"))

        messagebox.showwarning(message="ATTENTION: All the specified files will be erased with this option (" + parser.get("Path_Names_2", "path_name_10") +
                               ") and will not be sent to recycle bin. If you select 'yes' in the  next tab, there is no turning back.", title="MeCopy")

        Alert_Del = tk.messagebox.askyesno(title="MeCopy", message="Are you sure you want to delete "+parser.get(
            "Path_Names_2", "path_name_10")+"? There is no turning back after this. ")

        if Alert_Del is True:

            try:

                progressbar = ttk.Progressbar(mode="indeterminate")
                progressbar.place(x=1029, y=531, width=100)
                progressbar.start(10)

                Transfer_InProcress = tk.Label(
                    Delete_Frame, bg="#dbdbdb", fg="#382d2b", text="Removing...")
                Transfer_InProcress.place(x=1080, y=510)

                for rootDir, subdirs, filenames in os.walk(Src):
                    for filename in fnmatch.filter(filenames, Del_Extension_Read):
                        try:
                            os.remove(os.path.join(rootDir, filename))
                        except OSError:
                            pass

            except WindowsError:
                pass

            Deleting_Completed = tk.Label(
                Delete_Frame, bg="#dbdbdb", fg="#382d2b", text="Files deleted at  " + time.strftime("%H:%M:%S"))
            Deleting_Completed.place(x=950, y=531)
            progressbar.destroy()
            Transfer_InProcress.destroy()

    except SyntaxError:
        pass
    except ValueError:
        pass
    except TypeError:
        pass
    except FileNotFoundError:
        Path_Error = messagebox.showwarning(
            message="Path cannot be found (" + Src + ")", title="MeCopy")
        pass
    except pywintypes.error:
        Path_Error = messagebox.showwarning(message="Path "+parser.get(
            "Path_Names_2", "path_name_10")+" is misspelled or do not exist.", title="MeCopy")
        pass
# DEL_MODULES_END


# START_DELETE_THREADS


def schedule_check_Del_1(Patch_1_Thread):
    root.after(1000, check_if_done_Del_1, Patch_1_Thread)


def check_if_done_Del_1(Patch_1_Thread):
    if not Patch_1_Thread.is_alive():
        Btn_Del_1["state"] = "normal"
        Del_All["state"] = "normal"
    else:
        schedule_check_Del_1(Patch_1_Thread)


def Delete_Module_1_Thread():
    Btn_Del_1["state"] = "disabled"
    Del_All["state"] = "disabled"
    Patch_1_Thread = threading.Thread(target=Delete_Module_1)
    Patch_1_Thread.start()
    schedule_check_Del_1(Patch_1_Thread)


def schedule_check_Del_2(Patch_2_Thread):
    root.after(1000, check_if_done_Del_2, Patch_2_Thread)


def check_if_done_Del_2(Patch_2_Thread):
    if not Patch_2_Thread.is_alive():
        Btn_Del_2["state"] = "normal"
        Del_All["state"] = "normal"
    else:
        schedule_check_Del_2(Patch_2_Thread)


def Delete_Module_2_Thread():
    Btn_Del_2["state"] = "disabled"
    Del_All["state"] = "disabled"
    Patch_2_Thread = threading.Thread(target=Delete_Module_2)
    Patch_2_Thread.start()
    schedule_check_Del_2(Patch_2_Thread)


def schedule_check_Del_3(Patch_3_Thread):
    root.after(1000, check_if_done_Del_3, Patch_3_Thread)


def check_if_done_Del_3(Patch_3_Thread):
    if not Patch_3_Thread.is_alive():
        Btn_Del_3["state"] = "normal"
        Del_All["state"] = "normal"
    else:
        schedule_check_Del_3(Patch_3_Thread)


def Delete_Module_3_Thread():
    Btn_Del_3["state"] = "disabled"
    Del_All["state"] = "disabled"
    Patch_3_Thread = threading.Thread(target=Delete_Module_3)
    Patch_3_Thread.start()
    schedule_check_Del_3(Patch_3_Thread)


def schedule_check_Del_4(Patch_4_Thread):
    root.after(1000, check_if_done_Del_4, Patch_4_Thread)


def check_if_done_Del_4(Patch_4_Thread):
    if not Patch_4_Thread.is_alive():
        Btn_Del_4["state"] = "normal"
        Del_All["state"] = "normal"
    else:
        schedule_check_Del_4(Patch_4_Thread)


def Delete_Module_4_Thread():
    Btn_Del_4["state"] = "disabled"
    Del_All["state"] = "disabled"
    Patch_4_Thread = threading.Thread(target=Delete_Module_4)
    Patch_4_Thread.start()
    schedule_check_Del_4(Patch_4_Thread)


def schedule_check_Del_5(Patch_5_Thread):
    root.after(1000, check_if_done_Del_5, Patch_5_Thread)


def check_if_done_Del_5(Patch_5_Thread):
    if not Patch_5_Thread.is_alive():
        Btn_Del_5["state"] = "normal"
        Del_All["state"] = "normal"
    else:
        schedule_check_Del_5(Patch_5_Thread)


def Delete_Module_5_Thread():
    Btn_Del_5["state"] = "disabled"
    Del_All["state"] = "disabled"
    Patch_5_Thread = threading.Thread(target=Delete_Module_5)
    Patch_5_Thread.start()
    schedule_check_Del_5(Patch_5_Thread)


def schedule_check_Del_6(Patch_6_Thread):
    root.after(1000, check_if_done_Del_6, Patch_6_Thread)


def check_if_done_Del_6(Patch_6_Thread):
    if not Patch_6_Thread.is_alive():
        Btn_Del_6["state"] = "normal"
        Del_All["state"] = "normal"
    else:
        schedule_check_Del_6(Patch_6_Thread)


def Delete_Module_6_Thread():
    Btn_Del_6["state"] = "disabled"
    Del_All["state"] = "disabled"
    Patch_6_Thread = threading.Thread(target=Delete_Module_6)
    Patch_6_Thread.start()
    schedule_check_Del_6(Patch_6_Thread)


def schedule_check_Del_7(Patch_7_Thread):
    root.after(1000, check_if_done_Del_7, Patch_7_Thread)


def check_if_done_Del_7(Patch_7_Thread):
    if not Patch_7_Thread.is_alive():
        Btn_Del_7["state"] = "normal"
        Del_All["state"] = "normal"
    else:
        schedule_check_Del_7(Patch_7_Thread)


def Delete_Module_7_Thread():
    Btn_Del_7["state"] = "disabled"
    Del_All["state"] = "disabled"
    Patch_7_Thread = threading.Thread(target=Delete_Module_7)
    Patch_7_Thread.start()
    schedule_check_Del_7(Patch_7_Thread)


def schedule_check_Del_8(Patch_8_Thread):
    root.after(1000, check_if_done_Del_8, Patch_8_Thread)


def check_if_done_Del_8(Patch_8_Thread):
    if not Patch_8_Thread.is_alive():
        Btn_Del_8["state"] = "normal"
        Del_All["state"] = "normal"
    else:
        schedule_check_Del_8(Patch_8_Thread)


def Delete_Module_8_Thread():
    Btn_Del_8["state"] = "disabled"
    Del_All["state"] = "disabled"
    Patch_8_Thread = threading.Thread(target=Delete_Module_8)
    Patch_8_Thread.start()
    schedule_check_Del_8(Patch_8_Thread)


def schedule_check_Del_9(Patch_9_Thread):
    root.after(1000, check_if_done_Del_9, Patch_9_Thread)


def check_if_done_Del_9(Patch_9_Thread):
    if not Patch_9_Thread.is_alive():
        Btn_Del_9["state"] = "normal"
        Del_All["state"] = "normal"
    else:
        schedule_check_Del_9(Patch_9_Thread)


def Delete_Module_9_Thread():
    Btn_Del_9["state"] = "disabled"
    Del_All["state"] = "disabled"
    Patch_9_Thread = threading.Thread(target=Delete_Module_9)
    Patch_9_Thread.start()
    schedule_check_Del_9(Patch_9_Thread)


def schedule_check_Del_10(Patch_10_Thread):
    root.after(1000, check_if_done_Del_10, Patch_10_Thread)


def check_if_done_Del_10(Patch_10_Thread):
    if not Patch_10_Thread.is_alive():
        Btn_Del_10["state"] = "normal"
        Del_All["state"] = "normal"
    else:
        schedule_check_Del_10(Patch_10_Thread)


def Delete_Module_10_Thread():
    Btn_Del_10["state"] = "disabled"
    Del_All["state"] = "disabled"
    Patch_10_Thread = threading.Thread(target=Delete_Module_10)
    Patch_10_Thread.start()
    schedule_check_Del_10(Patch_10_Thread)
# END_DELETE_THREADS


Change_Del = ttk.Button(Move_Frame, text="Delete Files ->",
                        command=lambda: raise_frame(Delete_Menu_Screen))
Change_Del.place(x=570, y=572)
Change_Move = ttk.Button(Delete_Frame, text=" <-Return",
                         command=lambda: raise_frame(Move_Screen))
Change_Move.place(x=480, y=572)

btnFind5 = ttk.Button(Move_Frame, text="Start All", command=lambda: [Move_1_Thread(), Move_2_Thread(), Move_3_Thread(
), Move_4_Thread(), Move_5_Thread(), Move_6_Thread(), Move_7_Thread(), Move_8_Thread(), Move_9_Thread(), Move_10_Thread()])
btnFind5.place(x=480, y=572)
Del_All = ttk.Button(Delete_Frame, text="Delete all", command=lambda: [Delete_Module_1_Thread(), Delete_Module_2_Thread(), Delete_Module_3_Thread(), Delete_Module_4_Thread(), Delete_Module_5_Thread(), Delete_Module_6_Thread(), Delete_Module_7_Thread(), Delete_Module_8_Thread(), Delete_Module_9_Thread(), Delete_Module_10_Thread()])
Del_All.place(x=570, y=572)

# MOVE BUTTONS
Btn_Move_1 = ttk.Button(Move_Frame, style="flat.TButton",
                        text="Start", command=lambda: [Move_1_Thread()])
Btn_Move_1.place(x=193, y=77)

Btn_Move_2 = ttk.Button(Move_Frame, style="flat.TButton",
                        text="Start", command=lambda: [Move_2_Thread()])
Btn_Move_2.place(x=193, y=190)

Btn_Move_3 = ttk.Button(Move_Frame, style="flat.TButton",
                        text="Start", command=lambda: [Move_3_Thread()])
Btn_Move_3.place(x=193, y=305)

Btn_Move_4 = ttk.Button(Move_Frame, style="flat.TButton",
                        text="Start", command=lambda: [Move_4_Thread()])
Btn_Move_4.place(x=193, y=424)

Btn_Move_5 = ttk.Button(Move_Frame, style="flat.TButton",
                        text="Start", command=lambda: [Move_5_Thread()])
Btn_Move_5.place(x=193, y=540)

Btn_Move_6 = ttk.Button(Move_Frame, style="flat.TButton",
                        text="Start", command=lambda: [Move_6_Thread()])
Btn_Move_6.place(x=778, y=77)

Btn_Move_7 = ttk.Button(Move_Frame, style="flat.TButton",
                        text="Start", command=lambda: [Move_7_Thread()])
Btn_Move_7.place(x=778, y=190)

Btn_Move_8 = ttk.Button(Move_Frame, style="flat.TButton",
                        text="Start", command=lambda: [Move_8_Thread()])
Btn_Move_8.place(x=778, y=305)

Btn_Move_9 = ttk.Button(Move_Frame, style="flat.TButton",
                        text="Start", command=lambda: [Move_9_Thread()])
Btn_Move_9.place(x=778, y=424)

Btn_Move_10 = ttk.Button(Move_Frame, style="flat.TButton",
                         text="Start", command=lambda: [Move_10_Thread()])
Btn_Move_10.place(x=785, y=540)
# END MOVE BUTTONS

# DEL BUTTONS
Btn_Del_1 = ttk.Button(Delete_Frame, style="flat.TButton",
                       text=" Delete", command=lambda: [Delete_Module_1_Thread()])
Btn_Del_1.place(x=193, y=50)

Btn_Del_2 = ttk.Button(Delete_Frame, style="flat.TButton",
                       text=" Delete", command=lambda: [Delete_Module_2_Thread()])
Btn_Del_2.place(x=193, y=160)

Btn_Del_3 = ttk.Button(Delete_Frame, style="flat.TButton",
                       text=" Delete", command=lambda: [Delete_Module_3_Thread()])
Btn_Del_3.place(x=193, y=277)

Btn_Del_4 = ttk.Button(Delete_Frame, style="flat.TButton",
                       text=" Delete", command=lambda: [Delete_Module_4_Thread()])
Btn_Del_4.place(x=193, y=396)

Btn_Del_5 = ttk.Button(Delete_Frame, style="flat.TButton",
                       text=" Delete", command=lambda: [Delete_Module_5_Thread()])
Btn_Del_5.place(x=193, y=512)

Btn_Del_6 = ttk.Button(Delete_Frame, style="flat.TButton",
                       text=" Delete", command=lambda: [Delete_Module_6_Thread()])
Btn_Del_6.place(x=778, y=50)

Btn_Del_7 = ttk.Button(Delete_Frame, style="flat.TButton",
                       text=" Delete", command=lambda: [Delete_Module_7_Thread()])
Btn_Del_7.place(x=778, y=160)

Btn_Del_8 = ttk.Button(Delete_Frame, style="flat.TButton",
                       text=" Delete", command=lambda: [Delete_Module_8_Thread()])
Btn_Del_8.place(x=778, y=277)

Btn_Del_9 = ttk.Button(Delete_Frame, style="flat.TButton",
                       text=" Delete", command=lambda: [Delete_Module_9_Thread()])
Btn_Del_9.place(x=778, y=396)

Btn_Del_10 = ttk.Button(Delete_Frame, style="flat.TButton",
                        text=" Delete", command=lambda: [Delete_Module_10_Thread()])
Btn_Del_10.place(x=785, y=512)
# END DEL BUTTONS

raise_frame(Move_Screen)

root.mainloop()

os.system('taskkill /f /im Robocopy.exe')

# START_MOVE_PATHS_NAMES
parser.set("Path_Names", "path_name_1", Move_Module_Name_1.get())

parser.set("Path_Names", "path_name_2", Move_Module_Name_2.get())

parser.set("Path_Names", "path_name_3", Move_Module_Name_3.get())

parser.set("Path_Names", "path_name_4", Move_Module_Name_4.get())

parser.set("Path_Names", "path_name_5", Move_Module_Name_5.get())

parser.set("Path_Names", "path_name_6", Move_Module_Name_6.get())

parser.set("Path_Names", "path_name_7", Move_Module_Name_7.get())

parser.set("Path_Names", "path_name_8", Move_Module_Name_8.get())

parser.set("Path_Names", "path_name_9", Move_Module_Name_9.get())

parser.set("Path_Names", "path_name_10", Move_Module_Name_10.get())
# END_MOVE_PATHS_NAMES

# START_SRC_MOVE_PATHS
parser.set("Paths_Src", "path_1", Src_Path_1.get())

parser.set("Paths_Src", "path_2", Src_Path_2.get())

parser.set("Paths_Src", "path_3", Src_Path_3.get())

parser.set("Paths_Src", "path_4", Src_Path_4.get())

parser.set("Paths_Src", "path_5", Src_Path_5.get())

parser.set("Paths_Src", "path_6", Src_Path_6.get())

parser.set("Paths_Src", "path_7", Src_Path_7.get())

parser.set("Paths_Src", "path_8", Src_Path_8.get())

parser.set("Paths_Src", "path_9", Src_Path_9.get())

parser.set("Paths_Src", "path_10", Src_Path_10.get())
# END_SRC_MOVE_PATHS

# START_DST_MOVE_PATHS
parser.set("Paths_Dst", "path_1", Dst_Path_1.get())

parser.set("Paths_Dst", "path_2", Dst_Path_2.get())

parser.set("Paths_Dst", "path_3", Dst_Path_3.get())

parser.set("Paths_Dst", "path_4", Dst_Path_4.get())

parser.set("Paths_Dst", "path_5", Dst_Path_5.get())

parser.set("Paths_Dst", "path_6", Dst_Path_6.get())

parser.set("Paths_Dst", "path_7", Dst_Path_7.get())

parser.set("Paths_Dst", "path_8", Dst_Path_8.get())

parser.set("Paths_Dst", "path_9", Dst_Path_9.get())

parser.set("Paths_Dst", "path_10", Dst_Path_10.get())
# END_DST_MOVE_PATHS

# START_MOVE_EXTEMSIONS
parser.set("Extensions", "Search_1", Module_1_Extensions.get())

parser.set("Extensions", "Search_2", Module_2_Extensions.get())

parser.set("Extensions", "Search_3", Module_3_Extensions.get())

parser.set("Extensions", "Search_4", Module_4_Extensions.get())

parser.set("Extensions", "Search_5", Module_5_Extensions.get())

parser.set("Extensions", "Search_6", Module_6_Extensions.get())

parser.set("Extensions", "Search_7", Module_7_Extensions.get())

parser.set("Extensions", "Search_8", Module_8_Extensions.get())

parser.set("Extensions", "Search_9", Module_9_Extensions.get())

parser.set("Extensions", "Search_10", Module_10_Extensions.get())
# END_MOVE_EXTEMSIONS

# START_DELETE_PATHS_NAMES
parser.set("Path_Names_2", "path_name_1", Path_Name_Del_1.get())

parser.set("Path_Names_2", "path_name_2", Path_Name_Del_2.get())

parser.set("Path_Names_2", "path_name_3", Path_Name_Del_3.get())

parser.set("Path_Names_2", "path_name_4", Path_Name_Del_4.get())

parser.set("Path_Names_2", "path_name_5", Path_Name_Del_5.get())

parser.set("Path_Names_2", "path_name_6", Path_Name_Del_6.get())

parser.set("Path_Names_2", "path_name_7", Path_Name_Del_7.get())

parser.set("Path_Names_2", "path_name_8", Path_Name_Del_8.get())

parser.set("Path_Names_2", "path_name_9", Path_Name_Del_9.get())

parser.set("Path_Names_2", "path_name_10", Path_Name_Del_10.get())
# END_DELETE_PATHS_NAMES

# START_SRC_DELETE_PATHS
parser.set("Paths_Src_2", "path_1", Src_Del_Path.get())

parser.set("Paths_Src_2", "path_2", Src_Del_Path_2.get())

parser.set("Paths_Src_2", "path_3", Src_Del_Path_3.get())

parser.set("Paths_Src_2", "path_4", Src_Del_Path_4.get())

parser.set("Paths_Src_2", "path_5", Src_Del_Path_5.get())

parser.set("Paths_Src_2", "path_6", Src_Del_Path_6.get())

parser.set("Paths_Src_2", "path_7", Src_Del_Path_7.get())

parser.set("Paths_Src_2", "path_8", Src_Del_Path_8.get())

parser.set("Paths_Src_2", "path_9", Src_Del_Path_9.get())

parser.set("Paths_Src_2", "path_10", Src_Del_Path_10.get())
# END_SRC_DELETE_PATHS

# START_DELETE_EXTEMSIONS
parser.set("Extensions_2", "Search_1", Del_Extensions_1.get())

parser.set("Extensions_2", "Search_2", Del_Extensions_2.get())

parser.set("Extensions_2", "Search_3", Del_Extensions_3.get())

parser.set("Extensions_2", "Search_4", Del_Extensions_4.get())

parser.set("Extensions_2", "Search_5", Del_Extensions_5.get())

parser.set("Extensions_2", "Search_6", Del_Extensions_6.get())

parser.set("Extensions_2", "Search_7", Del_Extensions_7.get())

parser.set("Extensions_2", "Search_8", Del_Extensions_8.get())

parser.set("Extensions_2", "Search_9", Del_Extensions_9.get())

parser.set("Extensions_2", "Search_10", Del_Extensions_10.get())
# END_DELETE_EXTEMSIONS

with open('config.ini', 'w') as myconfig:
    parser.write(myconfig)