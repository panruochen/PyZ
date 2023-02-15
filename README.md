# PyZ

A python library collection

##### mplib
The ProcessManager class is designed to make multiproccessing coding easier.

<table>
  <tbody align="left">
    <tr>
      <th>Name</th>
      <th>Arguments</th>
      <th>Descriptions</th>
    </tr>
    <tr>
      <td>create</td>
      <td>num_processes: The number of sub processes to be started.</br>
          process_main: The main entry function of the sub process.</br></td>
	  <td>Create a manager with n processes. The manager can be created only once.</td>
    </tr>
    <tr>
      <td>add_tasklet</td>
      <td>*args: Variable number of arguments. When a tasklet is executed, these arguments could be taken from the queue as a tuple.</br>
	  For example, add_tasklet(a,b,c) will result in a tuple(a,b,c) in the queue.</td>
	  <td>Add a tasklet to the manager</td>
    </tr>
    <tr>
      <td>wait</td>
      <td></td>
	  <td>Wait for all tasklets to be completed</td>
	</tr>
    <tr>
      <td>close</td>
      <td></td>
	  <td>Wait for all tasklets to be completed and then terminate all sub processes.</td>
	</tr>
  </tbody></table>
