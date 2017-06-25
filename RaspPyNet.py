import socket, time, pickle, os, threading
from threading import Thread
from subprocess import check_output

import dot3k.backlight as backlight
import dot3k.lcd as lcd

start_time = time.time()

ips = check_output(['hostname', '--all-ip-addresses'])

bhost = ips.split(' ')[0]
host = ips.split(' ')[0]
senderPort = 8008
receiverPort = 8007

sender_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sender_socket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
sender_socket.bind(('', senderPort))

receiver_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
receiver_socket.bind(('', receiverPort))

serverHost = ''
nodesList = []
isServer = True

def main():
   setBroadCastaAddress()

   thread = Thread(target = listenSomePacket)
   thread.start()
   
   time.sleep(15)

   threadStatusChesker = Thread(target=statusCheker)
   threadStatusChesker.start()

   thread1 = Thread(target=displyaList)
   thread1.start()

   thread2 = Thread(target=decide)
   thread2.start()
   
   thread3 = Thread(target=renewStatus)
   thread3.start()

   thread4 = Thread(target=ledNodes)
   thread4.start()

def ledNodes():

    global nodesList
    #shutdown all LEDs
    for x in range (0,9):
        backlight.set_bar(x,0)
        time.sleep(0.05)

    threading.Timer(5.0, ledNodes).start()

    if len(nodesList) <= 0:
        for x in range (0,9):
            backlight.set_bar(x,100)
    else:
        for x in range(0,len(nodesList)):

            backlight.set_bar(x,255)



def lcdInfo( lcdMessage, line, rgb="" ):

    lcd.set_cursor_position( 0, line )
    lcd.write(lcdMessage)
    if rgb == "red" :
        backlight.rgb(200,0,0)
    if rgb == "green" :
        backlight.rgb(0,200,0)


def statusCheker():
	global nodesList
	threading.Timer(60.0, statusCheker).start()
	for item in nodesList:
		if item[1] < 8:
			nodesList.remove(item)
		else:
			item[1] = 0	

def decide():
    global isServer
    if isServer == True:
        startServer()
    else:
        startClient()

def setBroadCastaAddress():
    global bhost
    s = '.'
    tpmHost = (s.join(host.split('.')[:3])) + '.255'
    bhost = tpmHost.encode('utf-8')

def listenSomePacket():
    global isServer
    print("Defining type of node...")    
    while time.time() - start_time <= 5:				
		data, address = sender_socket.recvfrom(512)		
		if data != None:
			isServer = False

def startServer():
    global nodesList
    nodesList.append([host, 0, "server"])
    print("Starting Server...")
    lcdInfo("Starting Server", 0, "red" )
    
    def checkIp(data):
        tmp = False
        if len(nodesList) <= 0:
            nodesList.append([data.split()[0], 0, data.split()[2]])
            tmp = True
        else:
            for x in nodesList:				
				if data.split()[0] == x[0]:
					tmp = True
					x[1] += 1													
        try:
            if isinstance(pickle.loads(data), list):
                tmp = True
        except:
            pass

        if tmp == False:
            nodesList.append([data.split()[0], 0, data.split()[2]])
        return
             
    def sendData():
		while 1:
			time.sleep(5)
			dataA = pickle.dumps(nodesList)		
			sender_socket.sendto(dataA, (bhost, senderPort))
			
    def receiveData():
		while 1:
			time.sleep(5)			
			data, address = receiver_socket.recvfrom(1024)			
			checkIp(data)						   
    
    def serverStatusCounter():
		while 1:
			time.sleep(5)
			for item in nodesList:
				if item[2] == 'server':
					item[1] += 1
		
    threadReceiver = Thread(target = receiveData)
    threadReceiver.start()
    
    threadSender = Thread(target = sendData)
    threadSender.start()
    
    threadCounter = Thread(target = serverStatusCounter)
    threadCounter.start()

def startClient():
    print("Starting Client...")
    lcdInfo("Starting Client", 0,"green" )
        
    def defineServer():
		global serverHost
		while 1:		
			for item in nodesList:
				#print('arr item: ', item[2], item[2] == 'server')
				if item[2] == 'server':
					serverHost = item[0]
					#print(serverHost)			
			time.sleep(5)							
    
    def receivePackets():
		global nodesList, serverHost
		while 1:
			time.sleep(5)			
			data, address = sender_socket.recvfrom(1024)
			nodesList = pickle.loads(data)
			
    def sendPackets():
		myData = str(host) + " " + str(senderPort) + " " + "client"		
		while 1:
			time.sleep(5)
			try:
				sender_socket.sendto(myData, (serverHost, 8007))
			except:
				pass
				
			
    threadDefineHost = Thread(target = defineServer)	
    threadDefineHost.start()
   
    threadReceivePackets = Thread(target = receivePackets)
    threadReceivePackets.start()
   
    threadSendPackets = Thread(target = sendPackets)
    threadSendPackets.start()
			
def displyaList():
    while 1:
        time.sleep(2)        
        if(len(nodesList) > 0):            
            os.system('cls' if os.name == 'nt' else 'clear')
            #print("ip:		port:")
            for item in nodesList:
                print(str(item[0]) + " " + str(item[1]) + "  " + str(item[2]))
                lcdInfo( str(item[0]) + " " + str(item[1]) + "  " + str(item[2]), 2 )

def renewStatus():
    pass

if __name__ == '__main__':
    main()
