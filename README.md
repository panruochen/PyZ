# PyZ

A python library

##### threadpool
A ThreadPool class which makes multiple-threading more easier.

<table>
  <tbody align="left">
    <tr>
      <th>Name</th>
      <th>Arguments</th>
      <th>Descriptions</th>
    </tr>
    <tr>
      <td>create</td>
      <td>num_threads: The number of threads managed by this pool.</br>
          thread_function: The callback function to execute tasks.</br></td>
	  <td>Create a pool which manages n threads. The pool can be created only once.</td>
    </tr>
    <tr>
      <td>add_task</td>
      <td>*args: Variable number of arguments. When a task is executed, these arguments will be input via a tuple.</br>
	  For example, add_task(a,b,c) will result in thread_function(tuple(a,b,c)).</td>
	  <td>Add a task to the pool</td>
    </tr>
    <tr>
      <td>wait</td>
      <td></td>
	  <td>Wait for all task to be completed</td>
	</tr>
    <tr>
      <td>close</td>
      <td></td>
	  <td>Wait for all tasks to be completed and then close the pool</td>
	</tr>
  </tbody></table>


