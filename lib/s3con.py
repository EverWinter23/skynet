'''
20th june 2018 wednesday
NOTE:
    Any changes you make should not compromise
    with the atomicity of the actions. Review
    carefully and multiple times before making
    any changes, albeit reordering of the stmts.
'''

import os
import math
import shelve
import logging
import threading
from boto3 import client
from boto3 import resource
from threading import Lock
from threading import Thread
from filechunkio import FileChunkIO

# useful constants
KB = 1024
MB = KB * KB
PART_LIM = 5 * MB

# string literals for 'shelve'
XPARTS = 'xparts'
UPLOAD_ID = 'upload_id'
XPARTS_FILE = 'xparts'
PART_LIST = 'parts'


class S3Con:
    """
    Establishes connection with s3 bucket and helps
    in sending, moving and deleting files on the remote
    bucket storage.

    parameters
        bucket_name: str
            name of the aws s3 bucket(case sensitive) to
            which the files are to be uploaded.
        key_id: str
            amazon access-key of the dev's IAM account.
        secret_key: str
            amazon secret-access-key of the dev's IAM
            account. Not to be shared.
        region: str
            default aws region
        db_path: str
            path to the database where actions are
            stored, for storing shelve variables.
        _m_part: boolean
            if set to True, it will upload the file by
            partitioning the file into mulitple parts if
            they are above a certain threshold --PART_LIM.
        _xthreads: int
            number of threads to spawn for uploading the
            parts simultaneously.

    attributes
        _notifier: Notifier
            sends updates about partial part uploads
            to the remote DB for progress monitoring
            of multipart uploads.
    """

    def __init__(self, bucket_name, key_id, secret_key, region,
                 db_path, _m_part=True, _xthreads=5):

        self._client = client('s3', aws_access_key_id=key_id,
                              aws_secret_access_key=secret_key)
        self._bucket_name = bucket_name
        self._bucket = resource('s3').Bucket(bucket_name)
        self._xparts = shelve.open(os.path.join(db_path, XPARTS_FILE),
                                   flag='c', protocol=None, writeback=True)
        self._m_part = _m_part
        self._notifier = None
        self._xthreads = _xthreads

    def _send(self, src_path, remote_path):
        """
        Transfers a resource(file) to the s3-bucket.

        parameters
            src_path: str
                local path of the resource to be sent
            remote_path: str
                mapped path of the src_path on the
                remote storage
        """
        if os.path.exists(src_path) is False and self._m_part:
            logging.info('The file \'{}\' does not exist.'.format(src_path))
            logging.info('Removing partitioning info.')
            self._abort_parts(src_path)
            raise FileNotFoundError

        elif os.stat(src_path).st_size > PART_LIM and self._m_part:
            self._send_parts(src_path, remote_path)

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
            remote_path: str
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
        self._client.delete_objects(Bucket=self._bucket_name,
                                    Delete={
                                        'Objects': objects_to_delete})

    def _move(self, remote_src_path, remote_dest_path):
        """
        Moves a resource in the s3-bucket.

        parameters
            remote_src_path: str
                remote path of the resource before it was moved
            remote_dest_path: str
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

    def _set_notifier(self, notifier):
        """
        Sets the notifier for sending partial upload updates.

        parameters:
            notifier: Notifier
                an instance of Notifier class
        """
        self._notifier = notifier

    def _send_parts(self, src_path, key):
        """
        Uploads the file by partitioning the file into
        mulitple segements.

        parameters
            src_path: str
                local path of the resource to be sent
            key: str
                the mapped path of the local file on
                the remote storage
        """
        logging.info('Loading partitioning info.')
        _upload_id = self._load_parts(src_path, key)

        # upload x parts simultaneously
        while self._xparts[XPARTS]:
            logging.info('Parts: {}'.format(self._xparts[XPARTS]))
            _num_parts_ = len(self._xparts[XPARTS])
            _threads_ = []

            _thread_count = min(self._xthreads, _num_parts_)
            _lock = Lock()
            logging.info('Using {} \'threads\''.format(_thread_count))

            for x in range(_thread_count):
                _threads_.append(Thread(target=self._upload_part,
                                        args=(src_path, key, _upload_id,
                                              self._xparts[XPARTS][x],
                                              _lock)))
            # start the threads
            for _thread in _threads_:
                _thread.start()

            # wait for all 'threads' to complete
            for _thread in _threads_:
                _thread.join()

        logging.info(self._xparts[PART_LIST])
        # notify s3 to assemble parts
        self._client.complete_multipart_upload(
                     Bucket=self._bucket_name,
                     Key=key, UploadId=_upload_id,
                     MultipartUpload={"Parts": self._xparts[PART_LIST]})

        # clean up shelve for next upload
        self._xparts.clear()
        self._xparts.sync()

    def _upload_part(self, src_path, key, _upload_id, part_id, _lock):
        """
        Uploads a part of the file to the remote
        storage.

        parameters
            src_path: str
                local path of the resource to be sent
            key: str
                the mapped path of the local file on
                the remote storage
            _upload_id: str
                multipart upload id for the upload
            _part_id: int
                the id of the part being uploaded
            _lock: Lock
                grants exclusive write access to the
                thread for writing to the 'shelve'
        """
        size = os.stat(src_path).st_size
        offset = (part_id - 1) * PART_LIM

        # check for overflow, last part could be less than 5MB
        _bytes = min(PART_LIM, size - offset)

        part = FileChunkIO(src_path, 'r', offset=offset,
                           bytes=_bytes).read()

        result = self._client.upload_part(
                      Body=part, Bucket=self._bucket_name, Key=key,
                      UploadId=_upload_id, PartNumber=part_id)

        self._mark_part(src_path, part_id, _lock, result)

    def _load_parts(self, src_path, key):
        """
        Loads the partioning info of the file
        from the disk.

        parameters
            src_path: str
                local path of the resource to be sent
            key: str
                the mapped path of the local file on
                the remote storage
        """
        if UPLOAD_ID not in self._xparts:
            logging.info('No partitioning info found. Partitioning file.')
            self._xparts[UPLOAD_ID] = self._client.create_multipart_upload(
                                      Bucket=self._bucket_name,
                                      Key=key)['UploadId']
            self._xparts.sync()

        if XPARTS not in self._xparts:
            size = os.stat(src_path).st_size
            self._xparts[XPARTS] = list(range(1, math.ceil(size/PART_LIM) + 1))
            self._xparts.sync()

        if PART_LIST not in self._xparts:
            self._xparts[PART_LIST] = [{} for x in range(len(
                                      self._xparts[XPARTS]))]
            self._xparts.sync()

        return self._xparts[UPLOAD_ID]

    def _mark_part(src_path, self, part_id, _lock, result):
        """
        Marks the part as uploaded by removing
        it from the list of parts to be uploaded.

        parameters
            src_path: str
                local path of the resource to be sent
            _part_id: int
                the id of the part being uploaded
            _lock: Lock
                grants exclusive write access to the thread
                for writing to the 'shelve'
            result: dict
                response of the aws-s3 of the uploaded part
        """

        # NOTE: avoid deadlocks when making changes
        # provides the thread with exclusive write access
        with _lock:
            self._xparts[XPARTS].remove(part_id)

            # exclusive write access to the remote DB
            self._notifier._mark_part(src_path)

            self._xparts[PART_LIST][part_id - 1] = {"PartNumber": part_id,
                                                    "ETag": result["ETag"]}

            # sync only after noth changes have been written
            self._xparts.sync()
        # logging.info('part_id={} uploaded.'.format(part_id))
        # uncomment for listing parts uploaded to the bucket
        logging.info(self._xparts[XPARTS])

    def _abort_parts(self, key):
        """
        Removes the partitioning info of the corresponding
        file from the disk, and signals aws-s3 to remove
        the partitions of that file from the remote storage.

        parameters
            key: str
                the mapped path of the local file on
                the remote storage
        """
        _upload_id = self._load_parts()
        self._client.abort_multipart_upload(Bucket=self._bucket_name,
                                            Key=key, UploadId=_upload_id)

        # clean up shelve for next upload
        self._xparts.clear()
        self._xparts.sync()


if __name__ == '__main__':
    main()
