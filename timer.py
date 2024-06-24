from threading import Thread
from time import sleep


class Timer():
	def __init__(self, sleep_seconds):
		self.ctr = 0
		self.stopped = True
		self.done = False
		self.sleep_seconds = sleep_seconds
		self.thread = Thread(target=self.t_thread, args=[])

	def start(self):
		self.thread.start()
		self.stopped = False

	def stop(self):
		if self.stopped:
			return

		self.stopped = True
		self.done = True

		if self.thread.is_alive():
			self.thread.join()

	def reset(self):
		self.stop()
		self.ctr = 0
		self.done = False
		self.stopped = True
		self.thread = Thread(target=self.t_thread, args=())

	def get_time(self):
		return self.ctr

	def t_thread(self):
		while not self.done:
			sleep(self.sleep_seconds)
			self.ctr += 1
