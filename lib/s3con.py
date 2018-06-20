'''
20th june 2018 wednesday
'''

import boto3
import os
import logging


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
        self._client = client('s3',
                              aws_access_key_id=key_id,
                              aws_secret_access_key=secret_key)

        self._bucket_name = bucket_name
        self._bucket = resource('s3').Bucket(bucket_name)

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
        with open(src_path, 'rb') as data:
            self.upload_fileobj(data, key=src_path)

        self._client.put_object(Fileobj=src_path,
                                Bucket=self._bucket_name,
                                Key=remote_path)

    def _delete(self, remote_path):
        """
        Deletes the resource specified by the remote path
        in the s3-bucket.

        parameters
            remote_path
                path of the resource to be deleted on
                the remote storage
        """
        # NOTE: If a folder is specified by the path, we will
        # need to delete all other objects that contain that
        # folder's prefix --explained in the LOG.md
        prefix = remote_path
        objects_to_delete = []

        for obj in self._bucket.objects.filter(Prefix=prefix):
            objects_to_delete.append({'Key': obj.key})

        self._bucket.delete_objects(Delete={
                                    'Objects': objects_to_delete})

    def _move(self, remote_src_path, remote_dest_path):
        """
        Moves a resource in the s3-bucket.

        parameters
            remote_src_path
                remote path of the resource before it was moved

            remote_dest_path
                remote path of the resource after it was moved
        """
        # NOTE: Relatively more complex, have to copy all
        # objects to with new key to the bucket and then
        # delete all objects with the prefix that were moved.
        # Even more complex when folders are involved.
        old_prefix = remote_src_path
        new_prefix = remote_dest_path
        objects_to_move = []

        for obj in self._bucket.objects.filter(Prefix=prefix):
            objects_to_move.append({'Key': obj.key})

        for obj in objects_to_move:
            new_key = os.path.join(new_prefix, obj.key.split(old_prefix, 1)[1])
            logging.info("The new key for the object {} is {}".format(
                         obj.key, new_key))

            cpy_src = os.path.join(self._bucket_name, obj.key)
            logging.info("The source loc for copy is {}".format(cpy_src))
            self.client.copy_object(Bucket=self._bucket_name,
                                    CopySource=cpy_src,
                                    Key=new_key)
            # also note that object to move is also the object to be
            # deleted, so we'll just delete that object over here
            logging.info("Deleting object with key: {}".format(obj.key))
            self._bucket.delete_objects(Delete={'Objects': obj})
