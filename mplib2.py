import time, queue, subprocess

#################################################################
class Process :
	def __init__(self) :
		self.process = None
		self.order = None

#################################################################
class MakeCmdContext :
	def __init__(self) :
		self.args = []
		self.cmd_args = None
		self.stdin = None
		self.stdout = None
		self.order = None
		self.total_count = 0
		self.on_close = False

	def reset(self) :
		self.cmd_args = None
		del self.args[:]
		if self.stdin is not None : self.stdin.close()
		if self.stdout is not None : self.stdout.close()
		self.stdin = None
		self.stdout = None
		self.order = None
		self.on_close = False

#################################################################
class ProcessManager :
	uinst = None

	def __new__(cls):
		raise NotImplementedError()

	def __init__ (self) :
		raise NotImplementedError()

	def __del__(self):
		print("ProcessManager is destructing, total_count %d" % self.make_cmd_context.total_count)
		self.close()

	@staticmethod
	def create (max_processes, make_cmd) :
		if ProcessManager.uinst is not None :
			raise Exception("ThreadPool can be created only once")

		ProcessManager.uinst = object.__new__(ProcessManager)
		self = ProcessManager.uinst

		self.proc_list = []
		self.order_list = [x for x in range(0, max_processes)]
		self.proc_num = max_processes
		self.make_cmd = make_cmd
		self.make_cmd_context = MakeCmdContext()
		return self

	def _wait_one(self) :
		time.sleep(0.27)
		for xp in self.proc_list :
			if xp.process.poll() is not None :
				self.order_list.append(xp.order)
				self.proc_list.remove(xp)
#				print("Process (%d) terminated" % xp.process.pid)

	def _start_one(self) :
		ctx = self.make_cmd_context
		if ctx.cmd_args is not None :
			xp = Process()
#			print(ctx.cmd_args)
			xp.process = subprocess.Popen(ctx.cmd_args, stdin=ctx.stdin, stdout=ctx.stdout)
			xp.order = self.order_list[0]
			del self.order_list[0]
			self.proc_list.append(xp)
			ctx.reset()
#			print("Process (%d) running" % xp.process.pid)

	def add_tasklet(self, *args) :
		while len(self.proc_list) >= self.proc_num :
			self._wait_one()

		ctx = self.make_cmd_context
		ctx.order = self.order_list[0]
		self.make_cmd(ctx, tuple(x for x in args))
		self._start_one()

	# This must be call before the main process exits.
	def close(self) :
		while len(self.proc_list) > 0 : self._wait_one()

	# Wait for the sub processes to finish their tasklets.
	def wait(self) :
		ctx = self.make_cmd_context
		ctx.on_close = True
		self.make_cmd(ctx, None)
		self._start_one()
		while len(self.proc_list) > 0 : self._wait_one()

#################################################################
