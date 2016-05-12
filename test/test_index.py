import unittest
from tsdb.utils_indices import TreeIndex, BitmapIndex
import os

class TreeIndexTests(unittest.TestCase):

    def setUp(self):
        self.dirPath = "persistent_files/testing"
        if not os.path.isdir(self.dirPath):
            os.makedirs(self.dirPath)
            self._createdDirs = True
        else:
            self._createdDirs = False

        self.blarg_index = TreeIndex(db_name='testing',fieldName='blarg')
        self.blarg_index.insert(1,'ts-1')
        self.blarg_index.insert(1,'ts-2')
        self.blarg_index.insert(1,'ts-3')
        self.blarg_index.insert(1,'ts-4')
        self.blarg_index.insert(1,'ts-5')
        self.blarg_index.insert(2,'ts-6')
        self.blarg_index.insert(7,'ts-7')
        self.blarg_index.insert(8,'ts-8')
        self.blarg_index.insert(2,'ts-9')
        self.blarg_index.insert(8,'ts-10')

    def tearDown(self):
        self.blarg_index.deleteIndex()
        if self._createdDirs:
            os.removedirs(self.dirPath)

    def test_get(self):
        self.assertEqual(set(self.blarg_index.getEqual(8)),set(['ts-8','ts-10']))

    def test_getHigher(self):
        self.assertEqual(set(self.blarg_index.getHigher(6)),set(['ts-7','ts-8','ts-10']))

    def test_getLower(self):
        self.assertEqual(set(self.blarg_index.getLower(2)),set(['ts-1','ts-2','ts-3','ts-4','ts-5']))

    def test_missingField(self):
        self.assertEqual(set(self.blarg_index.getEqual(11)),set([]))

    def test_remove(self):
        self.assertEqual(set(self.blarg_index.getEqual(8)),set(['ts-8','ts-10']))
        self.blarg_index.remove(fieldValue=8,pk='ts-8')
        self.assertEqual(set(self.blarg_index.getEqual(8)),set(['ts-10']))

    def test_missingPK(self):
        with self.assertRaises(ValueError):
            self.blarg_index.remove(fieldValue=8,pk='ts-100')


class BitmapIndexTests(unittest.TestCase):

    def setUp(self):
        self.dirPath = "persistent_files/testing"
        if not os.path.isdir(self.dirPath):
            os.makedirs(self.dirPath)
            self._createdDirs = True
        else:
            self._createdDirs = False

        self.space_index = BitmapIndex(values = ['comet','alien','satellite'], pk_len=4,\
                            db_name='testing',fieldName='outerspace')
        self.space_index.insert('comet','ts-1')
        self.space_index.insert('comet','ts-2')
        self.space_index.insert('comet','ts-3')
        self.space_index.insert('alien','ts-4')
        self.space_index.insert('alien','ts-5')
        self.space_index.insert('satellite','ts-6')


    def tearDown(self):
        self.space_index.deleteIndex()
        if self._createdDirs:
            os.removedirs(self.dirPath)

    def test_getEqual(self):
        self.assertEqual(set(self.space_index.getEqual('alien')),set([b'ts-4',b'ts-5']))

    def test_getNotEq(self):
        self.assertEqual(set(self.space_index.getNotEq('comet')),set([b'ts-4',b'ts-5',b'ts-6']))

    def test_wrongLengthKey(self):
        with self.assertRaises(ValueError):
            self.space_index.insert('alien','ts-4000000')

    def test_fakeField(self):
        with self.assertRaises(ValueError):
            self.space_index.insert('moon','ts-1')

    def test_update(self):
        self.space_index.insert('alien','ts-1')
        self.assertEqual(set(self.space_index.getEqual('alien')), set([b'ts-1', b'ts-4',b'ts-5']))

    def test_get(self):
        self.assertEqual(set(self.space_index.get('ts-6')), set('satellite'))

    def test_remove(self):
        self.space_index.remove('ts-1')
        self.assertEqual(set(self.space_index.getEqual('alien')), set([b'ts-4', b'ts-5']))

    def test_allKeys_andInsertNew(self):
        self.space_index.insert('satellite','ts-7')
        self.assertEqual(set(self.space_index.getAllKeys()), set([b'ts-1', b'ts-2', b'ts-3', b'ts-4', b'ts-5', b'ts-6', b'ts-7']))

    def test_insert_withBytes(self):
        self.space_index.insert('satellite',b'ts-7')
        self.assertEqual(set(self.space_index.get('ts-7')), set('satellite'))

    def test_remove_invalidKey(self):
        with self.assertRaises(KeyError):
            self.space_index.remove('ts-9')

    def test_getEqual_invalidValue(self):
        with self.assertRaises(ValueError):
            self.space_index.getEqual('moon')

    def test_getNotEqual_invalidValue(self):
        with self.assertRaises(ValueError):
            self.space_index.getNotEq('moon')

    def test_loadFromFile(self):
        del self.space_index
        self.space_index = BitmapIndex(values = ['comet','alien','satellite'], pk_len=4,\
                            db_name='testing',fieldName='outerspace')
        self.assertEqual(set(self.space_index.getAllKeys()), set([b'ts-1', b'ts-2', b'ts-3', b'ts-4', b'ts-5', b'ts-6']))

    def test_loadFromFile_withOverwrites(self):
        self.space_index.insert('alien', 'ts-6')
        self.space_index.insert('comet', 'ts-7')
        self.space_index.insert('satellite', 'ts-7')
        del self.space_index
        self.space_index = BitmapIndex(values = ['comet','alien','satellite'], pk_len=4,\
                            db_name='testing',fieldName='outerspace')
        self.assertEqual(set(self.space_index.getAllKeys()), set([b'ts-1', b'ts-2', b'ts-3', b'ts-4', b'ts-5', b'ts-6', b'ts-7']))

if __name__ == '__main__':
    unittest.main()
