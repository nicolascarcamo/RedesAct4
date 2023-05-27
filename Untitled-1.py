
        #Send the segments to the receiver
        #We'll use a while loop to send the segments
        #The loop will run until last_ack is equal to the last sequence number, which is the size of the message plus the initial sequence number
        while last_ack != "{:03d}".format(int(self.seq) + len(message)):
            #We'll first check if there are any segments to send
            #If there are, we'll send the segments
            #We'll use the window to send the segments
            #We'll use a for loop to send the segments
            #The loop will run from the first segment in the window to the last segment in the window
            #The loop will run until the last segment in the window is sent
            for i in range(data_window.first, data_window.last + 1):
                #We'll check if the segment has been sent
                #If it has not been sent, we'll send it
                if data_window.sent[i] == False:
                    #We'll create a segment with the header and the sequence number
                    segment = self.create_segment([0, 0, 0], data_window.seq[i], data_window.data[i])
                    #We'll send the segment to the receiver
                    self.send_to(self.address, segment)
                    #We'll start the timer for the segment
                    timer_list.start_timer(i)
                    #We'll set the segment as sent
                    data_window.sent[i] = True
            #We'll check if there are any segments to recieve
            #If there are, we'll recieve the segments
            #We'll use a while loop to recieve the segments
            #The loop will run until the we recieve all N ACK segments
            while True:
                #We'll recieve the segments using a try except block
                try:
                    #We'll recieve the segments
                    whole_data, address = self.recieve(HEADER_SIZE)
                    #We'll parse the segment
                    last_header, new_seq, data = self.parse_segment(whole_data.decode())
                    #We'll check if the segment is an ACK segment
                    #If it is, we'll check if it is the next ACK segment
                    #If it is, we'll update the window
                    if last_header[0] == "0" and last_header[1] == "1" and last_header[2] == "0" and new_seq == "{:03d}".format(int(last_ack) + 1):
                        #We'll stop the timer for the segment
                        timer_list.stop_timer(int(new_seq) - int(self.seq))
                        #We'll update the window
                        data_window.update_window(int(new_seq) - int(self.seq))
                        #We'll update last_ack
                        last_ack = new_seq
                        #We'll break the loop
                        break
                    #If the segment is not an ACK segment, we'll ignore it
                    else:
                        continue
                #If we don't recieve any segments, we'll break the loop
                except:
                    break
