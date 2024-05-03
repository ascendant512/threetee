import logging
import sys
import threading
from subprocess import Popen, PIPE
from concurrent.futures import ThreadPoolExecutor

# Set up logging
logging.basicConfig(filename='stream_log.txt', level=logging.INFO)


# Function to handle reading from a stream and writing to another
def in_stream_handler(src_stream, dst_stream, name):
	while True:
		data = src_stream.readline()

		if not data:
			dst_stream.close()
			break
		dst_stream.write(data.encode())
		dst_stream.flush()  # Flush to ensure data is written immediately
		logging.info(f'{name}: {data.rstrip()}')


# Function to handle reading from a stream and writing to another
def out_stream_handler(src_stream, dst_stream, name):
	while True:
		data = src_stream.readline()

		if not data:
			dst_stream.close()
			break
		dst_stream.write(data.decode())
		dst_stream.flush()  # Flush to ensure data is written immediately
		logging.info(f'{name}: {data.decode().rstrip()}')


# Function to start the subprocess and handle its streams
def start_subprocess():
	# Start the subprocess
	process = Popen(['/bin/cat'], stdin=PIPE, stdout=PIPE, stderr=PIPE, bufsize=0)

	with ThreadPoolExecutor(3, "io") as pool:
		pool.submit(in_stream_handler, sys.stdin, process.stdin, 'stdin')
		pool.submit(out_stream_handler, process.stdout, sys.stdout, 'stdout')
		pool.submit(out_stream_handler, process.stderr, sys.stderr, 'stderr')

	# Wait for the subprocess to exit and get its exit code
	exit_code = process.wait()
	logging.info(f'Subprocess exited with code {exit_code}')
	return exit_code


if __name__ == "__main__":
	sys.exit(start_subprocess())
