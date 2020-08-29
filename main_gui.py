"""
Author: Tzvi Puchinsky
"""
import os
import webbrowser
import PySimpleGUI as sg
import main_pipeline as mp
from project_config import parser


def check_data_and_report(fileId, path):
    found_files = list()
    # Finds files for the provided ID if any
    for files in os.listdir(path):
        if os.path.isdir(os.path.join(path, files)):
            continue
        if files.split('_')[0] == str(fileId) and 'strip_output' in files:
            found_files.append(files)
    if not found_files:
        return 'No Files'
    else:
        res = list()
        for file in found_files:
            file = file[:-4]  # Remove .txtf
            if 'strip' in file:
                section = ' '.join(file[:file.index('strip') - 1].split('_')[1:])
            else:
                section = ' '.join(file[:file.index('output') - 1].split('_')[1:])
            if 'failed' in file.lower():
                cause = file.split('_')[-1]  # SEG OR PARSE
                res.append((section, file, cause))
            else:
                res.append((section, file, 'OK'))
        return res

# check_data_and_report(67, '/home/tzvi/PycharmProjects/linuxDiscourse/src/Output')
# ----- Menu -----------
menu_tool = [['Options', ['Show debug window', 'Disable lockdown', 'Enable lockdown']]]

# region ----- First Stage layout ------------------
first_stage_layout = [
    [sg.Text('First Stage\n--- Pre-Process ---', size=(30, 2), justification='center', font=("Helvetica", 15),
             relief=sg.RELIEF_RAISED, pad=((0, 0), (30, 10)))],
    [sg.Text('- Identify sections in the text\n- Create xml file\n- Create new text file based on xml file created',
             font=('Helvetica', 11))],
    [sg.Text('Input file path', size=(15, 1), justification='center'),
     sg.Input(disabled=True, size=(40, 1), key='filePathBrowse'),
     sg.FileBrowse()],
    [sg.Text('Discourse input\nfolder path', size=(15, 2), justification='center'),
     sg.Input(disabled=True, size=(40, 1), default_text=parser.get('main_pipeline', 'discourseInput'),
              key='discoursePathBrowse'), sg.FileBrowse()],
    [sg.Button('Process', key='process_button'), sg.Button('Next Stage', key='nextStage_button', visible=False)]
]
# endregion

# region ----- Second Stage layout ------------------
second_stage_layout = [
    [sg.Text('Second Stage\n--- Discourse Parsing ---', size=(30, 2), justification='center', font=("Helvetica", 15),
             relief=sg.RELIEF_RAISED)],
    [sg.Text(
        'Activating the discourse parsing script.\nThis script will create an RST tree with relations between all sentences.',
        font=('Helvetica', 11), justification='center')],
    [sg.Text('Complicated process that takes time. Be patient!', justification='center', font=("Helvetica", 11),
             text_color='black', background_color='grey')],
    [sg.Text('Discourse script\n path', size=(15, 2), justification='center'),
     sg.Input(disabled=True, size=(40, 1), default_text=parser.get('main_pipeline', 'discourse_script_path'),
              key='discourseScriptBrowse'), sg.FileBrowse()],
    [sg.Button('Process', key='process_button2')],
    [sg.Frame(layout=[
        [sg.Text('Discourse Output\nFolder', justification='center', size=(15, 2)),
                 sg.Input(disabled=True, size=(40, 1), default_text=parser.get('main_pipeline', 'trees_dir'), key='dOutputFolderPath'), sg.FileBrowse()],
        [sg.Button('Check Data', key='checkData')]
    ], title='Check if processed', relief=sg.RELIEF_SUNKEN, title_location=sg.TITLE_LOCATION_TOP, element_justification='center')],
    [sg.Button('Next Stage', key='nextStage_button2', visible=False)]
]
# endregion

# region ----- Third Stage layout ------------------
third_stage_layout = [
    [sg.Text('Third Stage\n--- Classify Trees ---', size=(30, 2), justification='center', font=("Helvetica", 15),
             relief=sg.RELIEF_RAISED, pad=((0, 0), (40, 10)))],
    [sg.Text(
        'Classify the text nodes in the discourse result tree files for all the sections.\nBased on pre-trained LDA models.',
        font=('Helvetica', 11), justification='center')],
    [sg.Frame(layout=[[sg.Checkbox('10 topics model', key='10', default=True),
                       sg.Checkbox('6 topics model', key='6', default=True),
                       sg.Checkbox('4 topics model', key='4', default=True)]],
              title='Pre-trained LDA models', relief=sg.RELIEF_SUNKEN, title_location=sg.TITLE_LOCATION_TOP)],
    [sg.Button('Process', key='process_button3'), sg.Button('Next Stage', key='nextStage_button3', visible=False)]
]
# endregion

# region ---- Fourth Stage layout ------------------
fourth_stage_layout = [
    [sg.Text('Fourth Stage\n--- Process Trees ---', size=(30, 2), justification='center', font=("Helvetica", 15),
             relief=sg.RELIEF_RAISED, pad=((0, 0), (40, 10)))],
    [sg.Text(
        'In this stage the program will process the discourse tree after topic classification and create units of\n'
        'small sub units in the tree. Each unit will have number of leaf nodes of the original discourse tree.\n'
        'Each unit will have only one topic number after calculating the weights of the nodes in the same unit.\n'
        'The calculation will be determined by effected by each node and if it Nucleus or Satellite and the place of the node\n'
        'in the hierarchy of the unit being built.',
        font=('Helvetica', 11), justification='center')],
    [sg.Button('Process', key='process_button4'), sg.Button('Next Stage', key='nextStage_button4', visible=False)]
]
# endregion

# region ---- Fifth Stage layout ------------------
fifth_stage_layout = [
    [sg.Text('Fifth Stage\n--- Create Show Case ---', size=(30, 2), justification='center', font=("Helvetica", 15),
             relief=sg.RELIEF_RAISED, pad=((0, 0), (40, 10)))],
    [sg.Text(
        'This stage collects all the data needed and parse it in json formats to create\n'
        'a local .html file to view the results in an interactive way.',
        font=('Helvetica', 11), justification='center')],
    [sg.Text('Choose model'), sg.Combo(['10 topic model', '6 topic model', '4 topic model'], default_value='10 topic model', key='topicChoice')],
    [sg.Button('Process', key='process_button5'), sg.Button('Show Case', key='show_case', visible=False)]
]
# endregion

# region -------------- Master Layout --------------
master_layout = [
    [sg.Menu(menu_tool)],
    [sg.TabGroup([[sg.Tab('First Stage', first_stage_layout, element_justification='center', key='firstStageTab'),
                   sg.Tab('Second Stage', second_stage_layout, element_justification='center', key='secondStageTab',
                          disabled=True),
                   sg.Tab('Third Stage', third_stage_layout, element_justification='center', key='thirdStageTab',
                          disabled=True),
                   sg.Tab('Fourth Stage', fourth_stage_layout, element_justification='center', key='fourthStageTab',
                          disabled=True),
                   sg.Tab('Fifth Stage', fifth_stage_layout, element_justification='center', key='fifthStageTab',
                          disabled=True)
                   ]])],
    # Bottom process bar
    [sg.Frame(layout=[[sg.Button('First Stage\nPre processing', size=(10, 2), key='first_stage_button', button_color=('black', 'yellow'), disabled_button_color=('black', 'yellow'), disabled=True),
                       sg.Button('Second Stage\nDiscourse parsing', size=(13, 2), key='second_stage_button', button_color=('black', 'yellow'), disabled_button_color=('black', 'yellow'), disabled=True),
                       sg.Button('Third Stage\nClassify sentences', size=(15, 2),
                                      key='third_stage_button', button_color=('black', 'yellow'), disabled_button_color=('black', 'yellow'), disabled=True),
                       sg.Button('Fourth Stage\nAnalyze Structure', size=(13, 2),
                                      key='fourth_stage_button', button_color=('black', 'yellow'), disabled_button_color=('black', 'yellow'), disabled=True),
                       sg.Button('Fifth Stage\nCreate show case', size=(13, 2),
                                      key='fifth_stage_button', button_color=('black', 'yellow'), disabled_button_color=('black', 'yellow'), disabled=True)]],
              title='Progress Bar',
              relief=sg.RELIEF_SUNKEN, title_location=sg.TITLE_LOCATION_TOP, key='progress_bar')
     ]
]
# endregion

# region Pop Up window
pop_up_layout=[
    [sg.Text('This are the files that already been processed\nand their status', justification='center')],
    [sg.MLine(key='-ml-'+sg.WRITE_ONLY_KEY, size=(120, 10), disabled=True)],
    [sg.Button('OK', key='popUpOk')]
]

pop_up_window = sg.Window('Data report', pop_up_layout, element_justification='center', finalize=True)
pop_up_window.hide()
# endregion

master_window = sg.Window('Hierarchical Summarization', master_layout, element_justification='center', size=(770, 460))
while True:  # The Event Loop
    event, values = master_window.read()
    print(event, values)  # TODO remove
    # region First Stage events
    if event is 'process_button':
        try:
            input_path = values['filePathBrowse']
            discourse_path = values['discoursePathBrowse']
            mp.first_stage(input_path, discourse_path)
            master_window['first_stage_button'].update(button_color=('white', 'green'),disabled_button_color=('white', 'green'))
            sg.popup_ok('Done', title='Notification')
            master_window['process_button'].update(visible=False)
            master_window['nextStage_button'].update(visible=True)
        except Exception as e:
            sg.popup_error(e, title='ERROR')
            master_window['first_stage_button'].update(button_color=('white', 'red'), disabled_button_color=('white', 'red'))
    if event is 'nextStage_button':
        master_window['secondStageTab'].update(disabled=False)
        master_window['secondStageTab'].select()
    # endregion
    # region Second Stage events
    if event is 'process_button2':
        try:
            # noinspection PyUnboundLocalVariable
            input_string = input_path.split(os.path.sep)[-1] + '.xml'
            script_path = values['discourseScriptBrowse']
            mp.second_stage(input_string, script_path)
            master_window['second_stage_button'].update(button_color=('white', 'green'), disabled_button_color=('white', 'green'))
            sg.popup_ok('Done', title='Notification')
            master_window['process_button2'].update(visible=False)
            master_window['nextStage_button2'].update(visible=True)
        except Exception as e:
            sg.popup_error(e, title='ERROR')
            master_window['second_stage_button'].update(button_color=('white', 'red'), disabled_button_color=('white', 'red'))
    if event is 'checkData':
        pop_up_window['-ml-' + sg.WRITE_ONLY_KEY].update(value='')
        res = check_data_and_report(input_path.split(os.path.sep)[-1][:-4], parser.get('main_pipeline', 'trees_dir'))  # TODO update file id
        if isinstance(res, list):
            for stat in res:
                pop_up_window['-ml-'+sg.WRITE_ONLY_KEY].print(stat[0] + ' | ' + stat[1] + ' | ', end='')
                pop_up_window['-ml-' + sg.WRITE_ONLY_KEY].print(stat[2], end='', background_color=('red' if stat[2] in ('SEG', 'PARSE') else 'green'))
                pop_up_window['-ml-' + sg.WRITE_ONLY_KEY].print('\n', end='')
            pop_up_window.un_hide()
            pop_event, pop_values = pop_up_window.read()
            pop_up_window.hide()
            master_window['nextStage_button2'].update(visible=True)
        else:
            sg.popup('No files, have to run process\nBrace yourself it takes time ;)', title='Note')
    if event is 'nextStage_button2':
        pop_up_window.close()
        master_window['second_stage_button'].update(button_color=('white', 'green'), disabled_button_color=('white', 'green'))
        master_window['thirdStageTab'].update(disabled=False)
        master_window['thirdStageTab'].select()
    # endregion
    # region Third Stage events
    if event is 'process_button3':
        try:
            # noinspection PyUnboundLocalVariable
            file_id = int(input_path.split(os.path.sep)[-1][:-4])
            models_dict = {'10': values['10'], '6': values['6'], '4': values['4'], 'hdp': values['hdp']}
            mp.third_stage(file_id, models_dict)
            master_window['third_stage_button'].update(button_color=('white', 'green'),disabled_button_color=('white', 'green'))
            sg.popup_ok('Done', title='Notification')
            master_window['process_button3'].update(visible=False)
            master_window['nextStage_button3'].update(visible=True)
        except MemoryError as e:
            sg.popup_error('Memory Error', title='ERROR')
            master_window['third_stage_button'].update(button_color=('white', 'red'), disabled_button_color=('white', 'red'))
        except Exception as e:
            sg.popup_error(e, title='ERROR')
            master_window['third_stage_button'].update(button_color=('white', 'red'), disabled_button_color=('white', 'red'))
    if event is 'nextStage_button3':
        master_window['fourthStageTab'].update(disabled=False)
        master_window['fourthStageTab'].select()
    # endregion
    # region Fourth Stage events
    if event is 'process_button4':
        try:
            # noinspection PyUnboundLocalVariable
            file_id = int(input_path.split(os.path.sep)[-1][:-4])
            mp.fourth_stage(file_id)
            master_window['fourth_stage_button'].update(button_color=('white', 'green'), disabled_button_color=('white', 'green'))
            sg.popup_ok('Done', title='Notification')
            master_window['process_button4'].update(visible=False)
            master_window['nextStage_button4'].update(visible=True)
        except Exception as e:
            sg.popup_error(e, title='ERROR')
            master_window['fourth_stage_button'].update(button_color=('white', 'red'), disabled_button_color=('white', 'red'))
    if event is 'nextStage_button4':
        master_window['fifthStageTab'].update(disabled=False)
        master_window['fifthStageTab'].select()
    # endregion
    # region Fifth Stage events
    if event is 'process_button5':
        choice = {'10 topic model': 10, '6 topic model': 6, '4 topic model': 4, 'HDP model': 20}
        try:
            # noinspection PyUnboundLocalVariable
            file_id = int(input_path.split(os.path.sep)[-1][:-4])
            url = mp.show_case(file_id, choice[values['topicChoice']])
            master_window['fifth_stage_button'].update(button_color=('white', 'green'), disabled_button_color=('white', 'green'))
            sg.popup_ok('Done', title='Notification')
            master_window['process_button5'].update(visible=False)
            master_window['show_case'].update(visible=True)
        except Exception as e:
            sg.popup_error(e, title='ERROR')
            master_window['fifth_stage_button'].update(button_color=('white', 'red'), disabled_button_color=('white', 'red'))
    if event is 'show_case':
        # noinspection PyUnboundLocalVariable
        webbrowser.open(url)
    # endregion
    # region -- Options Events ---
    if event is 'Disable lockdown':
        tabs_keys = ['secondStageTab', 'thirdStageTab', 'fourthStageTab', 'fifthStageTab']
        for tab in tabs_keys:
            master_window[tab].update(disabled=False)
        sg.popup_ok('All tabs are free now', title='Notification')
    if event is 'Enable lockdown':
        tabs_keys = ['secondStageTab', 'thirdStageTab']
        for tab in tabs_keys:
            master_window[tab].update(disabled=True)
        sg.popup_ok('All tabs are locked now', title='Notification')
    if event is 'Show debug window':
        sg.Print('Re-routing the stdout', do_not_reroute_stdout=False)
    # endregion
    if event in (None, 'Exit'):
        break
master_window.close()
