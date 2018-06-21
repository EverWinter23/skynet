'''
wednesday 6th june 2018
'''
# just for consolidating info about config together
# helps in writing comments to the config file TOO.

warning = """
WARNING: We're assuming that the user knows what he's doing,\n\
and thus there are no IO checks for empty/wrong inputs.
However, if you're facing any issues, refer to LOG.md. And
if you're still having a tough time, email me.
"""

end_msg = """
NOTE: If you have made any mistake during the configuration,
      you can edit this file using any text-editor or you can
      use the cli to generate a new one for you."""

sftp_config_msg = """
# ================= Sever Configuration =================
"""
host_msg = """# Hostname or IP address of the remote server."""

uid_msg = """
# SSH username for the remote server."""

port_msg = """
# TCP port for the SSH server on the remote machine
# The default port is 22."""

passwd_msg = """
# SSH password for the remote server."""

# S3 config
s3config_msg = """
# ================== S3 Configuration =================="""

bucket_msg = """# Your bucket's name."""

keyid_msg = """
# Now, time for entering your aws credentials. ^_^
# Your amazon access-key."""

secret_msg = """
# Your amazon secret-access-key."""

region_msg = """
# Enter the region. For the example given below, region = us-east-1
# https://s3.console.aws.amazon.com/s3/home?region=us-east-1
#                                                  ^^^^^^^^^"""


sync_msg = """
# ================= Sync Configuration ================='
# Trailing slashes are optional.
# The local path specified here should be relative to the top lvl dir.
# Please see LOG.md for further details on configuration settings."""

complete_sync_msg = """
# Enter boolean value, i.e. True or False [CASE SENSITIVE-- enter as is]
# When True, files deleted in the local folder will also be deleted in the
# remote folder.
# When False, files deleted in the local folder willbe retained in the
# remote folder."""

local_root_msg = """
# Path of the top level dir location on the local machine.
# Should be an absolute path, relative paths may lead to errors.
# Tilde notation is acceptable."""

remote_root_msg = """
# Top level directory location on the remote storage.
# Should be an absolute path --without tilde(~) notation.
# Should start with leading slashes.
# Should use UNIX-style forward slashes, since the remote
# storage will be accessed using UNIX like paths.
# NOTE: Don't get confused for s3, just specify the path of dir
#       to which you want to sync your stuff.
#       Example-> BUCKET_NAME/Work/Stuff [Syncs local dir to 'Stuff']"""

ignore_msg = """
# Files matching these patterns will be not be uploaded to the server.
# Temporary files --swap files should be ignored.
# Example input> *.swp *.tmp
# WARNING-------------^-PLEASE separate multiple entries with a single space."""

path_msg = """
# The following paths should not contain leading slashes.
# local_dir should be located relative to the local_root path.
# remote_dir should be located relative to the remote_root path.
# INFO: Having a problem, go see LOG.md --mapping section, it'll
#       definitely clear any doubts you have about relative mapping.
"""
