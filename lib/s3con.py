'''
20th june 2018 wednesday
'''

import os
import shelve
import logging
from boto3 import client
from boto3 import resource
from .chunkio import ChunkIO
from mulitprocessing import Process

KB = 1024
MB = KB * KB
PART_LIM = 5 * MB
XPARTS = 'xparts'
XPARTS_FILE = 'xparts'


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

        self._xparts = shelve.open(os.path.join(db_path, XPARTS_FILE),
                                   flag='c', protocol=None, writeback=True)
        self._xthreads = _xthreads
        self._multipart = _multipart

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

        if os.stat(src_path).st_size < PART_LIM and self._multipart:
            self._send_parts(src_path)
        else:
            with open(src_path, 'rb') as data:
                self._client.upload_fileobj(Fileobj=data,
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

        if not objects_to_delete:
            return

        logging.info("To delete {}".format(objects_to_delete))
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
        old_key = remote_src_path
        new_key = remote_dest_path
        logging.info("To move {}".format(old_key))

        cpy_src = os.path.join(self._bucket_name, old_key)
        logging.info("The source loc for copy is /'{}/'".format(cpy_src))

        self._client.copy_object(Bucket=self._bucket_name,
                                 CopySource=cpy_src,
                                 Key=new_key)

        # also note that object to move is also the object to be
        # deleted, so we'll just delete that object over here

        self._client.delete_object(Bucket=self._bucket_name,
                                   Key=old_key)
    
    def _send_parts(self, src_path):
        logging.inof('Loading partitioning info.')
        self._load_parts()
        s3part = self._bucket.intiate_multipart_upload(src_path)
        
        # upload x parts simultaneously
        while self._xparts[XPARTS]:
            _num_parts_ = len(self._xparts[XPARTS]))
            _prcoesses_ = []

            _proc_count = min(self._xthreads, _num_parts_)
            logging.info('Uploading using {} \'threads\'').format(_proc_count)
            for x in range(_proc_count):
                _prcoesses_.append(Process(target=self._upload_part, 
                                            args=(src_path, s3part,
                                            self._xparts[XPARTS][x])
                                    ).start())

            # wait for all 'threads' to complete
            for _proc in _prcoesses_:
                _proc.join()
    
    def _upload_part(self, src_path, s3part, part_id):
        size = os.stat(src_path).st_size
        offset = part_id * PART_LIM * MB
        logging.info('part_id={}, offset={}'.format(part_id, offset))
        # check for overflow, last part could be less than 5MB
        _bytes = min(PART_LIM, size - offset)
        logging.info('part_id={}, bytes={}'.format(part_id, _bytes))
        with ChunkIO(src_path, 'r', offset=offset, bytes=_bytes) as part:
            s3part.upload_part_from_file(part, part_id)
            self._mark_part(part_id)



    def _load_parts(self):
        if XPARTS not in self._xparts:
            logging.info('No partitioning info found. Partitioning file.')
            size = os.stat(src_path).st_size
            self._xparts[XPARTS] = list(1, range(math.ceil(size/5) + 1)
            self._xparts.sync()
        # will also have to intiate multipart here


    def _mark_part(self, part_id):
        self._xparts[XPARTS].remove(part_id)
        self._xparts[XPARTS].sync()
        logging.info('part_id={} uploaded.'.format(part_id))
        # TODO schema changes, mark part to DB

    def _abort_parts(self):
        pass
