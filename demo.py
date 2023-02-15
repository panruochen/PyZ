#/usr/bin/env python3 -f
import mplib1, mplib2, os, sys, hashlib, time

def info(title):
	print(title)
	print('module name:', __name__)
	print('parent process:', os.getppid())
	print('process id:', os.getpid())

def hash_calc(funcId, fileName) :
	if funcId == 1 :
		method = "md5"
	elif funcId == 2 :
		method = "sha256"

	ho = hashlib.new(method)
	digest = None
	with open(fileName, "rb") as f:
		for bytes in iter(lambda: f.read(4096), b"") :
			ho.update(bytes)
		f.close()
		digest = ho.hexdigest()
	del ho
	return digest

def process_main(name, daemon_exiting, queue):
	fh = open("%s.log" % (name), "w")
	funcId = -1
	while not daemon_exiting.value or not queue.empty() :
#		print("%s: %d %d" % (name, daemon_exiting.value, queue.empty()))
		try :
			funcId, line = queue.get(timeout=0.1)
#			print("%s: get" % (name))
		except:
			line = None
		if line :
			fileName = line
			digest = hash_calc(funcId, fileName)
			print("%s %s" % (digest, fileName), file=fh)
	fh.close()

def make_cmd1(ctx, args) :
	if args is not None :
		funcId, fileName = args
		ctx.args.append(fileName)
		ctx.total_count += 1
	if len(ctx.args) >= 128 or ctx.on_close :
		ctx.args.insert(0, "md5sum")
		ctx.cmd_args = ctx.args
		fileName = "Process-%d.log" % ctx.order
		fh = open(fileName, "a+")
		ctx.stdout = fh

def mplib_demo(version) :
	if version == 1 :
		pm = mplib1.ProcessManager.create(8, process_main)
	else :
		pm = mplib2.ProcessManager.create(8, make_cmd1)
	startTs = time.perf_counter()
	for funcId in (1,) :
		fh = open(sys.argv[1], "r")
		count = 0
		last_count = 0
		last_time = time.perf_counter()
		for line in fh :
			line = line.rstrip('\r\n')
			pm.add_tasklet(funcId, line)
			count += 1
			now = time.perf_counter()
			do_print = False
			if count - last_count >= 1000 :
				last_count = count
				do_print = True
			if now - last_time >= 5 :
				last_time = now
				do_print = True
			if do_print : print("%d: %s" % (count, line))
		fh.close()
		pm.wait()
	pm.close()
	endTs = time.perf_counter()
	print("Totally %d were entries processed in %.3f seconds" % (count, endTs - startTs))

# This demo uses 8 cores to speeding up calculating md5 and sha256 sums of lots of files saved in a list file.
if __name__ == '__main__':
	if len(sys.argv) < 2 :
		print("Usage: ./demo LIST-FILE")
		sys.exit(1)

	version = 1
	if len(sys.argv) > 2 :
		version = int(sys.argv[2])

	mplib_demo(version)
