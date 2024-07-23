# Python 3 server example
import urllib.request
import dns.resolver
import random
import time
import sys
from p_tqdm import p_umap

# Just a little print function that forces the terminal to write immediately
# so we can see what is going on in real-time.
def printf( data ):
    print( data )
    sys.stdout.flush()

if __name__ == "__main__":

    # Strictly, in a 'real' application where this might change, we would re-request
    # this periodically to check we have no worker address updates.
    printf( "Finding our worker addresses..." )
    worker_list = []
    answers = dns.resolver.Resolver().resolve( 'worker', 'A' )
    for server in answers:
        worker_list.append( server )
    
    # Just pause for a moment - this lets our workers all be ready, but also lets you
    # see what is happening on the terminal before we get a ton of text from the jobs
    # running on the workers :)
    printf( "Ready to go :) Waiting 5 seconds before we kick off the requests..." )
    time.sleep( 5 )

    # Change this to run more/fewer jobs!
    job_list = range( 100 )
    max_parallel_jobs = 7

    # This function is where in a 'real' application we would tell a worker what work
    # needed to be done next - perhaps processing the next part of tha corpus? Training
    # your LLM on the next chunk of data? Scraping the next webpage?
    def ask_worker( jobId ):
        printf( f"\nContacting a worker for job {jobId}..." )
        worker_ip = random.choice( worker_list )
        result = urllib.request.urlopen( f"http://{worker_ip}:8080/").read()

    # We're using the excellent p_tqdm and tqdm libraries to render a nice progress bar
    # in the terminal for us, as well as to dispatch our jobs in parallel - handy!
    p_umap(
        ask_worker,
        job_list,
        file=sys.stdout,
        desc="Running jobs: ",
        unit="job",
        ncols=100,
        num_cpus=max_parallel_jobs )

    printf( "Server stopped, all done! Bye!" )