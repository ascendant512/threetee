import logging
import sys
import threading
from subprocess import Popen, PIPE

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

	# Start threads for handling input and output streams
	stdin_thread = threading.Thread(target=in_stream_handler, args=(sys.stdin, process.stdin, 'stdin'))
	stdout_thread = threading.Thread(target=out_stream_handler, args=(process.stdout, sys.stdout, 'stdout'))
	stderr_thread = threading.Thread(target=out_stream_handler, args=(process.stderr, sys.stderr, 'stderr'))

	# Start the threads
	stdin_thread.start()
	stdout_thread.start()
	stderr_thread.start()

	# Wait for the threads to finish
	stdin_thread.join()
	stdout_thread.join()
	stderr_thread.join()

	# Wait for the subprocess to exit and get its exit code
	exit_code = process.wait()
	logging.info(f'Subprocess exited with code {exit_code}')


# Main function
def main():
	start_subprocess()


if __name__ == "__main__":
	main()
