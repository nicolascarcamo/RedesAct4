import socket
import sys 
import SocketTCP

HEADER_SIZE = 18
BYTES_TO_RECEIVE = 16
TOTAL_BYTES = HEADER_SIZE + BYTES_TO_RECEIVE

SERVER_ADDRESS = ('localhost', 8000)
NEW_SERVER_ADDRESS = (sys.argv[1], int(sys.argv[2]))



# CLIENT
client_socketTCP = SocketTCP.SocketTCP()
client_socketTCP.connect(SERVER_ADDRESS)
# test 1
message = "Mensje de len=16"
client_socketTCP.send(message)
# test 2
message = "Mensaje de largo 19"
client_socketTCP.send(message)
# test 3
message = "Mensaje de largo 19"
client_socketTCP.send(message)

# test close function
client_socketTCP.close()