from __future__ import print_function
import subprocess
import time
import requests
import threading

# USER CONFIGURABLE
application_bundle_identifier = 'com.leftyfl1p.saigonautorunner'
wait_seconds = 10
# END USER CONFIGURABLE

application_alive = False
application_process = timeout_timer = UDID = None
# write logging funcitons. regular vs fatal.

def reboot_device():
	''' Normally we would just do "idevicediagnostics restart", however there seems to be a bug
		(with libimobiledevice??) where if a jailbroken device is booted into an unjailbroken state
		it will not respond to any shutdown or restart commands. The work-around is to tell the device
		to boot into and then back out of recovery mode.
	'''
	print('REBOOTING DEVICE')
	# subprocess.Popen(['idevicediagnostics', 'restart'], stdout=subprocess.PIPE, stderr=subprocess.PIPE).wait()
	UDID = subprocess.check_output(['idevice_id', '-l'], stderr=subprocess.PIPE)

	if UDID:
		status = subprocess.check_output(['ideviceenterrecovery', '-d', UDID.rstrip()], stderr=subprocess.PIPE)

	# Don't trap ourselves in here. May not be the best way to do this.
	for x in xrange(1,20):
		try:
			status = subprocess.check_output(['irecovery', '-m', '-v'], stderr=subprocess.PIPE)
			if 'Recovery Mode' in status:
				print('Kicking device out of recovery')
				subprocess.Popen(['irecovery', '-n'], stdout=subprocess.PIPE, stderr=subprocess.PIPE).wait()
				time.sleep(5)
				break
		except Exception, e:
			pass


def check_application_alive():
	''' Sometimes the process hangs indefinitely at the start with no output.
		This is called with a timer to check against that and kill the process
		if no ouput has been received.
	'''
	global application_alive, application_process
	if not application_alive:
		print("Application hasn't responded, rebooting")
		try:
			application_process.kill()
		except Exception, e:
			pass
		reboot_device()

def timeout_application_process():
	''' Once saigon gets past the initial hang up of triple_fetch
		it will dump a ton of logs which takes the device/computer?
		a long time to process (hours).
	'''
	global application_process
	application_process.kill()
	print('Process timed out')

def run_application():
	global application_alive, application_process, application_bundle_identifier, timeout_timer
	application_alive = False

	print('Opening application ' + application_bundle_identifier)
	application_process = subprocess.Popen(['idevicedebug', 'run', application_bundle_identifier], stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
	
	threading.Timer(15.0, check_application_alive).start()
	timeout_timer = threading.Timer(600.0, timeout_application_process) # Give the process 10 minutes to run
	timeout_timer.start()

	for line in iter(application_process.stdout.readline, ''):
		application_alive = True
		print(line.rstrip())
		if 'com.leftyfl1p.saigonautorunner.rebootrequested' in line:
			print ('Device requested reboot')
			reboot_device()
		if 'com.leftyfl1p.saigonautorunner.trybuttondisabled' in line:
			print('try button disabled. jailbroken?')
		
	application_process.stdout.close()
	return_code = application_process.wait()
	if return_code:
		print('Application process ended')
		timeout_timer.cancel()

def wait_for_device_connection():
	print('Waiting for device...')
	
	shown_password_prompt = False
	while 1:
		local_UDID = subprocess.check_output(['idevice_id', '-l'], stderr=subprocess.PIPE)
		if local_UDID:
			try:
				status = subprocess.check_output(['ideviceinfo', '-k', 'PasswordProtected'], stderr=subprocess.PIPE).rstrip() #rstrip because \n
				if status == 'true':
					if not shown_password_prompt:
						print('[ERROR]: Device is password protected - cannot continue')
					shown_password_prompt = True
				elif status == 'false':
					break
			except Exception, e:
				pass

		recovery_status = None
		try:
			recovery_status = subprocess.check_output(['irecovery', '-m', '-v'], stderr=subprocess.PIPE)
		except Exception, e:
			pass # device not in recovery
		
		# add error checking ???
		if recovery_status is not None:
			if 'Recovery Mode' in recovery_status:
				reboot_device()

		time.sleep(1)

	try:
		device_name     = subprocess.check_output(['ideviceinfo', '-k', 'DeviceName'], stderr=subprocess.PIPE).rstrip() #rstrip because \n
		product_type    = subprocess.check_output(['ideviceinfo', '-k', 'ProductType'], stderr=subprocess.PIPE).rstrip() #rstrip because \n
		hardware_model  = subprocess.check_output(['ideviceinfo', '-k', 'HardwareModel'], stderr=subprocess.PIPE).rstrip() #rstrip because \n
		product_version = subprocess.check_output(['ideviceinfo', '-k', 'ProductVersion'], stderr=subprocess.PIPE).rstrip() #rstrip because \n
		print('[INFO]: Connected to {} ({}, {}) on {}'.format(device_name, product_type, hardware_model, product_version))
	except Exception, e:
		pass
	
	global wait_seconds
	print('[INFO]: Waiting ' + str(wait_seconds) + ' seconds before continuing...')
	time.sleep(wait_seconds)


def upload_disk_img():
	#check if already mounted
	out = subprocess.check_output(['ideviceimagemounter', '-l'], stderr=subprocess.PIPE)
	if not out:
		print('Uploading developer disk image')
		subprocess.Popen(['ideviceimagemounter', 'DeveloperDiskImage.dmg', 'DeveloperDiskImage.dmg.signature'], stdout=subprocess.PIPE, stderr=subprocess.PIPE).wait
		time.sleep(1)

while 1:
	wait_for_device_connection()
	upload_disk_img()
	run_application()
	

	

