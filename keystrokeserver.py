import socketserver
import pickle
import os
import socket
import anomalydetector


class MyTCPHandler(socketserver.BaseRequestHandler):
    """
    The RequestHandler class for our server.

    It is instantiated once per connection to the server, and must
    override the handle() method to implement communication to the
    client.
    """

    def handle(self):
        # self.request is the TCP socket connected to the client
        self.data = self.request.recv(1024).strip()
        print("{} wrote:".format(self.client_address[0]))
        received_obj=pickle.loads(self.data)
        print(received_obj['user'])
        userFilePath =  (os.path.join(os.path.dirname(os.path.abspath(__file__)), "accounts", received_obj['user'] + '_' + 'NN'+'.dat'))
        #print(userFilePath)
        try:
            ad=pickle.load(open(userFilePath,"rb"))
        except BaseException as e:
            print("error threw a {}".format(type(e).__name__))
            raise # Reraise the exception
            send_obj = (True, 0, 0)
            self.request.sendall(pickle.dumps(send_obj))

            return

        predict, dist, tresh = ad.predict(received_obj['data'])

        self.request.sendall(pickle.dumps((predict, dist, tresh)))

if __name__ == "__main__":
    HOST, PORT = '', 9999
    #HOST, PORT = socket.gethostname(), 9999
    # Create the server, binding to localhost on port 9999
    server = socketserver.TCPServer((HOST, PORT), MyTCPHandler)
    print("Server started at {}".format(HOST))
    # Activate the server; this will keep running until you
    # interrupt the program with Ctrl-C
    server.serve_forever()
