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

class DedicatedServer:
		
	test_run = 0
	
	
	# Server config from ini-file
	ds_name = ""
	ds_port = ""
	ds_password = ""
	ds_admin_password = ""
	ds_base_path = ""
	fpl_files_folder = ""
	
	# Pywinauto
	ds_app = 0
	
	# Paths	
	ds_app_path = ""
	flp_file_path = ""
	
	# Users home folder
	user_path = "" # Path to Documents folder
	result_folder_path = ""
	sfl_path = ""
	
	# Date of today.
	date_string = ""
	
	flight_plan_start_time = [19,30]
	join_time_limit = "45" #  20:15
	task_start_delay = 5   #  20:20
	
	def __init__(self,test_run):
		self.test_run = test_run
		self.__read_inifile()
		self.user_path = shell.SHGetFolderPath(0, shellcon.CSIDL_PERSONAL, None, 0)
		self.sfl_path = os.path.join(self.user_path,"flightplan.sfl")
		
		self.__set_ds_config()
		
		self.date_string = datetime.now().strftime("%Y.%m.%d")
		self.result_folder_path = os.path.join(self.user_path,"condor\\raceresults")
	
	def open_server(self):
		print(sys._getframe().f_code.co_name + " - ", end = '')
		self.ds_app_path = os.path.join(self.ds_base_path,"condordedicated.exe")
		self.ds_app = Application().start(self.ds_app_path)
		print("done!")
	
	def __set_ds_config(self):
		print("Write host.ini - ", end= '')
		ds_config_path = os.path.join(self.ds_base_path,"settings\\host.ini")
		ds_config = configparser.ConfigParser()
		ds_config_file = open(ds_config_path,"w")
		ds_config.add_section("General")
		ds_config.set("General","ServerName",self.ds_name)
		ds_config.set("General","Port",self.ds_port)
		ds_config.set("General","Password",self.ds_password)
		ds_config.set("General","AdminPassword",self.ds_admin_password)
		ds_config.set("General","CompetitionName","")
		ds_config.set("General","CompetitionPassword","")
		ds_config.set("General","MaxPlayers","30")
		ds_config.set("General","MinPlayers","1")
		ds_config.set("General","MaxPing","40")
		ds_config.set("General","JoinTimeLimit",self.join_time_limit)
		if self.test_run == 0:
			ds_config.set("General","AdvertiseOnWeb","1")
		else:
			ds_config.set("General","AdvertiseOnWeb","0")
		ds_config.set("General","AdvertiseManualIP","")
		ds_config.set("General","AutomaticPortForwarding","0")
		ds_config.set("General","AllowClientsToSaveFlightPlan","1")
		ds_config.set("General","MaxTowplanes","4")
		ds_config.add_section("DedicatedServer")
		ds_config.set("DedicatedServer","LastSFL",self.sfl_path)
		ds_config.write(ds_config_file)
		ds_config_file.close()
		print("done!")
	
	def select_random_flightplan(self):
		print("Select random flightplan:")
		# Select random flightplan from fpl_files_folder
		fpl_files = [x for x in os.listdir(self.fpl_files_folder) if x.endswith(".fpl")]
		fpl_file = random.choice(fpl_files)
		self.fpl_file_path = os.path.join(self.fpl_files_folder,fpl_file)
		
		# Write flightplan to SFL
		sfl_file = open(self.sfl_path,"w")
		sfl_file.write(self.fpl_file_path + "\r\n")
		sfl_file.close()
		print("* Flightplan = " + self.fpl_file_path)
		
	def set_flightplan_params(self):
		print("Set flightplan params - ", end = '')
		# Force Some parameters in flightplan
		task_start_time = [14,00]
		task_start_date = [2019,6,21]
		
		flight_plan = configparser.ConfigParser()
		flight_plan.read(self.fpl_file_path)
		flight_plan['GameOptions']['StartTime'] = str(task_start_time[0]+task_start_time[1]/60.0)
		flight_plan['GameOptions']['RaceStartDelay'] = str(self.task_start_delay/60)
		flight_plan['GameOptions']['TaskDate'] = str((date(task_start_date[0],task_start_date[1],task_start_date[2])-date(1900,1,1)+timedelta(2)).days)
		tmp_file = open(self.fpl_file_path,"w")
		flight_plan.write(tmp_file)
		tmp_file.close()
		print("done!")
	
	def sleep_for_start_time(self):
		start_tid = list(time.localtime())
		start_tid[3] = self.flight_plan_start_time[0]
		start_tid[4] = self.flight_plan_start_time[1]
		start_tid[5] = 0  # Sekunder
		start_tid_epoch = time.mktime(tuple(start_tid))
		if self.test_run != 0:
			return
		elif start_tid_epoch > time.time():
			print("Sleep for start time: " + str(self.flight_plan_start_time[0]) + ":" + str(self.flight_plan_start_time[1]))
			time.sleep(start_tid_epoch - time.time())
		else:
			print("Sleeping only 10 seconds!")
			time.sleep(10)
	
	def start_server(self):
		print(sys._getframe().f_code.co_name + " - ", end = '')	
		self.ds_app.TDedicatedForm.START.wait("exists enabled visible ready",5,0.5)
		while not self.ds_app.TDedicatedForm.STOP.exists(timeout=1):
			try:
				self.ds_app.TDedicatedForm.START.click()
			except:
				pass
		while "joining enabled" not in self.ds_app.TDedicatedForm.Listbox4.item_texts()[0]:
			time.sleep(0.5)
		print("done!")
	
	def start_flight(self):
		print(sys._getframe().f_code.co_name + " - ", end = '')
		while "Flight started." not in str(self.ds_app.TDedicatedForm.TspSkinMemo.texts()):
			self.ds_app.TDedicatedForm.edit.wait("exists enabled visible ready",5,0.5)
			self.ds_app.TDedicatedForm.edit.send_keystrokes(".start")
			self.ds_app.TDedicatedForm.edit.send_keystrokes("{ENTER}")
			time.sleep(1)
		# Responsen til denne er "Flight started." i Server log
		print("done!")
	
	def stop_server(self):
		print(sys._getframe().f_code.co_name + " - ", end = '')
		self.ds_app.TDedicatedForm.STOP.wait("exists enabled visible ready",5,0.5)
		self.ds_app.TDedicatedForm.STOP.click()
		self.ds_app.Confirm.OK.wait("exists enabled visible ready",5,0.5)
		self.ds_app.Confirm.OK.click()
		print("done!")
		
	def close_server(self):
		print(sys._getframe().f_code.co_name + " - ", end = '')
		self.ds_app.kill()
		print("done!")
	
	def messagehandler_loop(self):
		server_stop = False
		i = 0
	
		while True:
			if server_stop == True:
				break
			ds_log = self.ds_app.TDedicatedForm.TspSkinMemo.texts()
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
			if self.test_run == 0:
				time.sleep(2)			
			else:
				time.sleep(10)
				server_stop = True
		return server_stop
	
	def __read_inifile(self):
		print("Reading dscontrol.ini:")
		
		config = configparser.ConfigParser()
		config.read("dscontrol.ini")
		
		self.ds_name = config['general']['servername']
		print("* Servername = " + self.ds_name) 
		self.ds_port = config['general']['Port']
		print("* Portnumber = " + self.ds_port)
		self.ds_password = config['general']['Password']
		print("* Password = " + self.ds_password)
		self.ds_admin_password = config['general']['AdminPassword']
		print("* Admin pw = " + self.ds_admin_password)
		self.ds_base_path = config['general']['ServerBasePath']
		print("* Base path = " + self.ds_base_path)
		self.fpl_files_folder = config['general']['FlightPlansBasePath']
		print("* Flightplan folder = " + self.fpl_files_folder)
	
	def find_result_file(self):
		
		for root, dirs, files in os.walk(self.result_folder_path):
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
	else:
		test_run = 0
	
	server = DedicatedServer(test_run)
	
	server.select_random_flightplan()
	server.set_flightplan_params()
	
	server.open_server()
	
	server.sleep_for_start_time()
	
	server.start_server()
	
	server.start_flight()

	server_stop = False
	server_stop = server.messagehandler_loop()

	if server_stop:
		server.stop_server()
		server.close_server()
		server.find_result_file()
		if self.result_file != None:
			shutil.copy(self.result_file,self.fpl_files_folder)
			server.make_result_png()
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

