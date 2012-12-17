'''
Created on Dec 17, 2012

@author: gauravpatwardhan
'''
import socket
import thread
import re

def bootstrap_server_spawn_new_connection(connectionSocket,):
    input_message = ''
    connectionSocket.send('ready_sync')
    while True:
        
        input_message = connectionSocket.recv(2048)

        if input_message != 'close' and input_message != '':
            method = re.search(r'\A\w+\s',input_message)
            port = re.search(r'Port:\s\d+',input_message)
            host_name_in_tuple = str(connectionSocket.getpeername())
            host_name = ''.join(host_name_in_tuple)

            
            if method:
                #print 'method is-->'+method.group().split(' ')[0]
                #print type(method.group())
                method_name = method.group().split(' ')[0]
            else:
                print 'did not find method'
                break
                        
            if port:
                #print 'port is --> '+port.group().split(' ')[1]
                port_number = port.group().split(' ')[1]
            else:
                print 'did not find port'
                break

       
            if method_name == 'ADD':
                    
                    rfc = re.search(r'RFC\s\d+',input_message)
                    title = re.search(r'Title: \w.+',input_message)
                    
                    if rfc:
                            #print 'rfc is --> '+rfc.group().split(' ')[1]
                            rfc_number = rfc.group().split(' ')[1]
                    else:
                            print 'did not find rfc'
                            break
                    
                    if title:
                            #print 'title is --> '+title.group()[7:]
                            title_name = title.group()[7:]
                    else:
                            print ' did not find title'
                            break
                            
            elif method_name == 'LOOKUP':
            
                rfc = re.search(r'RFC\s\d+',input_message)
                
                if rfc:
                    #print 'rfc is --> '+rfc.group().split(' ')[1]
                    rfc_number = rfc.group().split(' ')[1]
                else:
                    print ' did not find rfc'
                    break
                
            elif method_name == 'LIST':
                    print ''
                    
            else:
                    #print 'going into last else'
                    break
        
            
            if method_name == 'ADD':
                
                add_status = add( host_name,port_number,rfc_number,title_name)
                connectionSocket.send(add_status)
            elif method_name == 'LOOKUP':
                returned_rfc_value = lookup (rfc_number)
                #print 'returned_rfc_value-->',returned_rfc_value
                connectionSocket.send(returned_rfc_value)
                
            elif method_name == 'LIST':
                returned_list = list()
                #print type(returned_list)
                connectionSocket.send(returned_list)
                returned_list = "Error - list is empty"
        
            input_message = ''
            
        else:
            #print 'going out from else loop'
            #print 'input_message-->',input_message
            break

    connectionSocket.close()
    purge(host_name)
    
####################################################################
# function to initialize the parameters before starting the server #
####################################################################
def init_parameters():
    #intialize the dictionaries
    global hostname_port_table
    global rfc_number_rfc_title_hostname
    #global temp

    #hostname_port_table = ['hostname i.e. ip address*','por`t']
    #rfc_number_rfc_title_hostname = ['rfc number*','title of RFC','list of hostname of peers having the RFC']
    hostname_port_table = {}
    rfc_number_rfc_title_hostname = {}
    #temp = {}
    
    #start the socket
    global serverSocket

    serverPort = 7734
    HOST = socket.gethostbyname(socket.gethostname())
    serverSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    serverSocket.bind((HOST,serverPort))
    serverSocket.listen(10)
    print 'The server is ready to receive'

################################################################
#add method for adding respective entries to both the databases#
################################################################
def add( host_name,port_number,rfc_number,title_name):
    #check if peer is already available in the hostname_port_table
    print  host_name,port_number,rfc_number,title_name #for debug
    if host_name in hostname_port_table:
        #print ' client exists in hostname_port_table'
        pass
    else:
        hostname_port_table [host_name]= port_number
        #print 'added client to hostname_port_table'
        #print hostname_port_table
    
    #print 'hostname_port_table -->', hostname_port_table
    #print 'rfc_number_rfc_title_hostname -->', rfc_number_rfc_title_hostname
    
    #check if rfc already available in the rfc_number_rfc_title_hostname
    if rfc_number in rfc_number_rfc_title_hostname:
       
        #if yes, check if host is already listed in there
        if host_name in rfc_number_rfc_title_hostname[rfc_number]:
            # if yes, skip
            #print 'host has the rfc n noted in server'
            #print 'rfc_number_rfc_title_hostname -->', rfc_number_rfc_title_hostname
            pass
        # if no, add
        else:
            rfc_number_rfc_title_hostname[rfc_number].append(host_name)
            #print 'rfc_number_rfc_title_hostname -->', rfc_number_rfc_title_hostname
        
    #if no, add rfc number, title and the host name
    else:
        rfc_number_rfc_title_hostname[rfc_number] = [title_name,host_name]
        #print 'rfc_number_rfc_title_hostname -->', rfc_number_rfc_title_hostname
    
    return "P2P-CI/1.0 200 OK RFC %s %s %s"% (rfc_number,title_name,port_number)


#####################################################
# lookup method for looking up rfcs in the database #
#####################################################
def lookup (rfc_number):
    if rfc_number in rfc_number_rfc_title_hostname:
        return "P2P-CI/1.0 200 OK %s %s %s %s" %(rfc_number,rfc_number_rfc_title_hostname [rfc_number][0],rfc_number_rfc_title_hostname [rfc_number][1],hostname_port_table[rfc_number_rfc_title_hostname [rfc_number][1]])
        #return rfc_number_rfc_title_hostname [rfc_number]
    else:
        return "P2P-CI/1.0 404 NOT FOUND"


############################################
# list method for listing rfcs to a client #
############################################
def list():
    # return the list of all the RFCs available in the rfc_number_rfc_title_hostname table
    if len(rfc_number_rfc_title_hostname) != 0:
        #print 'len(rfc_number_rfc_title_hostname)-->',len(rfc_number_rfc_title_hostname)
        #print 'inside list + if'
        base_string_to_send = "P2P-CI/1.0 200 OK"
        total_string = ""
        for key in rfc_number_rfc_title_hostname:
            
            for i in rfc_number_rfc_title_hostname[key][1:]:
                total_string = total_string + '%s %s %s %s\n' %(key,rfc_number_rfc_title_hostname[key][0],i,hostname_port_table[i])
                #print '\nkey -->:',key,'\nrfc_number_rfc_title_hostname[key][0]-->title-->',rfc_number_rfc_title_hostname[key][0],'i-->',i,'hostname_port_table[i]-->',hostname_port_table[i]
        
        #print "\ntotal_string\n",total_string
        return total_string
    else:
        return "P2P-CI/1.0 400 BAD REQUEST"


################################################
# purge method to clean db after client leaves #
################################################
def purge(host_name):
    #print 'entered purge-->',host_name
    #print 'hostname_port_table-->', hostname_port_table
    #print 'rfc_number_rfc_title_hostname -->', rfc_number_rfc_title_hostname
    
    #purge from hostname_port_table
    if host_name in hostname_port_table:
        del hostname_port_table[host_name]
        #print ''
        #print 'entered purging for hostname_port_table'
        #print 'hostname_port_table-->', hostname_port_table
        #print 'rfc_number_rfc_title_hostname -->', rfc_number_rfc_title_hostname
    
    #for key in temp.keys():
    #    del temp[key]
    #print 'temp-->',temp
    
    #purge from rfc_number_rfc_title_hostname
    #for key in rfc_number_rfc_title_hostname.keys():
    #    temp[key] = rfc_number_rfc_title_hostname[key]

    #print 'temp-->',temp
    
    temp2 = {}
    
    #for every rfc number, check ->
    rfc_number_rfc_title_hostname_keys_list = rfc_number_rfc_title_hostname.keys()
    for key in rfc_number_rfc_title_hostname_keys_list:
        #print ''
        #print 'for loop'
        #print 'temp -->', temp
        
        #if host name exists
        if host_name in rfc_number_rfc_title_hostname[key]:
            #print ''
            #print 'if host name exists'
            #print 'temp -->', temp
            temp2[key]=1

    #print '\ntemp2-->',temp2,'\n'
    for key in temp2:
        rfc_number_rfc_title_hostname[key].remove(host_name)
    
    for key in rfc_number_rfc_title_hostname:
        if len(rfc_number_rfc_title_hostname[key]) == 1:
            temp2[key]=2
    
    for key in temp2:
        if temp2[key] == 2:
            del rfc_number_rfc_title_hostname[key]
    
    #print '\ntemp2-->',temp2,'\n'
    #print 'finished purging for rfc_number_rfc_title_hostname'
    #print 'hostname_port_table-->', hostname_port_table
    #print 'rfc_number_rfc_title_hostname -->', rfc_number_rfc_title_hostname


#####################
# the main function #
#####################
def main():
    
    init_parameters()
    while 1:
        connectionSocket, addr = serverSocket.accept()
        thread.start_new_thread(bootstrap_server_spawn_new_connection, (connectionSocket,))    

if __name__ == "__main__":
    main()
