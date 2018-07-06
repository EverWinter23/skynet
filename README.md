# README

Work in Progress.

## SKYNET The Main Module

+ Can work with sftp, aws-s3 or any storage service you might want to use, provided that a
  con. class has been supplied.
+ Uses **polling** to establish connection with the remote storage.
+ Syncs files already present in the folder to be monitored.
+ Init. _thread_watcher to monitor subsequent file system events in that dir.
+ Init. _thread_handler to execute actions recorded in the Q.
+ If the connection is lost at any point during exec, _thread_handler is halted and is only
  restarted when the con. has been re-estd.
+ Sends notifications to a hostedDB when an action is enQ'd or an action is completed, using
  which you can remotely monitor actions. Sepearte Django-app in dev, will add the link to
  it when its completed.
+ Supports resumable **multipart uploads**[aws-s3 only], for big files. Even if the transfer
  gets interrupted somehow, or your PC crashes mid-transfer, the upload won't start from the
  beginning.
+ Also sends status updates for partial uploads, so you can monitor the progress of huge
  file uploads from anywhere.
+ For any problems during execution, you can see the **skynet.log** file for debugging and
  figuring out exactly where things went wrong.


### THE CORE

+ **Watcher** A thread that watches dir for FileSystemEvents and records actions
  corresponding to each one in a Q.
+ **Handler** Handles the execution of the actions recorded by dispatching them to the
  **XCon** The connection class, also provides native implementation of the scheduled 
  actions like _send, _delete, _move etc.
+ **Connection** Class which is supplied to **skynet** which is responsible for actual
  interaction with the remote storage and must implement _send, _delete, _move methods.
+ **Notifier** Sends notifications to Heroku-Postgres DB for monitoring progress remotely.
+ **Mapper** Maps a local path to the remote storage.


## INSTALLATION and CONFIGRUATION

The very first thing you need to do is cloning the repository and installing the required
python-libraries. Make sure you're working with **PYTHON 3.6.**

    $ git clone https://github.com/EverWinter23/skynet
    $ cd skynet
    $ pip install -r requirements.txt

Now, that you have installed the required python packages, you'll need to setup **skywatch**,
--the Django-app for monitoring progress remotely. This step's one's optional. If you don't
want to do that you can just remove the Notifier instance param and you'll be good to go.

We'll host this app on Heroku with Heroku-Postgres for our Database and Django for the web
framework.

>NOTE: Will add later.

After you're done with that, now you need to configure your setup. You can do that by using
cli. Navigate to the dir where you cloned the repo and execute the following command. 
Supported services are S3 and SFTP. The cli will guide you through the complete config for
the service you selected. Should you screw the config during this, you can go ahead and edit
the config file using any text editor.  **Refer to README.md, if you get stuck during the 
Sync Configration, because mapping can be tricky.**  Other than that, it's pretty straight
forward.

    $ python main.py --config [SERVICE]

**NOTE:** You can aslo pass empty params, keep on pressing enter when you're done, go to the
place where the config was saved and edit the config there.

All Done? Now, we're ready. Just execute the following command.

    $ python main.py --run-with [SERVICE]
    # If you want to stop it, hit cntrl + c, will add another way to do that later.



## ACTION FileSystemEvent Actions

Every FileSystemEvent has a corresponding action associated with it, which is enQ'd in the Q,
when that event takes place. There are only 3 types of actions for handling all the events,
namely --[send], [delete], [move].

```python
# [send] action, with args src_path
self._q.put({'action': 'send', 'src_path': event.src_path})
# [delete]] action, with args src_path
self._q.put({'action': 'delete', 'src_path': event.src_path})
# [move] action with args src_path and dest_path
self._q.put({'action': 'move', 'src_path': event.src_path,
              'dest_path': event.dest_path})
```
**NOTE:** self._q here is an instance of the Q class [UniqueQ] which has been further
explained below.

## UNIQUEQ Stores Actions

Our Q is an SQLiteDB based Q which makes it fault-tolerant and recoverable. Not only that,
one of the majore reasons that out of all possible SQLiteDB based Qs, this one was selected
because of one very special reason --it does not allow duplicate entries.

```python
from persistqueue import UniqueQ as Q
# NOTE:
#   auto_commit value depends on what you're trying to achieve
self._q = Q(path=db_path, auto_commit=True, multithreading=True)
```     

+ **Disk Based** Q which ensures that each queued action is backed-up onto the disk,
  in case of crashes or should we decide to pause the process or shut-down the PC.
+ **Thread Safe** Can be simultaneously used by producers, i.e. our watcher and consumers,
  i.e. our handler as it ensures atomicity and consistency.
+ **Recoverable** Stores actions onto the disk which makes sure that they can be executed
  after the process restarts from any interruption or crash.
+ Avoids **Producer-Consumer** problem.

## SYNCSNAP Syncs Initial Files

+ Syncs files already present in the folder to be synced by adding all file paths to the Q.
+ It is only called once for each mapping --if a DB corresponding to the Q for that mapping
  exists, then we donot add any actions to the Q.
+ _first_sync method simply picks up all the **file paths** present in that folder and
  adds a 'send' action to the Q.


## WATCHER Monitors Events

+ _thread_watcher keeps on monitoring the dir even when the _thread_handler is stopped, 
  that is, it runs even in case of connection loss b/w the local machine and the remote
  storage.
+ _thread_watcher enQ's an action corresponding to a FileSystemEvent as described below:

    + **Directory Modification**
    The mtime (modification time) of the directory changes only when a file or a 
    subdirectory is added, removed or renamed.
    Modifying the contents of a file within the directory does not change the 
    directory itself, nor does updating the modified times of a file or a subdir.
    Thus, if a dir is modified , no action will be taken. However, if a file is 
    modified, we will send a the whole file, which will be overwritten in the remote 
    dir.

    + **File Modification**
    Resending the whole file is a viable option, because:
        + Images have small sizes.
        + Videos will not be modified - video processing will be done by the processing
          team. 

    + **File Creation**
    Transfer the file.

    + **Dir Creation** No need to take any record any action corresponding to creation of
    a directory, because the dir will be automatically created when we transfer a file
    from within this directory, --as we make sure that the mapped remote_path on the remote
    storage exists. If it does not, we simply create the necessayr parent dirs.

    + **Resource Moved**
    If a resource [file/dir] is moved inside the local dir which is being monitored, we 
    simply mimic the move on the remote SFTP server.
    But first we make sure that the path leading up to the new destination of the resource,
    exists, --if not we create the parent dirs as needed.
    
    + **Resource Deletion**
    If a resource [file/dir] is deleted in the local dir which is being monitored, those
    files will be deleted on the rmote storage only if the complete-sync mode is set to True,
    otherwise the deleted files will be retained on the remote storage.

## HANDLER Schedules Actions

+ Retreives the actions stored in the Q one by one and only commits the changes to the DB, if
  the action is successfull.
+ However, if the execution ran into any error during execution, except for FileNotFoundError,
  _thread_handler is stopped.
+ When the con. is re-estd. again, the _thread_handler recieves a new instance of the **XCon**
  class and it picks up from where it was stopped.

## MAPPER Maps Local Files to Remote Storage

**Example**
Say, we want to sync the folder x to the folder y on our remote storage. Let the alphabets
represent a directory, then we can represent the paths as:

    NOTE: Using -> to represent '/' in Linux and '\\' in Windows
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
                          ^^^^^^^^^^ this part, --forms your local_base

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

## XCON The Connection Class

'X' in **XCon** stands for the type of remote storage, for example SFTPCon, S3Con.

+ Responsible for implementing _send, _move, _delete methods accordingly to the requirements 
  and limitations of the remote storage.
+ Do not handle any exceptions in this class, they'll be taken care of automatically, should
  they arise.
      
Whatever args you need to pass to the constructor, will be passed from the config
file. So, some changes will have to be made in skynet.py.

```python
# template for connection class
class XCon:
  def __init__(self, whatever's required):
    pass
  
  def _send(self, src_path, remote_path):
    pass

  def _delete(self, src_path):
    pass
          
  def _move(self, remote_src_path, remote_dest_path):
    pass
```

+ The following represents a the checklist of cahnges that will need to be made:
  + [x] Add service to --run-with arg, and gen and writing config to config.ini file.
  + [x] A _get_x_con method to skynet.py, register it with _get_connection method.

# LICENSE [![License: AGPL v3](https://img.shields.io/badge/License-AGPL%20v3-blue.svg)](https://www.gnu.org/licenses/agpl-3.0)

Permissions of this strongest copyleft license are conditioned on making available complete
source code of licensed works and modifications, which include larger works using a
licensed work, under the same license. Copyright and license notices must be preserved.
Contributors provide an express grant of patent rights. When a modified version is used to
provide a service over a network, the complete source code of the modified version must be
made available.