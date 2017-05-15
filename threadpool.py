#!/usr/bin/env python

import threading, Queue

# Global control data shared between ThreadPool and WorkThread objects
class _GlobalThreadControl(object) :
    inst = None

    def __new__(cls):
        return object.__new__(cls)

    def __init__ (self) :
        raise NotImplementedError()

    # Create a unique instance of the class
    @staticmethod
    def create(max_threads):
        _GlobalThreadControl.inst = _GlobalThreadControl.__new__(_GlobalThreadControl)
        self = _GlobalThreadControl.inst
        self.running = True
        self.max_threads = max_threads
        self.idle = threading.Event()
        self.tasks_lock = threading.Lock()
        self.tasks = Queue.Queue()
        self.threads_lock = threading.Lock()
        self.busy_threads  = set()
        self.idle_threads  = []
        return self

    # Verification function for debugging
    @staticmethod
    def checkpoint() :
        self = _GlobalThreadControl.inst
        if len(self.busy_threads) + len(self.idle_threads) != self.max_threads :
            raise Exception("busy_threads %u, idle_threads %u" % (len(self.busy_threads),len(self.idle_threads)))

#################################################################

class _WorkerThread (threading.Thread):
#---------------------------------------------------------------#
    def __init__(self, thread_function, threadID, name, gtc):
        threading.Thread.__init__(self)
        self.thread_function = thread_function
        self.threadID   = threadID
        self.name  = name
        self.gtc   = gtc
        self.active = threading.Event()
        self.debug  = False

#---------------------------------------------------------------#
    def run(self):
        while self.active.wait():
            self.active.clear()
            while True :
                args = None
                self.gtc.tasks_lock.acquire()
                if not self.gtc.tasks.empty() :
                    args = self.gtc.tasks.get()
                self.gtc.tasks_lock.release()
                if args is None:
                    break
                status = self.thread_function(args)

            self.gtc.threads_lock.acquire()
            self.gtc.busy_threads.remove(self)
            self.gtc.idle_threads.append(self)
            self.gtc.threads_lock.release()

            if not self.gtc.running:
                return
            self.gtc.idle.set()

#################################################################

class ThreadPool(object):
    inst = None

    def __new__(cls):
        return object.__new__(cls)

    def __init__ (self) :
        raise NotImplementedError()

    @staticmethod
    def create (max_threads, thread_function) :
        if ThreadPool.inst is not None :
            raise Exception("ThreadPool can be created only once")

        ThreadPool.inst = ThreadPool.__new__(ThreadPool)
        self = ThreadPool.inst
        self.gtc = _GlobalThreadControl.create(max_threads)
        for i in range(1,1+max_threads) :
            t = _WorkerThread(thread_function, i, "Thread-%d" % i, self.gtc)
            t.start()
            self.gtc.threads_lock.acquire()
            self.gtc.idle_threads.append(t)
            self.gtc.threads_lock.release()
        return self
#---------------------------------------------------------------#
    def __queue_cmd(self, icmd):
        self.gtc.tasks_lock.acquire()
        self.gtc.tasks.put(icmd)
        self.gtc.tasks_lock.release()

    def __awake_all(self) :
        threads = []
        n = self.gtc.tasks.qsize()

        self.gtc.threads_lock.acquire()
        while n > 0 and len(self.gtc.idle_threads) > 0:
            t = self.gtc.idle_threads.pop(0)
            self.gtc.busy_threads.add(t)
            threads.append(t)
            n -= 1
        self.gtc.threads_lock.release()

        for t in threads:
            t.active.set()

    # Add a task to the pool. The task will be executed while there is at least one available work thread.
    def add_task(self, *args) :
        icmd = tuple(x for x in args)
        self.__queue_cmd(icmd)
        self.__awake_all()

    # Wait all worker thread finished and then sleep.
    def wait(self):
        while True :
            self.gtc.tasks_lock.acquire()
            cont = not self.gtc.tasks.empty()
            self.gtc.tasks_lock.release()
            if not cont :
                break
            self.__awake_all()
            self.gtc.idle.wait()
        while len(self.gtc.busy_threads) > 0 :
            self.gtc.idle.wait()

    # Wait all worker thread finished and then close the pool.
    def close(self) :
        threads = []
        self.gtc.running = False

        self.gtc.threads_lock.acquire()
        for t in self.gtc.busy_threads :
            threads.append(t)
        while len(self.gtc.idle_threads) > 0 :
            t = self.gtc.idle_threads.pop(0)
            self.gtc.busy_threads.add(t)
            threads.append(t)
        self.gtc.threads_lock.release()

        for t in threads :
            t.active.set()
            t.join()

