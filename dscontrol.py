import sys
import time
import os
import random
import sched
import configparser
import getpass
from pywinauto import Application
from datetime import date,timedelta
from win32com.shell import shell, shellcon



ds_name = "Vinterflyging"
ds_port = "56278"
ds_password = "speider"
ds_admin_password = "sjefen"

ds_base_path = "c:\\condor2\\"
ds_app_path = os.path.join(ds_base_path,"condordedicated.exe")
ds_config_path = os.path.join(ds_base_path,"settings\\host.ini")

user_path = shell.SHGetFolderPath(0, shellcon.CSIDL_PERSONAL, None, 0)
sfl_path = os.path.join(user_path,"flightplan.sfl")
print(sfl_path)
fpl_files_folder = "Z:\\condor\\"

flight_plan_start_time = [19,30]

# Task parameters
task_start_time = [14,00]   
task_start_date = [2019,6,21]
task_start_delay = 5

ds_config = configparser.ConfigParser()
ds_config_file = open(ds_config_path,"w")

ds_config.add_section("General")
ds_config.set("General","ServerName",ds_name)
ds_config.set("General","Port",ds_port)
ds_config.set("General","Password",ds_password)
ds_config.set("General","AdminPassword",ds_admin_password)
ds_config.set("General","CompetitionName","")
ds_config.set("General","CompetitionPassword","")
ds_config.set("General","MaxPlayers","30")
ds_config.set("General","MinPlayers","1")
ds_config.set("General","MaxPing","40")
ds_config.set("General","JoinTimeLimit","45")
ds_config.set("General","AdvertiseOnWeb","1")
ds_config.set("General","AdvertiseManualIP","")
ds_config.set("General","AutomaticPortForwarding","0")
ds_config.set("General","AllowClientsToSaveFlightPlan","1")
ds_config.set("General","MaxTowplanes","4")
ds_config.add_section("DedicatedServer")
ds_config.set("DedicatedServer","LastSFL",sfl_path)
ds_config.write(ds_config_file)
ds_config_file.close()

# Select random flightplan from z:\condor\
fpl_files = [x for x in os.listdir(fpl_files_folder) if x.endswith(".fpl")]
fpl_file = random.choice(fpl_files)

sfl_file = open(sfl_path,"w")
sfl_file.write(fpl_files_folder + fpl_file + "\r\n")
sfl_file.close()
print("Selected fligtplan: " + fpl_file)

# Force Some parameters in flightplan
flight_plan = configparser.ConfigParser()
flight_plan.read(fpl_files_folder + fpl_file)
flight_plan['GameOptions']['StartTime'] = str(task_start_time[0]+task_start_time[1]/60.0)
flight_plan['GameOptions']['RaceStartDelay'] = str(task_start_delay/60)
flight_plan['GameOptions']['TaskDate'] = str((date(task_start_date[0],task_start_date[1],task_start_date[2])-date(1900,1,1)+timedelta(2)).days)
tmp_file = open(fpl_files_folder + fpl_file,"w")
flight_plan.write(tmp_file)
tmp_file.close()

# Start server application 
ds_app = Application().start(ds_app_path)

# Sleep until start time
start_tid = list(time.localtime())
start_tid[3] = flight_plan_start_time[0]
start_tid[4] = flight_plan_start_time[1]
start_tid[5] = 0  # Sekunder
start_tid_epoch = time.mktime(tuple(start_tid))
if start_tid_epoch > time.time():
    print("Sleep for start time: " + str(flight_plan_start_time[0]) + ":" + str(flight_plan_start_time[1]))
    time.sleep(start_tid_epoch - time.time())
else:
    print("Sleeping only 10 seconds!")
    time.sleep(10)

# Start flightplan, kl 19:30 søndager
print("STARTButton->click")
ds_app.TDedicatedForm.STARTButton.click()
time.sleep(10)

# Start flight
ds_app.TDedicatedForm.edit.send_keystrokes(".start")
ds_app.TDedicatedForm.edit.send_keystrokes("{ENTER}")


i = 0
while True:
    ds_log = ds_app.TDedicatedForm.TspSkinMemo.texts()
    ds_log_list = ds_log[0].split("\r\n")
    ds_log_list.pop()
    
    if len(ds_log_list) > i :
        for j in range(i, len(ds_log_list)):
            if ds_log_list[j].startswith("Flight started."):
                print("FLIGHT STARTED!")
            if ds_log_list[j].startswith("Server: stop"):
                print("STOPPING SERVER!")
                #ds_app.TDedicatedForm.STOPButton.click()
                #ds_app.Confirm.OK.click()
                #ds_app.TDedicatedForm.close_alt_f4()
                #ds_app.Confirm.OK.click()
                #exit()
        i = len(ds_log_list)
    time.sleep(2)

#os.system("shutdown /s /t 0")

# #Listbox2 -> Server name
# app.TDedicatedForm.Listbox2.item_texts()
# #Listbox4 -> Server status
# app.TDedicatedForm.Listbox4.item_texts()
# #Listbox6 -> Flightplan list
# app.TDedicatedForm.Listbox6.item_texts()
# #Listbox8 -> PLayers connected list
# app.TDedicatedForm.Listbox8.item_texts()
# #TspSkinMemo -> Server log
# app.TDedicatedForm.TspSkinMemo.texts()

# # Høyreklikk i Flightplan list
# app.TspSkinPopupWindow

# #.password	Password	Sets dedicated server password
# #.listids	No parameters	Lists IDs of all players
# #.kick	Player ID or Player CN	Kicks player from the game
# #.ban	Player ID or Player CN	Kicks player and adds them to the ban list
# #.stopjoin	No parameters | minutes | inf
# #.start
