'''
20th june 2018 wednesday
'''

from boto3 import resource
from boto3 import Session

class S3Con:
    """
    parameters
        bucket_name
            name of the bucket in which files will be stored

        key_id
            amazon access-key
        
        secret_key
            amazon secret-access-key
        
        region
            default region
    """

    def __init__(self, bucket_name, key_id, secret_key, region):
        self._session = Session(aws_access_key_id=key_id,
                                aws_secret_access_key=secret_key)
        
        self._bucket = self._session.Bucket(bucket_name)
    

    def _send(self, src_path, remote_path):
        """
        Transfers a resource(file) to the s3-bucket.

        parameters
            src_path
                local path of the resource to be sent

            remote_path
                mapped path of the src_path on the
                remote storage
        """
        pass

    def _delete(self, remote_path):
        """
        Deletes a resource in the s3-bucket.

        parameters
            remote_path
                path of the resource to be deleted on
                the remote storage
        """
        pass

    def _move(self, remote_src_path, remote_dest_path):
        """
        Moves a resource in the s3-bucket.

        parameters
            remote_src_path
                remote path of the resource before it was moved

            remote_dest_path
                remote path of the resource after it was moved
        """
        pass