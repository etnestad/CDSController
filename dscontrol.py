import sys
import time
import os
import random
import sched
import configparser
import getpass
import shutil
from pywinauto import Application
from datetime import date,timedelta,datetime
from win32com.shell import shell, shellcon
from PIL import Image,ImageDraw,ImageFont


test_run = 0

ds_name = ""
ds_port = ""
ds_password = ""
ds_admin_password = ""
ds_base_path = ""
fpl_files_folder = ""

flight_plan_start_time = [19,30]
join_time_limit = "45" #  20:15
task_start_delay = 5   #  20:20

def open_server(ds_base_path):
	print(sys._getframe().f_code.co_name + " - ", end = '')
	ds_app_path = os.path.join(ds_base_path,"condordedicated.exe")
	ds_app = Application().start(ds_app_path)
	print("done!")
	return ds_app

def set_ds_config(ds_base_path):
	print(sys._getframe().f_code.co_name + " - ", end = '')
	global test_run
	ds_config_path = os.path.join(ds_base_path,"settings\\host.ini")
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
	ds_config.set("General","JoinTimeLimit",join_time_limit)
	if test_run == 0:
		ds_config.set("General","AdvertiseOnWeb","1")
	else:
		ds_config.set("General","AdvertiseOnWeb","0")
	ds_config.set("General","AdvertiseManualIP","")
	ds_config.set("General","AutomaticPortForwarding","0")
	ds_config.set("General","AllowClientsToSaveFlightPlan","1")
	ds_config.set("General","MaxTowplanes","4")
	ds_config.add_section("DedicatedServer")
	ds_config.set("DedicatedServer","LastSFL",sfl_path)
	ds_config.write(ds_config_file)
	ds_config_file.close()
	print("done!")

def select_random_flightplan(fpl_files_folder):
	print(sys._getframe().f_code.co_name + " - ", end = '')
	# Select random flightplan from fpl_files_folder
	fpl_files = [x for x in os.listdir(fpl_files_folder) if x.endswith(".fpl")]
	fpl_file = random.choice(fpl_files)
	fpl_file_path = os.path.join(fpl_files_folder,fpl_file)
	
	# Write flightplan to SFL
	sfl_file = open(sfl_path,"w")
	sfl_file.write(fpl_file_path + "\r\n")
	sfl_file.close()
	print("done!")
	return fpl_file_path
	
def set_flightplan_params(fpl_file_path):
	print(sys._getframe().f_code.co_name + " - ", end = '')
	# Force Some parameters in flightplan
	task_start_time = [14,00]
	task_start_date = [2019,6,21]
	
	flight_plan = configparser.ConfigParser()
	flight_plan.read(fpl_file_path)
	flight_plan['GameOptions']['StartTime'] = str(task_start_time[0]+task_start_time[1]/60.0)
	flight_plan['GameOptions']['RaceStartDelay'] = str(task_start_delay/60)
	flight_plan['GameOptions']['TaskDate'] = str((date(task_start_date[0],task_start_date[1],task_start_date[2])-date(1900,1,1)+timedelta(2)).days)
	tmp_file = open(fpl_file_path,"w")
	flight_plan.write(tmp_file)
	tmp_file.close()
	print("done!")

def start_time(flight_plan_start_time):
	global test_run
	start_tid = list(time.localtime())
	start_tid[3] = flight_plan_start_time[0]
	start_tid[4] = flight_plan_start_time[1]
	start_tid[5] = 0  # Sekunder
	start_tid_epoch = time.mktime(tuple(start_tid))
	if test_run != 0:
		return
	elif start_tid_epoch > time.time():
		print("Sleep for start time: " + str(flight_plan_start_time[0]) + ":" + str(flight_plan_start_time[1]))
		time.sleep(start_tid_epoch - time.time())
	else:
		print("Sleeping only 10 seconds!")
		time.sleep(10)

def start_server(app):
	print(sys._getframe().f_code.co_name + " - ", end = '')	
	app.TDedicatedForm.START.wait("exists enabled visible ready",5,0.5)
	while not app.TDedicatedForm.STOP.exists(timeout=1):
		try:
			app.TDedicatedForm.START.click()
		except:
			pass
	while "joining enabled" not in ds_app.TDedicatedForm.Listbox4.item_texts()[0]:
		time.sleep(0.5)
	print("done!")

def start_flight(app):
	print(sys._getframe().f_code.co_name + " - ", end = '')
	while "Flight started." not in str(app.TDedicatedForm.TspSkinMemo.texts()):
		app.TDedicatedForm.edit.wait("exists enabled visible ready",5,0.5)
		app.TDedicatedForm.edit.send_keystrokes(".start")
		app.TDedicatedForm.edit.send_keystrokes("{ENTER}")
		time.sleep(1)
	# Responsen til denne er "Flight started." i Server log
	print("done!")

def stop_server(app):
	print(sys._getframe().f_code.co_name + " - ", end = '')
	app.TDedicatedForm.STOP.wait("exists enabled visible ready",5,0.5)
	app.TDedicatedForm.STOP.click()
	app.Confirm.OK.wait("exists enabled visible ready",5,0.5)
	app.Confirm.OK.click()
	print("done!")
	
def close_server(app):
	print(sys._getframe().f_code.co_name + " - ", end = '')
	# app.TDedicatedForm.close_alt_f4()
	# app.Confirm.OK.wait("exists enabled visible ready",5,0.5)
	# app.Confirm.OK.click()
	app.kill()
	print("done!")

def server_messagehandler(app):
	global test_run
	server_stop = False
	i = 0

	while True:
		if server_stop == True:
			break
		ds_log = ds_app.TDedicatedForm.TspSkinMemo.texts()
		ds_log_list = ds_log[0].split("\r\n")
		ds_log_list.pop()

		if len(ds_log_list) > i :
			for j in range(i, len(ds_log_list)):
				if ds_log_list[j].startswith("Flight started."):
					print("FLIGHT STARTED!")
				if ds_log_list[j].startswith("Dedicated server restarting."):
					print("STOPPING SERVER!")
					server_stop = True
					break
			i = len(ds_log_list)
		if test_run == 0:
			time.sleep(2)			
		else:
			time.sleep(10)
			server_stop = True
	return server_stop

def read_inifile():
	print(sys._getframe().f_code.co_name + " - ", end = '')
	global ds_name
	global ds_port
	global ds_password
	global ds_admin_password
	global ds_base_path
	global fpl_files_folder
	
	config = configparser.ConfigParser()
	config.read("dscontrol.ini")
	
	ds_name = config['general']['servername']
	ds_port = config['general']['Port']
	ds_password = config['general']['Password']
	ds_admin_password = config['general']['AdminPassword']
	ds_base_path = config['general']['ServerBasePath']
	fpl_files_folder = config['general']['FlightPlansBasePath']
	print("done!")

def find_result_file(date_string):
	user_path = shell.SHGetFolderPath(0, shellcon.CSIDL_PERSONAL, None, 0)
	result_folder_path = os.path.join(user_path,"condor\\raceresults")
	
	for root, dirs, files in os.walk(result_folder_path):
		for name in files:
			if date_string + ".csv" in name:
				return os.path.join(root,name)
	return None

def make_result_png(result_file):
	global fpl_files_folder
	# Load result file
	linelist = [line.rstrip('\n') for line in open(result_file)]
	
	# Remove duplicates
	final_list = []
	name_list = []
	for line in linelist:
		name = line.split(',')[2]
		if name not in name_list:
			name_list.append(name)
			final_list.append(line)
	linelist = final_list
	
	if os.name == "posix":
		font = ImageFont.truetype("/usr/share/fonts/truetype/freefont/FreeSans.ttf",15)
		fontbold = ImageFont.truetype("/usr/share/fonts/truetype/freefont/FreeSansBold.ttf",15)
	else:
		font = ImageFont.truetype("arial.ttf",15)
		fontbold = ImageFont.truetype("arialbd.ttf",15)
	
	img = Image.new('RGB',(700,100),(255,255,255))
	d = ImageDraw.Draw(img)
	
	max_x_sizes = [0] * 11
	max_y_size = 0
	x_spacing = 10
	columns = [0,1,2,5,6,7,8,9,10]
	
	# Find sizes
	i = 0
	while i < len(linelist):
		line = linelist[i].split(',')
		
		for col in columns:
			if font.getsize(line[col])[0] > max_x_sizes[col]:
				max_x_sizes[col] = font.getsize(line[col])[0]
			if font.getsize(line[col])[1] > max_y_size:
				max_y_size = font.getsize(line[col])[1]
		i = i+1
	
	img_x_size = sum(max_x_sizes) + x_spacing * (len(columns)-1)
	img_y_size = len(linelist)*max_y_size
	img = Image.new('RGB',(img_x_size,img_y_size),(255,255,255))
	d = ImageDraw.Draw(img)
	
	i = 0
	while i < len(linelist):
		line = linelist[i].split(',')
		row = max_y_size*i
		
		for idx, col in enumerate(columns):
			if i == 0:
				d.text((sum(max_x_sizes[0:col])+x_spacing*idx,row), line[col], fill="black", font=fontbold)
			elif idx == 0:
				d.text((sum(max_x_sizes[0:col])+x_spacing*idx,row), str(i), fill="black", font=font)
			elif idx == 2:
				# Remove dot in names
				player = ' '.join([str(elem) for elem in line[col].split('.')])
				d.text((sum(max_x_sizes[0:col])+x_spacing*idx,row), player, fill="black", font=font)
			else:
				d.text((sum(max_x_sizes[0:col])+x_spacing*idx,row), line[col], fill="black", font=font)
		i = i+1
	base_name = os.path.basename(result_file)	
	img.save(os.path.join(fpl_files_folder,base_name.replace(".csv",".png")))

if __name__ == "__main__":
		
	if len(sys.argv) == 2 and sys.argv[1] == "test":
		print("TEST RUN!")
		test_run = 1
	
	read_inifile()
	
	user_path = shell.SHGetFolderPath(0, shellcon.CSIDL_PERSONAL, None, 0)
	sfl_path = os.path.join(user_path,"flightplan.sfl")

	date_string = datetime.now().strftime("%Y.%m.%d")
	
	set_ds_config(ds_base_path)
	fpl_file_path = select_random_flightplan(fpl_files_folder)
	set_flightplan_params(fpl_file_path)
	
	ds_app = open_server(ds_base_path)
	
	start_time(flight_plan_start_time)
	start_server(ds_app)
	start_flight(ds_app)

	server_stop = False
	server_stop = server_messagehandler(ds_app)

	if server_stop:
		stop_server(ds_app)
		close_server(ds_app)
		result_file = find_result_file(date_string)
		if result_file != None:
			shutil.copy(result_file,fpl_files_folder)
			make_result_png(result_file)
	exit()
    
# #Listbox2 -> Server name
# ds_app.TDedicatedForm.Listbox2.item_texts()

# #Listbox4 -> Server status
# ds_app.TDedicatedForm.Listbox4.item_texts()[0] - Status: server not running

# ds_app.TDedicatedForm.Listbox4.item_texts()[0] - Status: joining enabled
# ds_app.TDedicatedForm.Listbox4.item_texts()[1] - Time: HH:MM:SS
# ds_app.TDedicatedForm.Listbox4.item_texts()[2] - Stop join in: HH:MM:SS

# ds_app.TDedicatedForm.Listbox4.item_texts()[0] - Status: waiting for race start
# ds_app.TDedicatedForm.Listbox4.item_texts()[1] - Time: HH:MM:SS
# ds_app.TDedicatedForm.Listbox4.item_texts()[2] - Race starts in: HH:MM:SS

# ds_app.TDedicatedForm.Listbox4.item_texts()[0] - Status: race in progress
# ds_app.TDedicatedForm.Listbox4.item_texts()[1] - Time: HH:MM:SS
# ds_app.TDedicatedForm.Listbox4.item_texts()[2] - DistanceFlown: 0.0km
# ds_app.TDedicatedForm.Listbox4.item_texts()[3] - Leader:


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

