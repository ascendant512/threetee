import asyncio
import logging
import sys
import threading
import concurrent.futures
from functools import partial

# Set up logging
logging.basicConfig(filename='stream_log.txt', level=logging.INFO)

async def in_stream_handler(src_stream, dst_stream, name):
	while True:
		data = src_stream.read(1024)

		if not data:
			# dst_stream.close()
			# await dst_stream.wait_closed()
			dst_stream.write_eof()
			dst_stream.close()
			await dst_stream.wait_closed()
			break
		dst_stream.write(data.encode())
		await dst_stream.drain()
		logging.info(f'{name}: {data.rstrip()}')


async def out_stream_handler(src_stream, dst_stream, name):
	while True:
		data = await src_stream.read(1024)

		if not data:
			dst_stream.close()
			break
		if isinstance(data, str):
			dst_stream.write(data)
			logging.info(f'{name}: {data}')
		else:
			dst_stream.write(data.decode())
			logging.info(f'{name}: {data.decode().rstrip()}')

def spacer(func, *args):
	asyncio.run(func(*args))


# Function to start the subprocess and handle its streams
async def start_subprocess():
	loop = asyncio.get_running_loop()
	# Start the subprocess
	process = await asyncio.create_subprocess_exec('/bin/cat',
							   stdin=asyncio.subprocess.PIPE,
							   stdout=asyncio.subprocess.PIPE,
							   stderr=asyncio.subprocess.PIPE)

	# this code is not threaded
	# await asyncio.gather(in_stream_handler(sys.stdin, process.stdin, 'stdin'),
	# 					 out_stream_handler(process.stdout, sys.stdout, 'stdout'),
	# 					 out_stream_handler(process.stderr, sys.stderr, 'stderr'))

	with concurrent.futures.ThreadPoolExecutor() as pool:
		# Future <Future pending> attached to a different loop
		# await loop.run_in_executor(pool, in_stream_handler, sys.stdin, process.stdin, 'stdin')
		# await loop.run_in_executor(pool, out_stream_handler, process.stdout, sys.stdout, 'stdout')
		# await loop.run_in_executor(pool, out_stream_handler, process.stderr, sys.stderr, 'stderr')

		# threads never seem to start
		loop.run_in_executor(pool, spacer, (in_stream_handler, sys.stdin, process.stdin, 'stdin'))
		loop.run_in_executor(pool, spacer, (out_stream_handler, process.stdout, sys.__stdout__, 'stdout'))
		loop.run_in_executor(pool, spacer, (out_stream_handler, process.stderr, sys.stderr, 'stderr'))

	exit_code = await process.wait()
	logging.info(f'Subprocess exited with code {exit_code}')


# Main function
def main():
	asyncio.run(start_subprocess())


if __name__ == "__main__":
	main()
