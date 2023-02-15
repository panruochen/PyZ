#import multiprocessing, os, sys, hashlib
import multiprocessing, time

#################################################################
class Process :
	def __init__(self) :
		self.process = None
		self.name = None

#################################################################
class ProcessManager :
	uinst = None

	def __new__(cls):
		raise NotImplementedError()

	def __init__ (self) :
		raise NotImplementedError()

	def __del__(self):
		print("ProcessManager is destructing")
		self.close()

	@staticmethod
	def create (max_processes, process_main) :
		if ProcessManager.uinst is not None :
			raise Exception("ThreadPool can be created only once")

		ProcessManager.uinst = object.__new__(ProcessManager)
		self = ProcessManager.uinst

		self.proc_list = []
		self.proc_num = max_processes
		self.proc_names = []
		for i in range(0, max_processes) :
			self.proc_names.append("Process-%d" % i)
		self.queue = multiprocessing.Queue(32)
		self.daemon_exiting = multiprocessing.Value('i', False)

		for i in range(0, max_processes) :
			sp = Process()
			self.proc_list.append(sp)
			sp.name = self.proc_names[i]
			sp.process = multiprocessing.Process(target=process_main, args=(self.proc_names[i], self.daemon_exiting, self.queue))
			sp.process.start()
		return self

	def add_tasklet(self, *args) :
		self.queue.put(tuple(x for x in args))

	# This must be call before the main process exits.
	def close(self) :
		self.daemon_exiting.value = True
		for sp in self.proc_list :
			sp.process.join()

	# Wait for the sub processes to finish their tasklets.
	def wait(self) :
		while not self.queue.empty() :
			time.sleep(0.1)

#################################################################
