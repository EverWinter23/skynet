'''
wednesday 6th june 2018
'''
# just for consolidating info about config together
# helps in writing comments to the config file TOO.

warning = """
WARNING: We're assuming that the user knows what he's doing,\n\
and thus there are no IO checks for empty/wrong inputs.
"""
server_config = """
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

sync_msg = """
# ================= Sync Configuration =================')
# Trailing slashes are optional.
# The local path specified here should be relative to the top lvl dir.
# Please see LOG.md for further details on configuration settings.
"""

local_root_msg = """
# Path of the top level dir location on the local machine.
# Should be an absolute path, relative paths may lead to errors.
# Tilde notation is acceptable."""

remote_root_msg = """
# Top level directory location on the remote server.
# Should be an absolute path -- without tilde notation.
# Should start with leading slashes.
# Should use UNIX-style forward slashes, since the remote server
# will be accessed via SFTP."""

ignore_msg = """
# Files matching these patterns will be not be uploaded to the server.
# Temporary files --swap files should be ignored.
# Example input> *.swp *.tmp
# WARNING-------------^-PLEASE separate multiple entries with a single space."""

path_msg = """
# The following paths should not contain leading slashes.
# local_dir should be located relative to the local_root path.
# remote_dir should be located relative to the remote_root path.
"""

end_msg = """
NOTE: If you have made any mistake during the configuration,
      you can edit this file or use the cli to generate a new one for you."""