'''
Created on Dec 17, 2012

@author: gauravpatwardhan
'''
import socket
import thread
import os
import re
import time
import platform
import datetime

###########################################################################
# This is the client side implementation of a P2P project.                #
#                                                                         #
# It will initiate connection with the server to gather a list of peers   #
# with the desired RFC. It will then connect to the peer to collect this  #
# RFC.                                                                    #
# Authored by: Nikhil Khatu and Gaurav Patwardhan                         #
# CSC573 Professor: Dr. Khaled Harfoush                                   #
###########################################################################


#set port number for the server to start up on the client
port_num = 7320

##################################################
# initial setting up of existing RFC lists, etc. #
##################################################
global RFC_dict
RFC_dict = {}
RFC_list_org = os.listdir('./RFC1/')
print RFC_list_org

if (os.path.isfile('./RFC1/.DS_Store')):
    RFC_list = RFC_list_org[1:]
else:
    RFC_list = RFC_list_org

#RFC_list = RFC_list_org
print RFC_list

for i in range(0,len(RFC_list)):
    filename = "./RFC1/"+RFC_list[i]
    #print filename
    f = open(filename, 'rb')
    match = re.search(r'\nRFC\s\d+\s.+',f.read())
    #print type(match)
    #if match:
        #print match.group()
    #else:
    #    print 'not matching'
    #    break
    stored_file_rfc_title =  (re.search(r'\s\s+.+\s',match.group())).group().strip().split('  ')[0]
    stored_file_rfc_number=re.search(r'\d+',RFC_list[i]).group()
    RFC_dict[stored_file_rfc_number]=stored_file_rfc_title

f.close()

##################################################
# for the client side implementation of a server #
##################################################
serverSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
serverSocket.bind((socket.gethostbyname(socket.gethostname()),port_num))
serverSocket.listen(10)
print 'The central server is ready.'

#######################################
# the server side code for the client #
#######################################
def server_in_client_spawn_new_connection(connectionSocket):
    print '\n[SERVER]in server_in_client_spawn_new_connection func'
    connectionSocket.send('[SERVER]hello peer. Which file do you want ?')
    rcv_get_file_message = connectionSocket.recv(1024)
    print ''
    #print rcv_get_file_message
    match1 = re.search(r'RFC\s\d+',rcv_get_file_message)
    
    #date
    date = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
    
    #os
    os_name = str(platform.platform())
    
    if match1:
        rfc_number_of_file_to_send = match1.group().split(' ')[1]
        if rfc_number_of_file_to_send in RFC_dict:
            print '[SERVER]file found'
            time.sleep(0.1)
            print '[SERVER]sending file...'
            #enter code to send file across sockets status code '200 OK'
            
            #last modified
            file_last_modified = os.stat('./RFC1/rfc%s.txt'%(rfc_number_of_file_to_send)).st_mtime
            
            #content-length
            file_length = os.stat('./RFC1/rfc%s.txt'%(rfc_number_of_file_to_send)).st_size
            
            #data
            name_of_file_to_send = './RFC1/rfc%s.txt'%(rfc_number_of_file_to_send)
            f = open (name_of_file_to_send,'r')
            data = f.read()
            
            send_file_message = '''P2P-CI/1.0 200 OK
            Date:%s
            OS:%s
            Last-Modified:%s
            Content-Length:%s
            Content-Type: text/text
            %s
            ''' %(date,os_name,file_last_modified,file_length,data)
            f.close()
            
            connectionSocket.send(send_file_message)
            
        else:
            print '[SERVER]file does not exist'
            #send error message '404 Not found'
            send_file_message = '''P2P-CI/1.0 404 Not Found
            Date:%s
            OS:%s
            ''' %(date,os_name)
            
            connectionSocket.send(send_file_message)
            
    else:
        print '[SERVER]sorry. wrong input/bad request'
        # send error message '400 bad request'
        send_file_message = '''P2P-CI/1.0 400 Bad Request
        Date:%s
        OS:%s
        ''' %(date,os_name)
            
        connectionSocket.send(send_file_message)
        
    connectionSocket.close()
    send_file_message = ''

#####################################################################################
# initiates the client connection / client side code to connect to bootstrap server #
# and to connect to other peers                                                     #
#####################################################################################

def client_process():
    #client_process_status_flag = 1
    #print  '\n[CLIENT]client_process_status_flag -->',client_process_status_flag
    flag_connected_to_server = 0
    while True:
        #print  '\n[CLIENT]client_process_status_flag -->',client_process_status_flag
        user_pref_one = raw_input('[CLIENT]Would you like to [1]connect to the server? or [2]end the program?')
        
        if int(user_pref_one) == 1 :
            
            if flag_connected_to_server == 0:
                # initiate connection to central server if not connected already (CHECK THIS CONDITION)
                hostname = ''.join(str(socket.gethostbyname(socket.gethostname())))
                port_num = 7320
                server_location_decision = raw_input('[CLIENT]where is server running ? [1] on your own computer [2] give ip address')
                
                if int(server_location_decision) == 1:
                        clientSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                        clientSocket.connect((socket.gethostbyname(socket.gethostname()),7734))
                        flag_connected_to_server = 1
                
                else: #int(server_location_decision) == 2:
                    server_ip_address = raw_input('[CLIENT]enter VALID server ip address--> ')
                    clientSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    clientSocket.connect((server_ip_address,7734))
                    flag_connected_to_server = 1
                #    print 'asdfasf'
                #else:
                #    print 'Wrong choice.Please run client program again'
                #    break
    
                temp_hello_message = clientSocket.recv(1024)
            
            
            if temp_hello_message  == 'ready_sync':
                print temp_hello_message
                print '[CLIENT]Connected to server'
                
                # Pass RFC listand self information to server via ADD
                keylist = RFC_dict.keys()
                keylist.sort()
                #print len(keylist)
                for key in keylist:
                    send_init_add_message = '''ADD RFC %s P2P-CI/1.0
                    Host: %s
                    Port: %s
                    Title: %s
                    '''%(key,hostname,port_num,RFC_dict[key])    
                    clientSocket.send(send_init_add_message)
                    rcvd_message_for_add = clientSocket.recv(1024)
                    #time.sleep(0.01)
                    #print '[CLIENT]From Server received message for add:', rcvd_message_for_add

                ##### not needed
                # Read server response to make list of peers(w/hostname and port)
                # peers = clientSocket.recv(1024)
                
                # Print options and execute based on reply:
                # print 'Please pick one:'                        
#                 print '[1] List/Get one RFC'
#                 print '[2] List all RFCs'
#                 print '[3] Disconnect from the server'
                user_pref_two = raw_input('[CLIENT]Please pick one:\n[1] List/Get one RFC\n[2] List all RFCs\n[3] Disconnect from server')
                
                if int(user_pref_two) == 1 :
                    user_pref_three = raw_input('[CLIENT]Please enter the number of the RFC you would like: ')
                    # send LOOKUP to server
                    lookup_message = '''LOOKUP RFC %s P2P-CI/1.0
                    Host: %s
                    Port: %s
                    '''%(user_pref_three,hostname,port_num)
                    clientSocket.send(lookup_message)
                    rcvd_message_for_lookup = clientSocket.recv(1024)
                    print '[CLIENT]From Server:', rcvd_message_for_lookup
                    enter= raw_input('[CLIENT]press enter: ')
                    
                    match_ip = re.search(r'\d+\.\d+\.\d+\.\d+',rcvd_message_for_lookup)
                    if match_ip:
                        peer_ip_address = match_ip.group()
                        print '[CLIENT]RFC available ; peer ip address is --> ',peer_ip_address
                    else:
                        print '[CLIENT]there is an error in the received message from the server [ip address not found]'
                        #client_process_status_flag = 0
                        break
                    
                    
                    match_port = re.search(r'\d\d\d\d',rcvd_message_for_lookup[-6:])
                    if match_port:
                        peer_port_address = match_port.group()
                        print '[CLIENT]RFC available ;  peer port address is --> ',peer_port_address
                    else:
                        print '[CLIENT]there is an error in the received message from the server [port number not found]'
                        #client_process_status_flag = 0
                        break
                        
                    #print  '\n[CLIENT]client_process_status_flag -->',client_process_status_flag
                    user_pref_four = raw_input ('[CLIENT]Do you want to download this RFC from %s? [Y]/[N]'%(peer_ip_address))
                    if user_pref_four  == 'Y' or user_pref_four == 'yes' or user_pref_four == 'Yes' or user_pref_four == 'YES':
                        
                        #download rfc
                        clientServerName = peer_ip_address
                        clientServerPort = int(peer_port_address)
                        clientToClientServerSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                        #print '[CLIENT]just before peer connects to peer-server'
                        clientToClientServerSocket.connect((clientServerName,clientServerPort))
                        #print '[CLIENT]just after peer connects to peer-server'
                        
                        print clientToClientServerSocket.recv(1024)
                #         GET RFC 1234 P2P-CI/1.0
                #         Host: somehost.csc.ncsu.edu
                #         OS: Mac OS 10.4.1
                        send_get_file_message = '''GET RFC %s P2P-CI/1.0
                        Host: %s
                        OS: %s
                        '''%(user_pref_three,socket.gethostbyname(socket.gethostname()),platform.platform())
                        #clientToClientServerSocket.gethostbyname(clientToClientServerSocket.gethostname())
                        print '\n[CLIENT]Sending request for RFC %s..' %(user_pref_three)
                        clientToClientServerSocket.send(send_get_file_message)
                        
                        #recv chi natka
                        total_data=[]
                        while True:
                            data = clientToClientServerSocket.recv(8192)
                            if not data:
                                break
                            total_data.append(data)
                            
                        #print total_data
                        #print type(total_data)
                #','.join(str(x) for x in foo)
                        
                        #check message and give output to client
                        #P2P-CI/1.0 200 OK, 404 not found, 400 bad request
                        #print '[CLIENT]before match3'
                        match3 = re.search (r'(P2P-CI/1.0\s)(\d\d\d)',str(total_data))
                        #print '[CLIENT]after match3'
                        if match3:
                            if int(match3.group(2)) == 200:
                                #remove starting stuff from total_data and then write
                                filename = './RFC1/rfc_temp%s.txt'%(user_pref_three)
                                temp_file_desc = open(filename,'w')
                                temp_file_desc.write(''.join(str(x) for x in total_data))
                                temp_file_desc.close()
                                os.system('tail -n +8 ./RFC1/rfc_temp%s.txt > ./RFC1/tempfile.txt'%(user_pref_three))
                                os.system('mv ./RFC1/tempfile.txt ./RFC1/rfc%s.txt'%(user_pref_three))
                                os.system('rm ./RFC1/rfc_temp%s.txt'%(user_pref_three))
                                #print temp_file_desc
                                #print  '\n[CLIENT]client_process_status_flag -->',client_process_status_flag
                
                            elif int(match3.group(2)) == 404:
                            #elif:
                                print '[CLIENT] ERROR 404 NOT FOUND'
                        
                            elif int(match3.group(2)) == 400:
                            #if 400 tell bad request
                            #else:
                                print '[CLIENT] ERROR 400 BAD REQUEST'
                            
                            else:
                                print '[CLIENT] ERROR BAD REQUEST (corrupted message)'
                            
                        else:
                            print '[CLIENT] ERROR 400 BAD REQUEST (corrupted message)'
                        
                        
                        
                    elif user_pref_four  == 'N' or user_pref_four == 'no' or user_pref_four == 'No' or user_pref_four == 'NO':
                        #print '[CLIENT]quitting the program since you do not want any RFC'
                        pass
                    else:
                        print '[CLIENT] Wrong input. Please try again with [Y]/[N].'
                    
                    
                    send_get_file_message = ''
                    #clientSocket.close()
                    clientToClientServerSocket.close()
                
                #get a list of all RFCs
                elif int(user_pref_two) == 2 :
                    send_list_all_message = '''LIST ALL P2P-CI/1.0
                    Host: %s
                    Port: %s
                    '''%(hostname,port_num)
                    clientSocket.send(send_list_all_message)
                    rcvd_list_all_message = clientSocket.recv(8192)
                    print '[CLIENT]From Server:\n', rcvd_list_all_message
                    enter= raw_input('[CLIENT] Press enter to continue: ')
                    
                    #clientSocket.close()
                
                elif int(user_pref_two) == 3 :
                    print '[CLIENT] Closing connection to server.'
                    break
                
                else :
                    print '[CLIENT] Wrong input. Please try again'
                    
            else:
                print '\n[CLIENT] ERROR - Not connected to server --> did not get "ready_sync" message'
                print '\n[CLIENT] ERROR - Check connection between server and client'
                break            
            
            
        
        elif int(user_pref_one) == 2 :
            print '[CLIENT]You have chosen to end the program.'
            #client_process_status_flag = 0
            break
        
        else :
            print '[CLIENT]Invalid Selection / Wrong input. Please try again.'
            #client_process_status_flag = 0
            
    clientSocket.send('close')
    clientSocket.close()
    print '[CLIENT] client side socket closed.'



        
# Start client process
thread.start_new_thread(client_process,())

while True:
    #print "[WHILE]connecting to server connection socket "
    connectionSocket, addr = serverSocket.accept()
    #print "[WHILE]starting thread for server_in_client_spawn_new_connection process "
    thread.start_new_thread(server_in_client_spawn_new_connection,(connectionSocket,))
    #print "[WHILE]started thread for server_in_client_spawn_new_connection process "

serverSocket.close()

    