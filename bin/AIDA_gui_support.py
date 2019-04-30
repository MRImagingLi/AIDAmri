#! /usr/bin/env python
#  -*- coding: utf-8 -*-
#
# Support module generated by PAGE version 4.22
#  in conjunction with Tcl version 8.6
#    Apr 29, 2019 01:28:17 PM CEST  platform: Darwin

import sys, os

try:
    import Tkinter as tk

except ImportError:
    import tkinter as tk
    import tkinter.filedialog as fileDia
try:
    import ttk

    py3 = False
except ImportError:
    import tkinter.ttk as ttk

    py3 = True


def set_Tk_var():
    global filenameStr
    filenameStr = tk.StringVar()
    global rawVal
    rawVal = tk.StringVar()
    global t2Val
    t2Val = tk.StringVar()
    global dtiVal
    dtiVal = tk.StringVar()
    global fmriVal
    fmriVal = tk.StringVar()
    global preVal
    preVal = tk.StringVar()
    global regVal
    regVal = tk.StringVar()
    global postVal
    postVal = tk.StringVar()
    global codetxt
    codetxt = tk.StringVar()
    global pythonPrefix
    pythonPrefix = "python "
    global dataPrefix
    dataPrefix = tk.StringVar()
    dataPrefix.set("")
    global commandPrefix
    commandPrefix = tk.StringVar()
    commandPrefix.set("")


def deavitvateProcLabel(trigger):
    if trigger is False:
        w.checkPre.configure(state='normal')
        w.checkReg.configure(state='normal')
        w.checkPost.configure(state='normal')
    else:
        w.checkPre.configure(state='disabled')
        w.checkReg.configure(state='disabled')
        w.checkPost.configure(state='disabled')


def DTI_cmd():
    t2Val.set(0)
    fmriVal.set(0)
    rawVal.set(0)
    preVal.set(0)
    regVal.set(0)
    postVal.set(0)
    deavitvateProcLabel(False)
    codetxt.set("Choose Processing Option...")


def fMRI_cmd():
    t2Val.set(0)
    dtiVal.set(0)
    rawVal.set(0)
    preVal.set(0)
    regVal.set(0)
    postVal.set(0)
    deavitvateProcLabel(False)
    codetxt.set("Choose Processing Option...")


def rawCheck_cmd():
    t2Val.set(0)
    fmriVal.set(0)
    dtiVal.set(0)
    preVal.set(0)
    regVal.set(0)
    postVal.set(0)
    deavitvateProcLabel(True)
    dataPrefix.set("1_PV2NIfTiConverter")
    commandPrefix.set(os.path.join(dataPrefix.get(), "pv_conv2Nifti.py -i "))
    fullComand = pythonPrefix + commandPrefix.get() + filenameStr.get()
    codetxt.set(fullComand)


def t2Check_cmd():
    dtiVal.set(0)
    fmriVal.set(0)
    rawVal.set(0)
    preVal.set(0)
    regVal.set(0)
    postVal.set(0)
    deavitvateProcLabel(False)
    codetxt.set("Choose Processing Option...")


def post_cmd():
    preVal.set(0);
    regVal.set(0)
    if t2Val.get() is '1':
        dataPrefix.set("3.1_T2Processing")
        commandPrefix.set("getIncidenceSize.py -i ")
    elif dtiVal.get() is '1':
        dataPrefix.set("3.2_DTIConnectivity")
        commandPrefix.set("dsi_main.py -i")
    else:
        dataPrefix.set("3.3_fMRIActivity")
        commandPrefix.set("process_fMRI.py -i ")

    fullComand = pythonPrefix + os.path.join(dataPrefix.get(), commandPrefix.get()) + filenameStr.get()
    codetxt.set(fullComand)


def pre_cmd():
    postVal.set(0);
    regVal.set(0)
    if t2Val.get() is '1':
        dataPrefix.set("2.1_T2PreProcessing")
        commandPrefix.set("preProcessing_T2.py -i ")
    elif dtiVal.get() is '1':
        dataPrefix.set("2.2_DTIPreprocessing")
        commandPrefix.set("preProcessing_DTI.py -i ")
    else:
        dataPrefix.set("2.3_fMRIPreProcessing")
        commandPrefix.set("preProcessing_fMRI.py -i ")

    fullComand = pythonPrefix + os.path.join(dataPrefix.get(), commandPrefix.get()) + filenameStr.get()
    codetxt.set(fullComand)


def reg_cmd():
    preVal.set(0);
    postVal.set(0)
    if t2Val.get() is '1':
        dataPrefix.set("2.1_T2PreProcessing")
        commandPrefix.set("registration_T2.py -i ")
    elif dtiVal.get() is '1':
        dataPrefix.set("2.2_DTIPreprocessing")
        commandPrefix.set("registration_DTI.py -i ")
    else:
        dataPrefix.set("2.3_fMRIPreProcessing")
        commandPrefix.set("registration_rsfMRI.py -i ")

    fullComand = pythonPrefix + os.path.join(dataPrefix.get(), commandPrefix.get()) + filenameStr.get()
    codetxt.set(fullComand)


def open_cmd():
    if rawVal.get() == '1':
        filename = fileDia.askdirectory(title="Select path to raw data")
        filenameStr.set(filename)
    elif regVal.get() == '1':
        filename = fileDia.askopenfilename(title="Select file of BET data")
        filenameStr.set(filename)
    else:
        filename = fileDia.askopenfilename(title="Select file of raw NIfTI data")
        filenameStr.set(filename)

    sys.stdout.flush()
    fullComand = pythonPrefix + commandPrefix.get() + filenameStr.get()
    codetxt.set(fullComand)


def apply_cmdT():
    os.chdir(dataPrefix.get())
    print('cd ' + dataPrefix.get())
    fullComand = pythonPrefix + commandPrefix.get() + filenameStr.get()
    print(fullComand)
    os.system(fullComand)

    os.chdir('..')
    sys.stdout.flush()
    filenameStr.set("")


def init(top, gui, *args, **kwargs):
    global w, top_level, root
    w = gui
    top_level = top
    root = top


def destroy_window():
    # Function which closes the window.
    global top_level
    top_level.destroy()
    top_level = None


if __name__ == '__main__':
    import AIDA_gui

    AIDA_gui.vp_start_gui()
