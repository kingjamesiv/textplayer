import os
import sys
import signal
import time
from subprocess import PIPE, Popen
from threading import Thread
from Queue import Queue, Empty

# Currently, for games that require several clicks to get start info, it doesn't scrape everything.
# Lost.z5 is one. The first couple commands will not produce the expected output.

# Class Summary: TextPlayer([name of the game file], [boolean for debug flag])
# Methods:	run()
# 			parse_and_execute_command_file([text file containing a list of commands])
# 			execute_command([command string])
#			quit()

class TextPlayer:

	# Initializes the class, sets variables
	def __init__(self, game_filename, debug_flag):
		self.game_loaded_properly = True

		# Verify that specified game file exists, else limit functionality
		if game_filename == None or not os.path.exists('games/' + game_filename):
			self.game_loaded_properly = False
			print "Unrecognized game file or bad path"
			return

		self.game_filename = game_filename
		self.game_log = game_filename + '_log.txt'
		self.debug = debug_flag

	# Runs the game
	def run(self):
		if self.game_loaded_properly == True:

			# Create a link to dfrotz if one doesn't exist
			#if not os.path.exists('dfrotz'):
			#	self.create_frotz_link()

			# Start the game process with both 'standard in' and 'standard out' pipes
			self.game_process = Popen(['./frotz/dfrotz', 'games/' + self.game_filename], stdin=PIPE, stdout=PIPE, bufsize=1)

			# Create Queue object
			self.output_queue = Queue()
			t = Thread(target=self.enqueue_pipe_output, args=(self.game_process.stdout, self.output_queue))

			# Thread dies with the program
			t.daemon = True
			t.start()

			# Grab start info from game.
			start_output = self.get_command_output()
			if 'Press' in start_output or 'press' in start_output or 'Hit' in start_output or 'hit' in start_output:
				start_output += self.execute_command(' \n')
			if 'introduction' in start_output:
				start_output += self.execute_command('no\n') # Parc

			return start_output

	# Sends buffer from output pipe of game to a queue where it can be retrieved later
	def enqueue_pipe_output(self, output, queue):
		for line in iter(output.readline, b''):
		    queue.put(line)
		output.close()

	# Run a bash command and wait until it finishes
	def run_bash(self, command):
		process = Popen(command, shell=True)
		while process.poll() is None:
			time.sleep(0.00001)

	# Parses through a text list of commands (or a single command) and executes them
	def parse_and_execute_command_file(self, input_filename):
		if self.game_loaded_properly == True:
			if (os.path.exists(filename)):
				f = open(filename, 'r')
				commands = f.read()
				f.close()
				if '\n' in commands:
					for command in commands.split('\n'):
						print self.execute_command(command)
				else:
					print self.execute_command(command)

	# Send a command to the game and return the output
	def execute_command(self, command):
		if self.game_loaded_properly == True:
			self.game_process.stdin.write(command + '\n')
			return self.get_command_output()

	# Grab the output from the queue
	def get_command_output(self):
		command_output = ''
		output_continues = True
		while (output_continues):
			# read line without blocking
			try: 
				line = self.output_queue.get(timeout=.1) # or q.get_nowait()
			except Empty:
				#print('output ended')
				output_continues = False
			else: # got line
				command_output += line
		command_output = command_output.replace('\n', ' ').replace('>', ' ')
		while '  ' in command_output:
			command_output = command_output.replace('  ', ' ')

		return command_output

	def quit():
		#os.killpg(os.getpgid(self.game_process.pid), signal.SIGTERM)
		pass

