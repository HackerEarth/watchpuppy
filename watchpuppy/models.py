import json

from mongoengine import (Document, StringField, DateTimeField, IntField,
                         ListField)


class UploadStatus(object):
    NOT_UPLOADED = 0
    UPLOAD_SUCCESSFUL = 1
    FAILED = 3

class BaseDocument(Document):
    meta = {'abstract': True}
    def update(self, **kwargs):
        data = {}
        for key, value in kwargs.iteritems():
            new_key = 'set__' + key
            data[new_key] = value
        super(BaseDocument, self).update(**data)

    @classmethod
    def create_or_update(cls, query_fields={}, update_fields={}):
        """Creates/Updates a document with the given query and update fields.

        query_fields: these key/value pairs are used to query the db
        update_fields: these fields are used to update the fields of the
           matching docs retrieved using query_fields
        """
        documents = cls.objects.filter(**query_fields)

        no_of_documents = documents.count()
        if no_of_documents == 0:
            return cls(**update_fields).save()

        if no_of_documents>1:
            raise Exception("Returned more than 1 row ")

        document = documents[0]
        document.update(**update_fields)
        #document.save()
        return document

class FileInfo(BaseDocument):
    meta = {
        'db_alias': 'watchpuppy',
    }
    file_path = StringField(required=True)
    s3_key = StringField(required=True)
    created = DateTimeField(required=True)
    debug_info = StringField(default='')

    upload_status = IntField(default=UploadStatus.NOT_UPLOADED)




class FileUploaderLog(BaseDocument):
    SUCCESSFUL = 1
    FAILED = 0

    meta = {
        'db_alias': 'watchpuppy'
    }

    files_uploaded = ListField(default=[])
    start_time = DateTimeField()
    end_time = DateTimeField()
    run_status = IntField(default=SUCCESSFUL)
    logs = ListField(default='')
