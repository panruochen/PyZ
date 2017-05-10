# PyZ

A python library

##### threadpool
A ThreadPool class which makes multiple-threading more easier.

ThreadPool.create(num_threads,thread_function)
    Create a thread pool whose contains at most num_threads threads.
	The thread_function is called to execute tasks with arguments passed by add_task().

ThreadPool.add_task(*args...)
	Add a task to ThreadPool. ThreadPool tries find an idle thread to execute it or
	put it to the internal queue and wait.

ThreadPool.wait()
	Wait for all tasks in the queue to be completed.

ThreadPool.close()
	Wait for all tasks in the queue to be completed and then close the pool.
