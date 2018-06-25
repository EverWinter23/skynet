# README

## SKYNET The Main Module

+ Can work with sftp, aws-s3 or any storage service you might want to use, provided that a
  con. class has been supplied. 
+ Uses **polling** to establish connection with the remote storage.
+ Syncs files already present in the folder to be monitored.
+ Init. _thread_watcher to monitor subsequent file system events in that dir.
+ Init. _thread_handler to execute actions recorded in the Q.
+ If the connection is lost at any point during exec, _thread_handler is halted and is only
  restarted when the con. has been re-estd.

## ACTIONS FileSystemEvent Action

Every FileSystemEvent has a corresponding action associated with it, which is enQ'd in the
when that event takes place. There are only 3 types of actions corresponding to all events,
namely --[send], [delete], [move].

    # [send] action, with args src_path
    self._q.put({'action': 'send', 'src_path': event.src_path})
    # [delete]] action, with args src_path
    self._q.put({'action': 'delete', 'src_path': event.src_path})
    # [move] action with args src_path and dest_path
    self._q.put({'action': 'move', 'src_path': event.src_path,
                 'dest_path': event.dest_path})

NOTE: self._q here is an instance of the Q class [UniqueQ] which has beed further explained
below.

## UNIQUEQ Stores Actions

Our Q is an SQLiteDB based Q which makes it fault-tolerant and recoverable. Not only that, one of
the majore reasons that out of all possible SQLiteDB based Qs, this one was selected because of one
very special reason --it only enQ's unique actions, any action which is similar to the one already
in the Q is discarded, mor or that later.

        from persistqueue import UniqueQ as Q
        # NOTE:
        #   auto_commit value depends on what you're trying to achieve
        self._q = Q(path=db_path, auto_commit=True, multithreading=True)
        

 + **Disk Based** Q which ensures that each queued action is backed-up onto the disk,
   in case of crashes or should we decide to pause the process or shut-down the PC.
 + **Thread Safe** Can be simultaneously used by producers, i.e. our watcher and consumers,
   i.e. our handler as it ensures atomicity and consistency.
 + **Recoverable:** Stored actions can be executed after the process restarts from any
   interruption or crash.

## SYNCSNAP Syncs Initial Files

+ Syncs files already present in the folder to be synced by adding all file paths to the Q.
+ It is only called once for each mapping --if a DB corresponding to the Q for that mapping
  exists, then we donot add any actions to the Q.
+ _first_sync method simply picks up all the **file paths** present in that folder and
  adds a 'send' action to the Q.


## WATCHER Monitors Events

+ _thread_watcher keeps on monitoring the dir even when the _thread_handler is stopped.




# LICENSE [![License: AGPL v3](https://img.shields.io/badge/License-AGPL%20v3-blue.svg)](https://www.gnu.org/licenses/agpl-3.0)

Permissions of this strongest copyleft license are conditioned on making available complete
source code of licensed works and modifications, which include larger works using a
licensed work, under the same license. Copyright and license notices must be preserved.
Contributors provide an express grant of patent rights. When a modified version is used to
provide a service over a network, the complete source code of the modified version must be
made available.