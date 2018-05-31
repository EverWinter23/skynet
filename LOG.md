SKYNET

## Setting up SSH server
Before using SFTP protocol, we need to setup the SFTP server using SSH.

**Linux**

By default Linux has `ssh` pre-installed for outgoing connections, but it
does not have `ssh-server` for incoming connections.

    sudo apt install openssh-server
`ssh-server` by default runs on port 22.

**Windows**

Detailed setup for windows will be provided later.

## Establishing connection with remote SFTP server

Using the [pysftp](http://pysftp.readthedocs.io/en/release_0.2.9/) library 
(soft wrapper around paramiko lib) for establishing connection with the SFTP 
server. 

In this module we have used a wrapper around pysftp, so that even if the next
update was to break the sftpconn.py module, the whole unit won't be affected.

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


**With SSH keys**

Detailed setup for SSH keys will be provided later.