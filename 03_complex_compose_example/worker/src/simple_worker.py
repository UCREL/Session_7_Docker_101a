# Python 3 server example
from http.server import BaseHTTPRequestHandler, HTTPServer
import signal
import time
import sys

# Listen on all interfaces on port 8080
hostName = "0.0.0.0"
serverPort = 8080

# Just a little print function that forces the terminal to write immediately
# so we can see what is going on in real-time.
def printf( data ):
    print( data )
    sys.stdout.flush()

# A basic Python webserver, listens on a TCP port for web requests and writes
# data back to the connection.
class MyServer(BaseHTTPRequestHandler):

    # Handle HTTP GET requests... by doing nothing! We pretend to actually do
    # some work here, but actually just wait half a second so it looks like we
    # have something complicated to do.
    #
    # In your real application this would be where you would retrieve your data
    # and do something useful with it :)
    def do_GET(self):
        printf( "Hello from a worker!" )

        # Pretend to do some complex work :)
        time.sleep( 0.5 )

        # Reply that we're ok
        self.send_response( 200 )
        self.send_header( "Content-type", "text/plain" )
        self.end_headers()
        self.wfile.write( bytes( "ok", "utf-8" ) )
    
    # Quiets down the server a bit...
    # Comment out or delete this function to see the web requests
    def log_message( self, format, *args ):
        return

if __name__ == "__main__":        
    webServer = HTTPServer((hostName, serverPort), MyServer)
    printf( "Worker started http://%s:%s" % (hostName, serverPort) )
    printf( "Waiting for requests..." )

    # This function just handles shutting the worker down if we press Ctrl+C
    def signal_handler( sig, frame ):
        webServer.server_close()
        printf( 'You pressed Ctrl+C!' )
        sys.exit(0)

    signal.signal(signal.SIGINT, signal_handler)

    try:
        # Start listening for web requests forever!
        webServer.serve_forever()
    except KeyboardInterrupt:
        pass

    # If we somehow get here, we need to close down the server and stop... probably
    # either a crash, or we were shutting down anyway.
    webServer.server_close()

    printf( "Worker stopped." )