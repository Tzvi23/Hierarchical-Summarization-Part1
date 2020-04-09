import grapher
import PySimpleGUI as sg
import os

sg.change_look_and_feel("DarkBlue13")  # please make your creations colorful

currentFolder = os.getcwd()
layout = [[sg.Text('Choose file to process')],
		  [sg.Input(disabled=True), sg.FileBrowse(initial_folder=currentFolder)],
		  [sg.OK(), sg.Cancel()]]

mainWindow = sg.Window('HSFP', layout)

while True:
	event, values = mainWindow.Read()
	print(event, values)
	if event is None or event == 'Cancel':
		break
	if event == 'OK':
		layout = [[sg.Text('Choose file to process')],
				  [sg.Input(values[0], disabled=True), sg.FileBrowse(initial_folder=currentFolder)],
				  [sg.Button("Pre-Process"), sg.Cancel()]]
		pre_process_window = sg.Window('HSFP', layout)
		mainWindow.close()
		while True:
			event, values = pre_process_window.Read()
			if event is None or event == 'Cancel':
				pre_process_window.Close()
				exit()
			if event == 'Pre-Process':
				for i in range(1, 100):
					button = sg.OneLineProgressMeter('Pre Processing the file', i + 1, 100, 'key', 'Processing File', orientation='h')
					if button is False:
						break
				layout = [[sg.Text('Choose file to process')],
						  [sg.Input(values[0], disabled=True), sg.FileBrowse(initial_folder=currentFolder)],
						  [sg.Button("Summarize!"), sg.Cancel()]]
				summarize_window = sg.Window('HSFP', layout)
				pre_process_window.close()
				while True:
					event, value = summarize_window.Read()
					if event is None or event == 'Cancel':
						summarize_window.Close()
						exit()
					if event == 'Summarize!':
						grapher.draw_demo()
						buttons = list()
						for i in range(1, 20):
							buttons.append(sg.Button(str(i)))
						layout_chooser = [[sg.Text('Choose node to view summary')],
										  buttons,
										  [sg.Image(r'tree_figure.png')]]
						node_chooser = sg.Window('Choose Node', layout_chooser)
						event, value = node_chooser.Read()



# import tkinter as tk
# from tkinter.filedialog import askopenfile
#
# LARGE_FONT = ("Verdana", 12)
# HEIGHT = 300
# WIDTH = 300
#
#
# class HSFP(tk.Tk):
#     def __init__(self):
#         tk.Tk.__init__(self)
#         self.title("Hierarchical Summarization of Financial Reports HSFP")
#         container = tk.Frame(self)
#         container.pack(side="top", fill="both", expand=True)
#         container.grid_rowconfigure(0, weight=1)
#         container.grid_columnconfigure(0, weight=1)
#
#         self.frames = dict()
#
#         for F in (MainWindow, MainWindow):
#             frame = F(container, self)
#             self.frames[F] = frame
#             frame.grid(row=0, column=0, sticky="nsew")
#
#         self.show_frame(MainWindow)
#
#     def show_frame(self, cont):
#         frame = self.frames[cont]
#         frame.tkraise()
#
#
# class MainWindow(tk.Frame):
#     def __init__(self, parent, controller):
#         tk.Frame.__init__(self, parent)
#         self.parent = controller
#         self.parent.geometry('{}x{}'.format(HEIGHT, WIDTH))
#         self.chosenFile = None
#
#         # Inside frame
#         frame = tk.Frame(self)
#         frame.place(relx=0.1, rely=0.01, relwidth=0.8, relheight=0.9)
#
#         # Choose File button
#         self.button_chooseFile = tk.Button(frame, text='Choose file', command=lambda: self.chooseFile())
#         self.button_chooseFile.pack()
#
#         # Text Box for entry chosen
#         self.textEntry_chosenFile = tk.Entry(frame, state=tk.DISABLED)
#         self.textEntry_chosenFile.pack()
#
#         # Pre-Process button
#         self.button_PreProcess = tk.Button(frame, text='Pre - Process')
#         self.button_PreProcess.pack()
#
#     def chooseFile(self):
#         self.chosenFile = askopenfile(parent=tk.Frame(self), mode='rb', title='Choose file')
#         self.textEntry_chosenFile.insert(0, self.chosenFile)
#
#
# class ResultWindow(tk.Frame):
#     pass
#
#
# app = HSFP()
# app.mainloop()
