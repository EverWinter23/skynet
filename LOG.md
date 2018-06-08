SKYNET

## Setting up SSH server
Before using SFTP protocol, we need to setup the SFTP server using SSH.

**Linux**

By default Linux has `ssh` pre-installed for outgoing connections, but it does
not have `ssh-server` for incoming connections.

    sudo apt install openssh-server
`ssh-server` runs on port 22, by default, but support for port forwarding has
also been added because on android devices the SFTP server runs on port 2222.

**Windows**

Detailed setup for windows will be provided later.

## Establishing connection with remote SFTP server

Using the [pysftp](http://pysftp.readthedocs.io/en/release_0.2.9/) library 
(soft wrapper around paramiko lib) for establishing connection with the SFTP 
server. 

In this module we have used a wrapper around pysftp, so that even if the next
update of pysftp was to break the sftpcon.py module, skynet won't be affected.
Changes will only be needed to apply to the sftpcon.py module.

**Without SSH keys**

    # connection options
    cnopts = pysftp.CnOpts()
    cnopts.hostkeys = None
    # NOTE: cnopts.compression is False (by default), assign True to enable it

    # establish connection to the remote SFTP server
    with pysftp.Connection(host='...', username='...', password='...', cnopts=cnopts) as sftp:
        # connection estd. otherwise exception would be thrown
        # download a remote file from the SFTP server
        sftp.get('remote_file_path')
        # upload a local file to the SFTP server
        sftp.put('local_file_path')

## The concept of Mapping

**Example:** Say, we want to sync the folder x to the folder y on the remote SFTP server.

Let alphabets represent a directory, then we can represent the paths as:

    Here,
      local_root = o->l
      remote_root = o->o->r
      local_dir = x
      remote_dir = y

    Remote dir structure: [o->l->y]->...
                          [-------]
                           ^^^^^^^ this part, --forms your remote_base

    Local dir structure: [o->o->r->x]->z->a
                         [----------]
                          ^^^^^^^^^ this part, --forms your local_base

    For tranfering a file in the dir x, we first strip its absolute path
    of its local_base to obtain it's relative path.
    For the sake of this example, let's say we want to transfer the dir a.
    Then the relative path of 'a' to the local base will be: z->a

    After this, we map this relative path to the remote dir by appending
    this relative path to the remote_base.

    After the transfer is complete,
    Remote dir structure: [o->l->y]->z->a
                          [-------]
                           ^^^^^^^ this part, --forms your remote_base
    

**With SSH keys**

Detailed setup for SSH keys will be provided later.

## Monitoring the local dir for changes

watcher.py module Watches a dir for any changes within that dir for any file 
system event (create, delete, rename, move etc...) and takes appropriate action.

Implemented using the [watchdog](https://pythonhosted.org/watchdog/) library
which has the following two classes for handling any file system events:

**Observer** A thread that schedules watching directories and dispatches
calls to event handlers to take appropriate action.

**Handler** Handles the actual execution of the action taken by ovveriding
methods.

## Handling the file system events

**Directory Modification**

The mtime (modification time) of the directory changes only when a file or a 
subdirectory is added, removed or renamed.

Modifying the contents of a file within the directory does not change the 
directory itself, nor does updating the modified times of a file or a subdir.
Thus, if a dir is modified , no action will be taken. However, if a file is 
modified, we will send a the whole file, which will be overwritten in the remote 
dir.

**File Modification**

Sending the whole file is a viable option, because:
+ Images have small sizes.
+ Videos will not be modified - video processing will be done by the processing
    team. 

**Resource Creation**

If a dir is created in the dir being monitored, there is no need to take any 
action for it. It will automatically be created on the remote SFTP server if it 
contains any file during the file transer. 
If a file is created in the local dir, then we'll transfer that file to the
remote dir.

NOTE: But frist we'll make sure that the path leading up to the file, exists,
--we'll create parent dirs as needed.

**Resource Deletion**

If a resource (file/dir) is deleted in the local dir which is being monitored, we 
will only delete that file if it is present on the remote dir only if this complete-sync
mode is on.

complete-sync=True The remote dir will be a true reflection of the local dir.

complete-sync=False The remote dir will retain the files which have been deleted
in the local dir.

**Resource Moved**

If a resource (file/dir) is moved inside the local dir which is being monitored, we simply mimic the move on the remote SFTP server.

NOTE: But frist we'll make sure that the path leading up to the new destination
of the file, exists, --we'll create parent dirs as needed.

## Syncing local dir with remote dir

The following is a list of things that need to be done to done, to set-up complete
syncing.

+ watcher.py should keep monitoring the local dir for file system changes even when 
  the connection to the SFTP server is lost.
+ handler.py should record all actions that need to be taken corresponding to the
  file system events in a Q or a file, so that they can be executed when conn b/w
  the local system and remote SFTP server exists.
+ skynet.py (the main module) should notify some module (which acts b/w watcher.py 
  and skynet.py as a src of comm.) that the conn has been re-estd. and it should
  begin execution of each action stored in the Q/file.
+ skynet.py should be able to recover from conn loss and execute seamlessly. It should
  also preserve the action during which the connection was lost so that it can be
  re-executed.
+ skynet.py should keep on trying to connect to the SFTP server peridoically to
  re-establish the conn.

**NOTE:** The Q(if implemented) will need to be saved somewhere-> if the local PC was
to shut down. The Q will also lead to Poducer-Consumer problem which will need to handled.

## Fault tolerant and recoverable syncing
Will use [persist-queue](https://pypi.org/project/persist-queue/) module as it implements
a file-based queue, and also achieves the main 3 features we desire:

**Disk-based:** Each queued item should be stored in disk in case of any crash.

**Thread-safe:** Can be used by multi-threaded producers and multi-threaded consumers.

**Recoverable:** Items can be read after process restart.

We integrate it with the watcher.py module by enQing the action needed to handle the 
corresponding file system event. 

    # SEND action, with args src_path
    self._q.put({'action': 'send', 'src_path': event.src_path})
    # DELETE action, with args src_path
    self._q.put({'action': 'delete', 'src_path': event.src_path})
    # MOVE action with args src_path and dest_path
    self._q.put({'action': 'move', 'src_path': event.src_path,
                 'dest_path': event.dest_path})

Whilst, the handler.py module checks the Q for any pending actions --which have not
been executed yet. 

**[DISCARDED] EnQing at the End if action unsuccessful**: This approach was discarded
because it introduced bugs. Consider a scenario in which a file was created inside the
dir being monitored and that action failed --due to conn. problems. And another action
was enQ'd to the Q on that same file --let's assume delete action.
If the process was to continue, it would try to delete a file which has not even been
trasnferred to the remote SFTP server. Of course this is only one scenario out of all
possible scenarios.

**[IMPLEMENTED] Commiting only if successful:** This approach guarantees, that any
action which runs into error will not be lost --because we only commit the changes
to the Q when the action is successful.
Another scenario is that the action completes, but it is not commited --due to any
error b/w the line in which the action was completed and the line in which it the 
action was going to be commited. What this means is that the action will be executed
twice, although it may try to delete a file which has already been deleted --we have
a try and catch mechanism for that in place to guard agains that, but this approach
makes sure that the actions are executed inorder. 

        # snippet from the code that makes the above approach possible
        # NOTE:
        #   auto_commit = False in this declaration, this ensures that
        #   when we deQ something from the Q, the change is not committed
        #   until and unless the action is completed.
        self._q = Q(path='skynet_db', auto_commit=False, multithreading=True)

NOTE: handler.py and watcher.py run independent of each other, --as threads.
