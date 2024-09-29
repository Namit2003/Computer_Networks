import socket
import pickle
import random

def server_program():
    host = socket.gethostname()
    port = 5000

    server_socket = socket.socket()
    server_socket.bind((host, port))

    server_socket.listen(2)
    conn, address = server_socket.accept()
    print("Connection from: " + str(address))

    max_seq = 7
    nr_bufs = (max_seq+1)/2
    Events = ["frame_arrival","cksum_error","timeout","network_layer_ready","ack_timeout"]
    no_nak = True
    oldest_frame = max_seq+1
    ack_expected = None
    next_frame_to_send = None
    frame_expected = None
    too_far = None
    out_buf = [-1]*nr_bufs
    in_buf = [-1]*nr_bufs
    arrived = [False]*nr_bufs

    def between(a,b,c):
        p = ((a<=b) and (b<c)) or ((c<a) and (a<=b)) or ((b<c) and (c<a))
        return p

    def send_frame(fk,frame_nr,frame_expected,Buffer):
        s = {}
        s["kind"] = fk
        if fk == "data":
            s["info"] = Buffer[frame_nr % nr_bufs]
        s["seq"] = frame_nr
        s["ack"] = (frame_expected+max_seq)%(max_seq+1)
        if fk == "nak":
            no_nak = False
        data_to_send = pickle.dumps(s)
        conn.sendall(data_to_send)
    nbuffered = None
    if enable_network_layer ==1:

        ack_expected=0
        next_frame_to_send = 0
        frame_expected=0
        too_far = nr_bufs
        nbuffered = 0

        r = {}

        while True:
            event = random.choice(Events)

            if event == "network_layer_ready":
                nbuffered+=1
                with open("NL1.txt", "a+") as f1:
                    out_buf[next_frame_to_send % nr_bufs] = f1.read(1024)
                send_frame("data",next_frame_to_send,frame_expected,out_buf)
                next_frame_to_send+=1

            elif event == "frame_arrival":
                received_data = conn.recv(1024)
                r = pickle.loads(received_data)

                if r["kind"] == "data":
                    if r["seq"] != frame_expected and no_nak:
                        send_frame("nak",0,frame_expected,out_buf)
                    if between(frame_expected,r["seq"],too_far) and arrived[r["seq"] % nr_bufs] == False:
                        arrived[r["seq"] % nr_bufs] = True
                        in_buf[r["seq"] % nr_bufs] = r["info"]
                        while arrived[frame_expected % nr_bufs]:
                            with open("NL1.txt", "a+") as f1:
                                f1.write(in_buf[frame_expected % nr_bufs])
                            no_nak = True
                            arrived[frame_expected % nr_bufs] = False
                            frame_expected+=1
                            too_far+=1
                if r["kind"] == "nak" and between(ack_expected,(r["ack"]+1) % (max_seq+1),next_frame_to_send):
                    send_frame("data",(r["ack"]+1) % (max_seq+1), frame_expected,out_buf)
                while between(ack_expected,r["ack"],next_frame_to_send):
                    nbuffered-=1
                    ack_expected+=1
           
            elif event == "cksum_error":
                if no_nak:
                    send_frame("nak",0,frame_expected,out_buf)
            elif event == "timeout":
                send_frame("data",oldest_frame,frame_expected,out_buf)
            elif event == "ack_timeout":
                send_frame("ack",0,frame_expected,out_buf)
            if nbuffered< nr_bufs:
                enable_network_layer = 1
            else:
                enable_network_layer = 0
    conn.close()

server_program()
