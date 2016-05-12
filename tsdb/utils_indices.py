"""All the index classes.

Currentlly:
    PKIndex: Primary Key Index
    TreeIndex: Tree based index using a AVL tree for high cardinality fields
    BitmapIndex: Bitmap index for low cardinality fields
    vptreeIndex: for similarity search
"""

# from .persistentdb import FILES_DIR
# from .baseclasses import BaseIndex
from collections import defaultdict
import pickle
import os
import bintrees
import numpy as np
from tsdb.tsdb_constants import *
import abc

class Index(metaclass = abc.ABCMeta):
    """
    Implementation of polymorphism as Rahul suggested
    Interface that all indices should support
    """
    @abc.abstractmethod
    def __init__(self):
        '''

        Initialization
        1. Initialize DB Parameters
        2. Create file system for persistence
        '''
        pass

    @abc.abstractmethod
    def insert(self, fieldValue, pk):
        """
        Insert the value into the appropriate place in the tree
        """
        pass

    @abc.abstractmethod
    def remove(self, fieldValue, pk):
        """
        remove a primary key from the index
        """
        pass

    @abc.abstractmethod
    def getEqual(self, fieldValue):
        """
        return set of primary keys that match this fieldValue
        """
        pass

class PKIndex(Index):
    """
    PK Index using Pickle serialization and a write ahead log.
    Essentially a (pk: offset) dictionary with writelog and disk storage.

    """
    def __init__(self, db_name='default'):
        self.filename = FILES_DIR + '/'+db_name+'/'+'pks.p'
        self.writelog = FILES_DIR + '/'+db_name+'/'+'writelog.idx'

        # if file never created before, create it
        if not os.path.exists(self.filename):
            self.dict = dict()
            self.save_pickle(new=True)
        else:
            self.dict = self.load_pickle()

        if not os.path.exists(self.writelog):
            self.fd = open(self.writelog, 'x')
        else: # if log had values, load, save, and wipe them
            self.fd = self.load_and_clear_log()

        self.pk_count = len(self.dict.keys())

        self.fd.seek(0,2)
        self.writeptr = self.fd.tell()

    def load_and_clear_log(self, loaded=False, close=False):
        """
        if loaded, writelog assumed to be open. otherwise, closed.
        loads values, clears writelog and opens.
        if close, then file descriptor not return.
        """
        if loaded:
            self.fd.close()
        self.fd = open(self.writelog,'r')
        items = [l.strip().split(':') for l in self.fd.readlines()]
        writelog_dict = {k:int(v) for k,v in items}
        self.dict.update(writelog_dict)
        self.save_pickle()
        self.fd.close()
        open(self.writelog, 'w').close() # this deletes the log
        if not close:
            return open(self.writelog, 'w')

    def save_pickle(self, new=False):
        form = 'xb' if new else 'wb'
        with open(self.filename, form, buffering=0) as fd:
            pickle.dump(self.dict, fd)

    def load_pickle(self):
        with open(self.filename, 'rb', buffering=0) as fd:
            return pickle.load(fd)

    def keys(self):
        return self.dict.keys()

    def __len__(self):
        return self.pk_count

    def insert(self, key, value):
        # insert the value into the appropriate place in the tree
        # delegates to __setitem__
        self[key] = value

    def remove(self, key, value=None):
        # added to match interface. Value unnecessary here.
        self.fd = self.load_and_clear_log(loaded=True)
        del self.dict[key]
        self.save_pickle()

    def getEqual(self, key):
        return self[key]

    def close(self):
        self.load_and_clear_log(loaded=True, close=True)

    def __getitem__(self, key):
        return self.dict[key]

    def __setitem__(self, key, value):
        if key not in self.dict.keys():
            self.pk_count += 1
            self.dict[key] = value
            self.fd.write(key+':'+str(value)+'\n')
            if self.pk_count % REFRESH_RATE == 0:
                self.fd = self.load_and_clear_log(loaded=True)
        else:
            self.dict[key] = value

    def __iter__(self):
        return iter(self.dict.keys())

    def __contains__(self, key):
        return key in self.dict.keys()

class TreeIndex(Index):

    def __init__(self, fieldName='default', db_name='default'):
        self.db_name = db_name
        self.name = fieldName
        self.filename = FILES_DIR+'/'+db_name+'/'+fieldName+'.idx'
        self.dict = defaultdict(set)
        self.tree = self._load()

        # variable that checks the staus of the in memory
        self._stale = False

    def _persist(self):
        with open(self.filename,'wb') as f:
            pickle.dump(self.tree, f)

    def _load(self):
        '''
        load from file if the file exists, else return empty AVL tree
        '''

        if os.path.isfile(self.filename):
            with open(self.filename,'rb') as f:
                return pickle.load(f)
        else:
            # print("Loading Empty Tree")
            return bintrees.AVLTree()

    def _checkStale(self):
        if self._stale:
            self._load()
            self._stale = False

    def insert(self,fieldValue, pk):
        self._checkStale()

        if fieldValue in self.tree:
            if pk not in self.tree[fieldValue]:
                self.tree[fieldValue] = self.tree[fieldValue] + [pk]
        else:
            self.tree[fieldValue] = [pk]
        self._persist()
        self._stale = True

    def remove(self, fieldValue, pk):
        self._checkStale()
        if fieldValue in self.tree:
            matchingPks = self.tree[fieldValue]
            if pk in matchingPks:
                del matchingPks[matchingPks.index(pk)]
                self.tree[fieldValue] = matchingPks
            else:
                raise ValueError("primary_key {} does not exist in Treeindex for {}".format(pk, self.name))
        else:
            import pdb; pdb.set_trace()
            raise ValueError("Field value {} does not have index".format(self.name))
        self._persist()
        self._stale = True

    def get(self, fieldValue, operator_num=2):
        """
        'get' wrapper function to delegate to other functions
        based on submitted operator
        """
        if operator_num == 0:
            return self.getLower(fieldValue)
        elif operator_num == 1:
            return self.getHigher(fieldValue)
        elif operator_num == 2:
            return self.getEqual(fieldValue)
        elif operator_num == 3:
            return self.getNotEq(fieldValue)
        elif operator_num == 4:
            return self.getLowerOrEq(fieldValue)
        elif operator_num == 5:
            return self.getHigherOrEq(fieldValue)
        raise RuntimeError("should be impossible")

    def getEqual(self, fieldValue):
        self._checkStale()

        if fieldValue in self.tree:
            return set(self.tree[fieldValue])
        else:
            return set()

    def getLower(self, fieldValue):
        self._checkStale()
        retList = set()
        for v in self.tree[:fieldValue]:
            retList = retList | self.getEqual(v)

        return set(retList)

    def getHigher(self, fieldValue):
        self._checkStale()
        retList = set()
        for v in self.tree[fieldValue:]:
            if v != fieldValue:
                retList = retList | self.getEqual(v)
        return set(retList)

    def getHigherOrEq(self, fieldValue):
        return self.getHigher(fieldValue) | self.getEqual(fieldValue)

    def getLowerOrEq(self, fieldValue):
        return self.getLower(fieldValue) | self.getEqual(fieldValue)

    def getNotEq(self, fieldValue):
        return self.getAllKeys() - self.getEqual(fieldValue)

    def getAllKeys(self):
        pks = set()
        for value in self.trees.values():
            pks = pks | value
        return pks

    def deleteIndex(self):
        if os.path.isfile(self.filename):
            os.remove(self.filename)


class BitmapIndex(Index):

    def __init__(self, values, pk_len = 4, fieldName='default', db_name='default'):
        # Requires the user to specify pk_len, the fixed length of the primary keys
        self.pks_len = pk_len
        # 'values' is a list of possible fieldValues
        self.values = values
        self.values_len = len(values)
        # File containing the bitmap indices for this field
        self.filename = 'persistent_files/'+db_name+'/'+fieldName+'_index.txt'

        # Empty list to store the the lists of booleans for each field value.
        #CJ: I am storing the indices as a list of list of boolean because it
        # is more memory-efficient to append to append to the lists than it is to keep
        # vertically stacking numpy arrays.
        self.bmindex_list = [[] for ii in range(self.values_len)]

        # Empty dictionary to store primary keys and their indices in self.bmindex
        self.pks_dict = {}
        self.dict_pks = {}

        # Create desired files if they don’t exist.
        # Load files if they do exist.

        # Open the associated files for updating
        if not os.path.exists(self.filename):
            self.bmindex = open(self.filename, "xb+", buffering=0)
            self.last_pk_idx = 0

        else:
            # Load from file
            item_counter = 0

            self.bmindex = open(self.filename, "r+b", buffering=0)
            while True:
                # Try to read the primary key for this line
                prim_key = self.bmindex.read(self.pks_len)
                if prim_key == b'':
                    # Reached last line.
                    break
                elif prim_key in self.pks_dict.keys():
                    del self.dict_pks[self.pks_dict[prim_key]]
                self.pks_dict.update({prim_key:item_counter})
                self.dict_pks.update({item_counter:prim_key})

                for ii in range(self.values_len):
                    try:
                        boolean = bool(int(self.bmindex.read(1)))
                        self.bmindex_list[ii].append(boolean)
                    except ValueError:
                        # Thrown if the sentinel value of b'-' has been written
                        del self.pks_dict[prim_key]
                        del self.dict_pks[item_counter]
                        break
                item_counter += 1
            self.last_pk_idx = item_counter

    def insert(self, fieldValue, pk):
        # Updates the booleans that indicate the field's values for the appropriate pk.
        # Adds pk's that are not already present, and updates pk's that are already present.

        # Pk's are stored as bytes, so if the user passed ints or strings, convert to bytes.
        if type(pk) != bytes:
            pk_str = bytes(str(pk),'utf-8')
        else:
            pk_str = pk

        if len(pk_str) != self.pks_len:
            raise ValueError("Primary key {} is not of the pre-specified length {}".format(pk,self.pks_len))

        # Check if the fieldValue is valid.  If not, throw an error.
        if fieldValue not in self.values:
            raise ValueError('\"{}\" not in the set of user-specified values: {}'.format(fieldValue, self.values))
        else:
            # Find field index from the objects values
            field_index = self.values.index(fieldValue)

            # Add the pk to the dictionary along with its index
            if pk_str in self.pks_dict.keys():
                del self.dict_pks[self.pks_dict[pk_str]]
                del self.pks_dict[pk_str]

            self.pks_dict.update({pk_str:self.last_pk_idx})
            self.dict_pks.update({self.last_pk_idx:pk_str})

            self.last_pk_idx += 1

            # Add the pk and the booleans to the end of the file
            self.bmindex.seek(0,2)
            self.bmindex.write(pk_str)

            # Update the in-memory lists and write to file
            for ii in range(self.values_len):
                if ii==field_index:
                    self.bmindex_list[ii].append(True)
                    self.bmindex.write(b'1')
                else:
                    self.bmindex_list[ii].append(False)
                    self.bmindex.write(b'0')

    def remove(self, pk):
        # Removes the entry for this field and primary key from the database

        if type(pk) != 'bytes':
            pk_str = bytes(str(pk),'utf-8')

        # Check if the pk is in the file or not.
        if pk_str not in self.pks_dict.keys():
            raise KeyError('\"{}\" not a valid primary key'.format(pk))
        else:
            # Remove the primary key from the dictionaries
            del self.dict_pks[self.pks_dict[pk_str]]
            del self.pks_dict[pk_str]

            # Write a sentinel value to the persistent database
            self.bmindex.write(pk_str + (self.values_len*b'-'))

    def getEqual(self, fieldValue):
        # Returns the list of primary keys that match this fieldValue
        # Find the index of this fieldValue in the list of valid values
        if fieldValue not in self.values:
            raise ValueError('\"{}\" not in the set of user-specified values: {}'.format(fieldValue, self.values))
        else:
            fieldValue_index = self.values.index(fieldValue)
            matching_keys = []

            for ii in self.dict_pks.keys():
                if self.bmindex_list[fieldValue_index][ii] == True:
                    matching_keys.append(self.dict_pks[ii])

            return set(matching_keys)

    def getNotEq(self, fieldValue):
        if fieldValue not in self.values:
            raise ValueError('\"{}\" not in the set of user-specified values: {}'.format(fieldValue, self.values))
        else:
            fieldValue_index = self.values.index(fieldValue)

            matching_keys = []

            for ii in self.dict_pks.keys():
                if self.bmindex_list[fieldValue_index][ii] == False:
                    matching_keys.append(self.dict_pks[ii])

            return set(matching_keys)

    def getAllKeys(self):
        return set(self.pks_dict.keys())

    def deleteIndex(self):
        if os.path.isfile(self.filename):
            os.remove(self.filename)

    def get(self,pk):
        index = self.pks_dict[bytes(pk, 'utf-8')]
        for ii in range(self.values_len):
            value_index = self.bmindex_list[ii][index]
            if value_index == True:
                return self.values[ii]

    def __del__(self):
        self.bmindex.close()
