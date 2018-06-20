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

## Monitoring the local dir for changes --wathcer.py

watcher.py module Watches a dir for any changes within that dir for any file 
system event (create, delete, rename, move etc...) and takes appropriate action.

Implemented using the [watchdog](https://pythonhosted.org/watchdog/) library
which has the following two classes for handling any file system events:

**Observer** A thread that schedules watching directories and dispatches
calls to event handlers to take appropriate action.

**Handler** Handles the actual execution of the action taken by ovveriding
methods.

## Handling the file system events --handler.py

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

If a resource (file/dir) is moved inside the local dir which is being monitored, we 
simply mimic the move on the remote SFTP server.

NOTE: But frist we'll make sure that the path leading up to the new destination
of the file, exists, --we'll create parent dirs as needed.

## Syncing local dir with remote dir --skynet.py

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

## Syncing files already present in a folder mapping --syncsnap.py

Prior to this commit->(syncsnap.py: Sync folders based on dir snapshots), skynet did
not have this feature. Now, the resources already present in the dir to be monitored
are also synced to the remote folder, when the main module is executed for the very
first time.

The syncsnap.py module will aslo help in making the main module independent of the
watcher, i.e. we would not need to rely on the watcher to watch for file system 
events.

However, we would still want to use the watcher because is we were to totally rely
on syncsnap.py, we would need to implement polling, or periodic syncing, which defeats
the syncing the purpose.
So the best way to approach this would be to combine the best features of both, using
syncsnap.py when the connection is not present and using the watcher or faster event
dispatch when we do have an internet connection for direct monitoring--although we will
be using the Q, even when we use the watcher. But the main roadblock in implementing
this is backing up the snapshot to the disk. Pickling maybe??

## Working with aws-s3 --awscon.py

The library for uploading and downloading will be [boto3](https://github.com/boto/boto3),
which allows you to write scripts which make use of Amazon-S3's services.


Next, set up credentials (in e.g. ~/.aws/credentials):

    [default]
    aws_access_key_id = YOUR_KEY
    aws_secret_access_key = YOUR_SECRET

Then, set up a default region (in e.g. ~/.aws/config):

    [default]
    region=us-east-1
    
Let's start by listing the bucket names that you can access.

    import boto3
    s3 = boto3.resource('s3')
    # Let's get our bucket
    SKYNET_23 = [bucket.name for bucket in s3.buckets.all()][0]
    SKYNET_23

### Uploading files and preserving the dir structure
This creates a folder named 'hello' with bucket.txt and c.txt as it contents. Kind of like a folder.

    data = open('bucket.txt', 'rb')
    s3.Bucket(SKYNET_23).put_object(Key='hello/bucket.txt', Body=data)
    data = open('c.txt', 'rb')
    s3.Bucket(SKYNET_23).put_object(Key='hello/c.txt', Body=data)

### Downloading a dir with the dir structure
Lists all files/folders within the folder name 'hello'. If you can list them, you can
pretty much figure out the way to download them. Half the part is knowing what to
download.

    bucket = s3.Bucket(SKYNET_23)
    for obj in bucket.objects.filter(Prefix='hello'):
    print('{0}:{1}'.format(bucket.name, obj.key))

# OPTIMIZATIONS

## Optimizing the Q [NOT DONE YET]

As things stand right now, the Q records multiple actions when a single large file
is copied or moved into the dir being monitored/synced, which is redundant, because
we only want one action corresponding to each event.

**watchdog.observers.api.EventQueue** is a thread-safe event 
queue based on a special queue that skips adding the same event (FileSystemEvent) 
multiple times consecutively. Thus avoiding dispatching multiple event handling calls
when multiple identical events are produced quicker than an observer can consume them.

Will have to switch from persistQ to this EventQueue, but backing up onto the disk
is a raodblock, rightnow.

## Squashing actions [NOT DONE YET]

We could really benefit from squashing the actions corresponding to a file into the
most recent one, --here we only execute one action for that file, which might have
multiple actions recorded in the Q.

    Consider the scenario in which multiple actions correspond to the same file, 
    and we do not have an internet connection rendering us unable to execute the
    instructions which have been stored in the Q.

    handler.py Q-> [delete][move][modify][modify][modify][modify][create]
                   ^--This is the HEAD, i.e, the most recent action performed on
                   this file.
    However, watcher records all action, since the creation of that file, making
    all the actions corresponding to each event useless, because ultimately the
    file will be deleted.

We could use dir snapshots --something like storing the folder structure on the disk,
or file, and compare it with the previous snapshot and accordingly enQ instructions
in the Q based on files that were created, modified, deleted during the time when
either the process was not exectuing or the internet conn could not be established. 


# BUGS
All the known bugs have been listed below, with their status.

### Bug #1 [RESOLVED]

How to handle actions which ran into error during their execution?

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

### Bug #2 [RESOLVED]

This bug arises when an action is unable to complete due to some error during its
execution. The way that handler.py handles unsuccessfull actions right now, is that
it simply accepts that some error occured, and proceeds with the execution of the
pending actions. This causes a problem, because when that action is completed
successfully, the change is comitted to the Database --resulting in loss of the action
which could not complete successfully.

However, if we were to keep on executing the same instruction until it executed
successfully we would never get out of a state in which the execution of that action
is simply not possible, here is an example to illustrate that scenario:

Assume that:

  + We do not have internet connection.
  + The sequence of actions to be executed is, [SEND, MOVE] --and these actions
  are to be carried out on the same file.
  + Some other examples include, [MOVE, MOVE], [SEND, DELETE] etc.

When the connection is re-estd., the handler tries to mimic the modification on
the remote server, but the corresponding file does not exist locally because it 
has been moved to some other folder. If were to keep re-executing this action, we
would be unable to make any progress.

**[IMPLEMENTED]** The same solution, mentioned above, fixes this problem. Because if an
action were to run into an error due to connectivity issues --we are unable to commit
the removal of that action from the persistQ and we resume the exectuion of that same
instruction when the connection is re-estd.
Moreover, if we run into a scenario described above, where we try to modify a file, 
which has been moved to different location, it guarantees that we are not stuck in that
state forever --because handler.py keeps proceeds with the execution of the pending
actions.

