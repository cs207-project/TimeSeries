"""A heap that is used in the persistentdb implementation
"""

# from .persistentdb import TYPES, TYPE_DEFAULT
import os
import struct
import timeseries
import json
import pickle

# see https://docs.python.org/3.4/library/struct.html#struct-format-strings
TYPES = {
    'float': 'd',
    'bool': '?',
    'int': 'i'
}# if changed, need to modify in persistentdb.py as well

TYPE_DEFAULT = {
    'float': 0.0,
    'bool': False,
    'int': 0
}# if changed, need to modify in persistentdb.py as well

TS_FIELD_LENGTH = 4
BYTES_PER_NUM = 8

class HeapFile:
    def __init__(self, heap_file_name):
        self.filename = heap_file_name
        if not os.path.exists(self.filename):
            #DNY: buffering=0 only allowed in binary mode, see python docs
            self.fd = open(self.filename, "xb+", buffering=0)
        else:
            self.fd = open(self.filename, "r+b", buffering=0)
        self.readptr = self.fd.tell()
        self.fd.seek(0,2)#DNY: seek the end of the file
        self.writeptr = self.fd.tell()

    def close(self):
        self.fd.close()

class MetaHeapFile(HeapFile):
    def __init__(self, heap_file_name, schema):
        super().__init__(heap_file_name)
        # if metaheap is new, write it to disk
        if not os.path.exists(heap_file_name+'_metadata.met'):
            self._create_compression_string(schema)
            with open(heap_file_name+'_metadata.met','xb',buffering=0) as fd:
                pickle.dump((self.compression_string,
                             self.fields,
                             self.fieldsDefaultValues,
                             self.byteArrayLength), fd)
            # print("new metaheap meta values written to disk")
        # otherwise load it
        else:
            with open(heap_file_name+'_metadata.met','rb',buffering=0) as fd:
                self.compression_string, self.fields, self.fieldsDefaultValues, self.byteArrayLength = pickle.load(fd)
            # print("old metaheap meta values loaded from disk")

    def _create_compression_string(self, schema):
        fieldList = sorted(list(schema.keys()))
        # pk and ts will be stored in the index file and tsheap file respectively
        fieldList.remove('ts')
        fieldList.remove('pk')
        self.compression_string = ''
        # DNY: ordered list of storage of fields
        self.fields = []
        # DNY: to store default values of each field, as placeholders
        self.fieldsDefaultValues = []
        for field in fieldList:
            self.compression_string += TYPES[schema[field]['type']]
            self.fields.append(field)
            self.fieldsDefaultValues.append(TYPE_DEFAULT[schema[field]['type']])
            # create field to check whether field is set, later
            if schema[field]['type'] != "bool":
                self.compression_string += TYPES['bool']
                self.fields.append(field+"_set")
                self.fieldsDefaultValues.append(False)
        self.byteArrayLength = len(struct.pack(self.compression_string,
                                               *self.fieldsDefaultValues))

    def check_byteArray(self,byteArray):
        "method to double check compression succeeded"
        assert(len(byteArray) == self.byteArrayLength)

    def encode_and_write_meta(self, meta, pk_offset=None):
        "takes metadata and writes to file, return the offset of the write"
        byteArray = struct.pack(self.compression_string,*meta)
        self.check_byteArray(byteArray)
        if pk_offset is None:
            pk_offset = self.writeptr
        self.fd.seek(pk_offset)
        self.fd.write(byteArray)
        # DNY: seek the end of the file in case new element written
        self.fd.seek(0,2)
        self.writeptr = self.fd.tell()
        return pk_offset

    def read_and_return_meta(self,pk_offset):
        self.fd.seek(pk_offset)
        buff = self.fd.read(self.byteArrayLength)
        #check that reading and writing worked
        # print(self.metaFields)
        # print(struct.unpack(self.compression_string,buff))
        return list(struct.unpack(self.compression_string,buff))

class TSHeapFile(HeapFile):
    def __init__(self, heap_file_name, ts_length):
        super().__init__(heap_file_name)
        if not os.path.exists(heap_file_name+'_metadata.met'):
            self.ts_length = ts_length
            # DNY: Store as floats, *2 for both times and values
            self.byteArrayLength = self.ts_length * 2 * BYTES_PER_NUM
            with open(heap_file_name+'_metadata.met','xb',buffering=0) as fd:
                pickle.dump((self.ts_length,self.byteArrayLength), fd)
            # print("new tsheap meta values written to disk")
        # otherwise load it
        else:
            with open(heap_file_name+'_metadata.met','rb',buffering=0) as fd:
                self.ts_length, self.byteArrayLength = pickle.load(fd)
            # print("old tsheap meta values loaded from disk")


    def encode_and_write_ts(self, ts):
        ts_items = ts.items
        times = [float(i[0]) for i in ts_items]
        values = [float(i[1]) for i in ts_items]
        byteArray = struct.pack('%sd' % (2*self.ts_length), *times, *values)
        assert(len(byteArray) == self.byteArrayLength)

        # dataBytes = json.dumps(ts.to_json()).encode()
        # lengthFieldBytes = (len(dataBytes)+TS_FIELD_LENGTH).to_bytes(TS_FIELD_LENGTH, byteorder='little')
        # byteArray = lengthFieldBytes + dataBytes

        self.fd.seek(self.writeptr)
        ts_offset = self.fd.tell()
        self.fd.write(byteArray)
        self.fd.seek(0,2)#DNY: seek the end of the file
        self.writeptr = self.fd.tell()
        return ts_offset

    def read_and_decode_ts(self, offset):
        self.fd.seek(offset)
        # ts_length = int.from_bytes(self.fd.read(TS_FIELD_LENGTH), byteorder='little')
        # self.fd.seek(offset + TS_FIELD_LENGTH)
        buff = self.fd.read(self.byteArrayLength)
        items = struct.unpack('%sd' % (2*self.ts_length),buff)
        return timeseries.TimeSeries(items[:self.ts_length], items[self.ts_length:])
        # return timeseries.TimeSeries.from_json(json.loads(buff.decode()))
