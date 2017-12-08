import subprocess
import time
import requests
import threading

global alive
alive = 0

global application_process
application_process = None

global UDID
UDID = None

global timeoutTimer
timeoutTimer = None

#subprocess.Popen(['irecovery', '-m', '-v'], stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=2).stdout.read()

#subprocess.check_output(['irecovery', '-m', '-v'], stderr=subprocess.PIPE)
# write logging funcitons. regular vs fatal.
# change all to check_output

bundleid = 'com.leftyfl1p.saigonautorunner'
wait_period = 5

def reboot_device():
	print("REBOOTING DEVICE")
	# subprocess.Popen(['idevicediagnostics', 'restart'], stdout=subprocess.PIPE, stderr=subprocess.PIPE).wait()
	UDID = subprocess.check_output(['idevice_id', '-l'], stderr=subprocess.PIPE).decode('UTF-8').rstrip()

	if UDID:
		command = "ideviceenterrecovery -d " + UDID
		#subprocess.check_output(command.split(), stderr=subprocess.PIPE)
		subprocess.Popen(command.split(), stdout=subprocess.PIPE, stderr=subprocess.PIPE).wait()

	# not sure why this is for and not while
	status = None	
	for x in range(1,20):
		try:
			status = subprocess.check_output(['irecovery', '-m', '-v'], stderr=subprocess.PIPE).decode('UTF-8').rstrip()
		except Exception as e:
			pass
		if status is not None:
			if "Recovery Mode" in status:
				print("Kicking device out of recovery")
				subprocess.check_output(['irecovery', '-n'], stderr=subprocess.PIPE)
				break

def checkAlive():
	#print("checking alive")
	global alive
	global application_process
	if alive != 1:
		print("Application Hasn't responded, rebooting")
		try:
			application_process.kill()
		except Exception as e:
			pass
		reboot_device()

def application_process_timeout():
	global application_process
	application_process.kill()
	print("Process timed out")

def execute(cmd):
	global alive
	alive = 0
	global application_process 
	application_process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
	threading.Timer(15.0, checkAlive).start()

	global timeoutTimer
	timeoutTimer = threading.Timer(600.0, application_process_timeout)
	timeoutTimer.start()

	for stdout_line in iter(application_process.stdout.readline, ""):
		alive = 1
		yield stdout_line
		
	application_process.stdout.close()
	return_code = application_process.wait()
	if return_code:
		print("Application process ended")
		#global timeoutTimer
		timeoutTimer.cancel()

def wait_for_device_connection():
	print("Waiting for device...")
	#status = subprocess.Popen(['idevice_id', '-l'], stdout=subprocess.PIPE, stderr=subprocess.PIPE).stdout.read()
	shown_password_prompt = False
	while 1:
		local_UDID = subprocess.check_output(['idevice_id', '-l'], stderr=subprocess.PIPE)
		if local_UDID:
			try:
				status = subprocess.check_output(['ideviceinfo', '-k', 'PasswordProtected'], stderr=subprocess.PIPE).decode('UTF-8').rstrip() #rstrip because \n
				if status == 'true':
					if not shown_password_prompt:
						print("[ERROR]: Device is password protected - cannot continue")
					shown_password_prompt = True
				elif status == 'false':
					break
			except Exception as e:
				print(e)

		recovery_status = None
		try:
			recovery_status = subprocess.check_output(['irecovery', '-m', '-v'], stderr=subprocess.PIPE).decode('UTF-8').rstrip()
		except Exception as e:
			pass # device not in recovery
			#print("device not in recovery?")
		
		# add error checking
		if recovery_status is not None:
			if "Recovery Mode" in recovery_status:
				reboot_device()

		time.sleep(1)

	try:
		# local_UDID = subprocess.check_output(['idevice_id', '-l'], stderr=subprocess.PIPE)
		# global UDID
		# if local_UDID != UDID:
		# 	UDID = local_UDID
		device_name     = subprocess.check_output(['ideviceinfo', '-k', 'DeviceName'], stderr=subprocess.PIPE).decode('UTF-8').rstrip() #rstrip because \n
		product_type    = subprocess.check_output(['ideviceinfo', '-k', 'ProductType'], stderr=subprocess.PIPE).decode('UTF-8').rstrip() #rstrip because \n
		hardware_model  = subprocess.check_output(['ideviceinfo', '-k', 'HardwareModel'], stderr=subprocess.PIPE).decode('UTF-8').rstrip() #rstrip because \n
		product_version = subprocess.check_output(['ideviceinfo', '-k', 'ProductVersion'], stderr=subprocess.PIPE).decode('UTF-8').rstrip() #rstrip because \n
		print('[INFO]: Connected to {} ({}, {}) on {}'.format(device_name, product_type, hardware_model, product_version))
	except Exception as e:
		print(e)
	
	global wait_period
	print('[INFO]: Waiting ' + str(wait_period) + ' seconds before continuing...')
	time.sleep(wait_period)


def runApp():
	global bundleid
	print("Opening application " + bundleid)
	for path in execute(['idevicedebug', 'run', bundleid]):
		print(path, end="")
		if "com.leftyfl1p.saigonautorunner.rebootrequested" in path:
			print ("Device requested reboot")
			reboot_device()
		if "com.leftyfl1p.saigonautorunner.trybuttondisabled" in path:
			requests.post("https://api.pushover.net/1/messages.json",
				data={'token': 'ac2op1s7yr9z3n5po4ftak7xzrwr5h',
				'user': 'uev4a6q2sk2uah5yf45uc31ubvhq2o',
				'title': 'Saigon Status Update',
				'message' : 'Try button is disabled'}, verify=True)
		#popen.stdout.close()



def upload_disk_img():
	#check if already mounted
	out = subprocess.check_output(['ideviceimagemounter', '-l'], stderr=subprocess.PIPE)
	if not out:
		print("Uploading developer disk image")
		# need error checking. check for files
		try:
			subprocess.Popen(['ideviceimagemounter', 'DeveloperDiskImage.dmg', 'DeveloperDiskImage.dmg.signature'], stdout=subprocess.PIPE, stderr=subprocess.PIPE).wait()
		except Exception as e:
			pass
		
		time.sleep(1)

while 1:
	wait_for_device_connection()
	upload_disk_img()
	runApp()
	

	


