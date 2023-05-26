import socket
import SocketTCP

HEADER_SIZE = 18
BYTES_TO_RECEIVE = 16
TOTAL_BYTES = HEADER_SIZE + BYTES_TO_RECEIVE
ADDRESS = 'localhost'
INITIAL_PORT = 8000
FULL_ADDRESS = (ADDRESS, INITIAL_PORT)

# SERVER
initial_tcp = SocketTCP.SocketTCP()
initial_tcp.bind(FULL_ADDRESS)
connection_socketTCP, new_address = initial_tcp.accept()

# test 1
buff_size = 16
full_message = connection_socketTCP.recv(buff_size)
print("Test 1 received:", full_message)
if full_message == "Mensje de len=16": print("Test 1: Passed")
else: print("Test 1: Failed")

# test 2
buff_size = 19
full_message = connection_socketTCP.recv(buff_size)
print("Test 2 received:", full_message)
if full_message == "Mensaje de largo 19": print("Test 2: Passed")
else: print("Test 2: Failed")

# test 3
buff_size = 14
message_part_1 = connection_socketTCP.recv(buff_size)
message_part_2 = connection_socketTCP.recv(buff_size)
print("Test 3 received:", message_part_1 + message_part_2)
if (message_part_1 + message_part_2) == "Mensaje de largo 19": print("Test 3: Passed")
else: print("Test 3: Failed")

# test recv_close function
connection_socketTCP.recv_close()