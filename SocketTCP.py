import random
import socket
import slidingWindow as sw
import timerList as tm

HEADER_SIZE = 18
NEW_SERVER_ADDRESS = ('localhost', 8001)

class SocketTCP:
    def __init__(self):
        self.sock=socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        #Default address, port and sequence number
        self.address = 'localhost'
        self.port = 8001
        self.seq = "000"
        #Message length counter
        self.message_length = 0
        #Message buffer
        self.message = ""
        self.whole_message = ""
        self.message_segments = []
        self.window_size = 4
        self.timeout = 1
        self.number_of_sent_segments = 0
        
        

    def set_address(self, address):
        self.address = address

    def set_port(self, port):
        self.port = port

    #bind function will be used by the server to bind the socket to the given address
    def bind(self, address=None):
        self.address = address[0]
        self.port = address[1]
        self.sock.bind(address)

    def listen_socket(self):
        if self.sock is None:
            raise Exception("Socket not initialized")
        self.sock.listen(1)

    def close_socket(self):
        if self.sock is None:
            raise Exception("Socket not initialized")
        self.sock.close()

    def recieve(self, bytes_to_receive):
        if self.sock is None:
            raise Exception("Socket not initialized")
        return self.sock.recvfrom(bytes_to_receive)
    
    def send_to(self, address, message):
        if self.sock is None:
            raise Exception("Socket not initialized")
        self.sock.sendto(message.encode(), address)

                
    #Info sent through TCP class will include TCP-type headers such as "ACK", "SYN", "FIN" or "SEQ"
    #We'll create "parse_segment" function to parse these headers into a data structure
    #We'll also create "create_segment" function to create a segment from a data structure

    #Parse a segment into a data structure

    def parse_segment(self, segment):
        #Get the header
        split_segment = segment.split("|||")
        header = split_segment[0:3]
        #Get the sequence number
        seq = split_segment[3]
        #Get the data
        data = split_segment[4]
        #Return the data structure
        return header, seq, data



    #Create a segment from a data structure
    def create_segment(self, header, seq, data):
        #Create the segment
        #The segment will be a string which contains the header, the sequence number and the data
        #Headers are signaled through binary numbers
        #These is an example of how the function will be used
        #create_segment([1, 0, 0], "001", "Hello")

        #Create the segment
        segment = ""
        #Add the header
        for i in header:
            segment += str(i) + "|||"
        #Add the sequence number
        segment += seq + "|||"
        #Add the data
        segment += data

        #Return the segment
        return segment

    #Connect function will be used by the client to connect to the server to implement the three-way handshake
    #The client will send a SYN segment to the server
    #The server will respond with a SYN-ACK segment
    #The client will respond with an ACK segment
    def connect(self, address):
        print("Connecting to server using three-way handshake")
        #Generate a random sequence number between 0    and 100, using string format to pad the number with zeros
        self.seq = "{:03d}".format(random.randint(0, 100))
        #Create a segment with SYN header and the sequence number
        segment = self.create_segment([1, 0, 0], self.seq, "")
        #Send the segment to the server
        self.send_to(address, segment)
        self.number_of_sent_segments += 1
        #Wait for a response from the server (SYN-ACK segment), with HEADER_SIZE bytes, since the segment will not contain any data
        whole_data, response_address = self.recieve(HEADER_SIZE)
        #Parse the segment
        header, server_seq, data = self.parse_segment(whole_data.decode())
        #If the segment is a SYN-ACK segment, and check if the sequence number is one more than the client sequence number
        if header[0] == "1" and header[1] == "1" and header[2] == "0" and server_seq == "{:03d}".format(int(self.seq) + 1):
            print("Received SYN-ACK segment from server")
            #Increment the sequence number by 1
            self.seq = "{:03d}".format(int(server_seq) + 1)
            #Create a segment with ACK header and the sequence number
            segment = self.create_segment([0, 1, 0], self.seq, "")
            #Send the segment to the server
            self.send_to(response_address, segment)
            self.number_of_sent_segments += 1
            #Return address
            return response_address
        else:
            raise Exception("Connection failed")
    #accept function will be used by the server to accept a connection from the client
    #The server will wait for a SYN segment from the client
    #The server will respond with a SYN-ACK segment
    #The client will respond with an ACK segment
    def accept(self):
        #Wait for a SYN segment from the client, with HEADER_SIZE bytes, since the segment will not contain any data
        whole_data, client_address = self.recieve(HEADER_SIZE)
        #Parse the segment
        header, client_seq, data = self.parse_segment(whole_data.decode())
        #Update the sequence number
        self.seq = client_seq
        #If the segment is a SYN segment, send a SYN-ACK segment
        if header[0] == "1" and header[1] == "0" and header[2] == "0":
            print("Accepting connection from client")
            #Increment the sequence number by 1
            self.seq = "{:03d}".format(int(client_seq) + 1)
            #Create a segment with SYN-ACK header and the sequence number
            segment = self.create_segment([1, 1, 0], self.seq, "")
            #Create a new TCP object to communicate with the client
            new_tcp = SocketTCP()
            #Set the address and port of the new TCP object using SERVER_ADDRESS
            new_tcp.set_address(NEW_SERVER_ADDRESS[0])
            new_tcp.set_port(NEW_SERVER_ADDRESS[1])
            new_tcp.seq = self.seq
            #Bind the socket to the client address
            new_tcp.bind(NEW_SERVER_ADDRESS)
            #Send the segment to the client
            new_tcp.send_to(client_address, segment)
            self.number_of_sent_segments += 1
            #Wait for a response from the client (ACK segment)
            whole_data, new_address = new_tcp.recieve(HEADER_SIZE)
            #Parse the segment
            last_header, new_client_seq, data = self.parse_segment(whole_data.decode())
            #If the segment is an ACK segment, and check if the sequence number is one more than the server sequence number
            #If the sequence number is correct, return the TCP object
            if last_header[0] == "0" and last_header[1] == "1" and last_header[2] == "0" and new_client_seq == "{:03d}".format(int(self.seq) + 1):
                print("ACK segment received from client")
                #Update the sequence number 
                new_tcp.seq = new_client_seq
                return new_tcp, (new_tcp.address, new_tcp.port)
            else:
                raise Exception("Connection failed at last step")
        else:
            raise Exception("Connection failed")
        
    def send(self, message, mode="stop_and_wait"):
        if mode == "stop_and_wait":
            return self.send_using_stop_and_wait(message)
        elif mode == "selective_repeat":
            return self.send_using_selective_repeat(message)
    
    def recv(self, buff_size, mode="stop_and_wait"):
        if mode == "stop_and_wait":
            return self.recv_using_stop_and_wait(buff_size)
        elif mode == "selective_repeat":
            return self.recv_using_selective_repeat(buff_size)
            


    #We'll implement now send_using_selective_repeat function
    #The function will implement timeout and retransmission
    #The function will have a window size of N to manage the sending of segments
    #To do so, we'll first divide the message into segments of maximum size 16 bytes
    #We'll then store the segments in a list
    #First segment sent will inform the receiver of the size of the message
    #This function will mantain a timer for each segment
    #Using tm.TimerList, we'll have to note that not necessarily a timer index will be the same as the ones in data_window
    #We'll have to keep track of the timer index for each segment
    #For this, we'll implement an auxiliary function to manage the timers
    def send_using_selective_repeat(self, message):
        dead_timers = []
        #We'll use a last_ack variable to keep track of the last ack received
        last_ack = None
        #Split the message into segments of size 16 bytes and store them in a list
        data_list = [message[i:i+16] for i in range(0, len(message), 16)]
        #Create a segment with the size of the message
        size_segment = str(len(message))
        #keep track of initial sequence number
        initial_seq = self.seq
        #add size_segment to data_list
        data_list.insert(0, size_segment)
        print(int(self.seq))
        #We'll use a window of size N
        data_window = sw.SlidingWindow(self.window_size, data_list, int(initial_seq))
        #Create a timer list to keep track of the timers using tm.TimerList class
        #tm.TimerList class recieves (timeout, number_of_timers)
        timer_list = tm.TimerList(self.timeout, self.window_size)
        #timer index
        timer_index = 0
        #Send initial window
        for i in range(self.window_size):
            #Get window segment data
            segment_data = data_window.get_data(i)
            #If data is None, break
            if segment_data == None:
                break
            #Get current sequence number
            current_seq = data_window.get_sequence_number(i)
            #Create a segment with the data
            segment = self.create_segment([0, 0, 0], str(current_seq), segment_data)
            #Send the segment
            self.send_to((self.address, int(self.port)), segment)
            self.number_of_sent_segments += 1

            #start timer
            timer_list.start_timer(timer_index)
            #increment timer index
            timer_index += 1
            #increment sequence number
            self.seq = "{:03d}".format(int(self.seq) + 1)

        #Set socket as non-blocking
        self.sock.setblocking(False)

        #Wait for an ACK segment
        while True:
            try:
                timeouts = timer_list.get_timed_out_timers()
                #If there are timeouts, retransmit the segments
                if len(timeouts) > 0:
                    #Retransmit the segments
                    for i in timeouts:
                        #Get window segment data
                        segment_data = data_window.get_data(i)
                        #If data is None, break
                        if segment_data == None:
                            break
                        #Get current sequence number
                        current_seq = data_window.get_sequence_number(i)
                        #Create a segment with the data
                        segment = self.create_segment([0, 0, 0], current_seq, segment_data)
                        #Send the segment
                        self.send_to((self.address, int(self.port)), segment)
                        self.number_of_sent_segments += 1
                        #start timer
                        timer_list.start_timer(i)
                #Recieve the ACK segment
                whole_data, server_address = self.recieve(HEADER_SIZE)
                
                #Parse the segment
                last_header, client_seq, data = self.parse_segment(whole_data.decode())
            except Exception as e:
                print(e)
                continue

            else:
                #If the segment is an ACK segment
                if last_header[0] == "0" and last_header[1] == "1" and last_header[2] == "0":
                    #If the sequence number is the same as the last ack received
                    if client_seq == last_ack:
                        #Do nothing
                        continue
                    #If the sequence number is not the same as the last ack received
                    else:
                        #Update last_ack
                        last_ack = client_seq
                        #get timer index by identifying the client_seq in data_window
                        timer_index = data_window.get_index(int(client_seq))
                        #Replace segment in data_list with 1
                        data_list[int(last_ack - initial_seq)] = 1
                        #Stop the timer
                        timer_list.stop_timer(int(timer_index))
                        #Add the timer to dead_timers
                        dead_timers.append(int(timer_index))
                        #Check if window can be slided
                        #get steps to move
                        steps_to_move = self.steps_to_move_selective_repeat(data_window, data)
                        wnd_index = self.window_size - 1
                        for k in range(1, steps_to_move + 1):
                            data_window.move_window(1)
                            current_data = data_window.get_data(wnd_index)
                            # si hay algo por mandar, lo mando
                            if current_data is not None:
                                #Get current sequence number
                                current_seq = data_window.get_sequence_number(wnd_index)
                                #Create a segment with the data
                                segment = self.create_segment([0, 0, 0], current_seq, current_data)
                                #Send the segment
                                self.send_to(server_address, segment)
                                self.number_of_sent_segments += 1
                                #start timer from dead_timers
                                timer_list.start_timer(dead_timers[0])
                                #remove timer from dead_timers
                                dead_timers.pop(0)
                        #Check if all segments have been sent from data_list
                        if data_list.count(1) == len(data_list):
                            print("Number of sent segments: ", self.number_of_sent_segments)
                            #Reset number of sent segments
                            self.number_of_sent_segments = 0
                            return
                        
                        
    #Create proper recv_using_selective_repeat function
    def recv_using_selective_repeat(self, buff_size):
        #Deactivate timeout
        self.sock.settimeout(None)
        #expected sequence number
        expected_seq = self.seq
        #We create a sliding window of size N
        #Create a dummy list to keep track of the data
        data_list = [None] * self.window_size
        recieving_window = sw.SlidingWindow(self.window_size, data_list, int(expected_seq))
        #Recieve the first segment containing the size of the message
        whole_data, server_address = self.recieve(HEADER_SIZE)
        #Parse the segment
        last_header, client_seq, data = self.parse_segment(whole_data.decode())
        #Get the size of the message
        message_size = int(data)
        #Send an ACK segment
        segment = self.create_segment([0, 1, 0], self.seq, "ACK")
        self.send_to(server_address, segment)
        self.number_of_sent_segments += 1
        #Increment sequence number
        self.seq = "{:03d}".format(int(self.seq) + 1)
        #Recieve the rest of the segments
        while True:
            #Recieve the segment
            whole_data, server_address = self.recieve(HEADER_SIZE + 16)
            #Parse the segment
            last_header, client_seq, data = self.parse_segment(whole_data.decode())
            #Iterate through the recieving window to find the correct index
            for i in range(0, self.window_size):
                #If the sequence number is the same as the expected sequence number
                if client_seq == expected_seq:
                    #If the data is not None, add it to the recieving window using put_data
                    if data != None:
                        recieving_window.put_data(data, client_seq, i)
                    #Send an ACK segment
                    segment = self.create_segment([0, 1, 0], self.seq, "ACK")
                    self.send_to(server_address, segment)
                    self.number_of_sent_segments += 1
                    #Increment sequence number
                    self.seq = "{:03d}".format(int(self.seq) + 1)
                    #Increment expected sequence number
                    expected_seq = "{:03d}".format(int(expected_seq) + 1)
                    #Break the loop
                    break
                #If the sequence number is not the same as the expected sequence number
                else:
                    #Send an ACK segment
                    segment = self.create_segment([0, 1, 0], self.seq, "ACK")
                    self.send_to(server_address, segment)
                    self.number_of_sent_segments += 1
                    #Increment sequence number
                    self.seq = "{:03d}".format(int(self.seq) + 1)
                    #Break the loop
                    break
            
        


    def steps_to_move_selective_repeat(self, sender_window, seq) -> int:
        """Determina la cantidad de pasos que la ventana deslizante sender_window se debe mover dado que se recibio el segmento receibed_segment."""
        # si el segmento que llego es el que se esperaba, se mueve la ventana hasta el siguiente segmento que se esperaba
        if sender_window.get_sequence_number(0) == seq:
            return 1
        # si no, se busca el segmento que se esperaba
        else:
            for i in range(1, sender_window.get_size()):
                if sender_window.get_sequence_number(i) == seq:
                    return i + 1
        # si no se encuentra, no se mueve la ventana
        return 0
    
    
    #We'll create a send(message) function which will be used to send a message to the other side
    #The function will implement timeout and retransmission
    #The function will first send the receiver the size of the message
    #Then it will send the message itself
    #It will split the meesage into segments of maximum size 16 bytes
    #It will send each segment to the receiver
    #It will wait for an ACK segment from the receiver
    #If the ACK segment is not received within a timeout, it will retransmit the segment
    #If the ACK segment is received, it will send the next segment
    def send_using_stop_and_wait(self, message):

        print("Sending message: ", message)
        #Send the size of the message to the receiver
        #The size of the message will be sent using len function
        #Begin timeout
        self.sock.settimeout(5)
        #Send the size of the message to the receiver in a while loop
        while True:
            try:
                #Send the size of the message to the receiver
                #Create segment with size of message
                segment = self.create_segment([0, 0, 0], self.seq, str(len(message)))
                #Send the segment to the receiver
                self.send_to((self.address, int(self.port)), segment)
                self.number_of_sent_segments += 1
                #Wait for an ACK segment from the receiver
                whole_data, server_address = self.recieve(HEADER_SIZE)
                #Parse the segment
                header, seq, data = self.parse_segment(whole_data.decode())
                #Check if the segment is an ACK segment and if the sequence number is incremented by 1
                if header[0] == "0" and header[1] == "1" and header[2] == "0" and seq == "{:03d}".format(int(self.seq) + 1):
                    print("ACK segment received from server in response to size of message")
                    #Increment the sequence number by 1
                    self.seq = "{:03d}".format(int(seq) + 1)
                    break
            except socket.timeout:
                print("Timeout occured, resending size of message")
                #reset timeout
                self.sock.settimeout(5)
        #Send the message to the receiver
        #Split the message into segments of maximum size 16 bytes
        segments = [message[i:i+16] for i in range(0, len(message), 16)]
        #Send each segment to the receiver in a while loop
        for segment in segments:
            while True:
                try:
                    #Create a segment with no headers and the sequence number
                    segment = self.create_segment([0, 0, 0], self.seq, segment)
                    #Send the segment to the receiver
                    self.send_to((self.address, int(self.port)), segment)
                    self.number_of_sent_segments += 1
                    #Wait for an ACK segment from the receiver
                    whole_data, address = self.recieve(HEADER_SIZE)
                    #Parse the segment
                    header, seq, data = self.parse_segment(whole_data.decode())
                    #Check if the segment is an ACK segment and if the sequence number is incremented by 1
                    if header[0] == "0" and header[1] == "1" and header[2] == "0" and seq == "{:03d}".format(int(self.seq) + 1):
                        print("ACK segment received from server in response to message segment")
                        #Increment the sequence number by 1
                        self.seq = "{:03d}".format(int(seq) + 1)
                        break
                except socket.timeout:
                    print("Timeout occured, resending segment")
                    #reset timeout
                    self.sock.settimeout(5)
        #End timeout
        self.sock.settimeout(None)
        #Return
        print("Number of sent segments: ", self.number_of_sent_segments)
        #Reset number of sent segments
        self.number_of_sent_segments = 0
        return


    #We'll create a recv(size) function which will be used to receive a message from the other side
    def recv_using_stop_and_wait(self, buff_size):
        # si tenia un timeout activo en el objeto, lo desactivo
        self.sock.settimeout(None)
        #If self.message_length is 0, then we'll receive the size of the message
        if self.message_length == 0:
            #Receive the size of the message from the sender
            #No timeout is needed here
            whole_data, client_address = self.recieve(24)
            #Parse the segment
            header, seq, data = self.parse_segment(whole_data.decode())
            #Get the size of the message 
            self.message_length = int(data)
            self.message = ""
            #Send an ACK segment to the sender
            #Increment the sequence number by 1
            self.seq = "{:03d}".format(int(seq) + 1)
            #Create an ACK segment
            ack_segment = self.create_segment([0, 1, 0], self.seq, "")
            #Send the ACK segment to the sender
            self.send_to(client_address, ack_segment)
            self.number_of_sent_segments += 1
        #Receive the message from the sender
        #Begin timeout
        self.sock.settimeout(5)
        while len(self.whole_message) < self.message_length:
            try:
                #Receive a segment from the sender
                whole_data, client_address = self.recieve(1024)
                #Parse the segment
                header, seq, data = self.parse_segment(whole_data.decode())
                #Check if the segment is a data segment and if the sequence number is one more than the previous sequence number
                if header[0] == "0" and header[1] == "0" and header[2] == "0" and seq == "{:03d}".format(int(self.seq) + 1):
                    print("Data segment received from server")
                    #Increment the sequence number by 1
                    self.seq = "{:03d}".format(int(seq) + 1)
                    #Append the data to the message
                    self.whole_message += data
                    #Send an ACK segment to the sender
                    #Create an ACK segment
                    ack_segment = self.create_segment([0, 1, 0], self.seq, "")
                    #Send the ACK segment to the sender
                    self.send_to(client_address, ack_segment)
                    self.number_of_sent_segments += 1
                else:
                    raise Exception("Connection failed")
                #Divide the message into segments of buff_size
                self.message_segments = [self.whole_message[i:i+buff_size] for i in range(0, len(self.whole_message), buff_size)]

            except socket.timeout:
                print("Timeout occured, resending")
                #reset timeout
                self.sock.settimeout(5)
        #If we have received the whole message, we can now return the message
        #We're going to assign the message to a variable called "message"
        #Message will be the first element of message_segments
        #We'll also remove the message from message_segments
        #We're going to repeat this process until message_segments is empty
        self.message = self.message_segments[0]
        self.message_segments.pop(0)

        if len(self.message_segments) == 0:
            self.whole_message = ""
            self.message_length = 0

        #End timeout
        self.sock.settimeout(None)
        #Return the message
        return self.message

    #Now we'll implement end of connection
    #We'll create a close() function which will be used to end the connection
    #close() function will send a FIN segment to the other side
    #Then it will wait for a FIN-ACK segment from the other side
    #Then it will send an ACK segment to the other side
    #Then it will close the socket
    def close(self):
        #Send a FIN segment to the other side
        #Create a FIN segment
        fin_segment = self.create_segment([0, 0, 1], self.seq, "")
        #Send the FIN segment to the other side
        self.send_to((self.address, int(self.port)), fin_segment)
        self.number_of_sent_segments += 1
        #Wait for a FIN-ACK segment from the other side
        #Begin timeout
        self.sock.settimeout(5)
        while True:
            try:
                #Receive a segment from the other side
                whole_data, sever_address = self.recieve(HEADER_SIZE)
                #Parse the segment
                header, seq, data = self.parse_segment(whole_data.decode())
                #Check if the segment is a FIN-ACK segment and if the sequence number is one more than the previous sequence number
                if header[0] == "0" and header[1] == "1" and header[2] == "1" and seq == "{:03d}".format(int(self.seq) + 1):
                    print("FIN-ACK segment received from server")
                    #Increment the sequence number by 1
                    self.seq = "{:03d}".format(int(seq) + 1)
                    break
                else:
                    raise Exception("Connection failed")
            except socket.timeout:
                print("Timeout occured, resending FIN segment")
                #reset timeout
                self.sock.settimeout(5)

        #Send an ACK segment to the other side
        #Create an ACK segment
        ack_segment = self.create_segment([0, 1, 0], self.seq, "")
        #Send the ACK segment to the other side
        self.send_to((self.address, int(self.port)), ack_segment)
        self.number_of_sent_segments += 1
        #End timeout
        self.sock.settimeout(None)
        #Close the socket
        self.sock.close()
        print("Connection closed from client side")
        #Return
        return
    
    #Now we'll implement the server side
    #recv_close() function will be used to receive a FIN segment from the other side
    #Then it will send a FIN-ACK segment to the other side
    #Then it will wait for an ACK segment from the other side
    #Then it will close the socket
    def recv_close(self):
        #Receive a FIN segment from the other side
        #Begin timeout
        self.sock.settimeout(5)
        while True:
            try:
                #Receive a segment from the other side
                whole_data, client_address = self.recieve(HEADER_SIZE)
                #Parse the segment
                header, seq, data = self.parse_segment(whole_data.decode())
                #Check if the segment is a FIN segment and if the sequence number is one more than the previous sequence number
                if header[0] == "0" and header[1] == "0" and header[2] == "1" and seq == "{:03d}".format(int(self.seq) + 1):
                    print("FIN segment received from client")
                    #Increment the sequence number by 1
                    self.seq = "{:03d}".format(int(seq) + 1)
                    break
                else:
                    raise Exception("Connection failed")
            except socket.timeout:
                print("Timeout occured, FIN segment not received")
        #End timeout
        self.sock.settimeout(None)
        #Send a FIN-ACK segment to the other side
        #Create a FIN-ACK segment
        fin_ack_segment = self.create_segment([0, 1, 1], self.seq, "")
        #Send the FIN-ACK segment to the other side
        self.send_to(client_address, fin_ack_segment)
        self.number_of_sent_segments += 1
        #Wait for an ACK segment from the other side
        #Begin timeout
        self.sock.settimeout(5)
        while True:
            try:
                #Receive a segment from the other side
                whole_data, client_address = self.recieve(HEADER_SIZE)
                #Parse the segment
                header, seq, data = self.parse_segment(whole_data.decode())
                #Check if the segment is an ACK segment and if the sequence number is one more than the previous sequence number
                if header[0] == "0" and header[1] == "1" and header[2] == "0" and seq == "{:03d}".format(int(self.seq) + 1):
                    print("ACK segment received from client")
                    #Increment the sequence number by 1
                    self.seq = "{:03d}".format(int(seq) + 1)
                    break
                else:
                    raise Exception("Connection failed")
            except socket.timeout:
                print("Timeout occured, ACK segment not received")
        #End timeout
        self.sock.settimeout(None)
        #Close the socket
        self.sock.close()
        print("Connection closed from server side")
        #Return
        return
    
    #setter for window size
    def set_window_size(self, window_size):
        self.window_size = window_size