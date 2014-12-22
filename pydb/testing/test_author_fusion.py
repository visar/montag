import unittest

import logging
logger = logging.getLogger('test_author_fusion')

import pydb.localdb
import pydb.friendsdb
import pydb.mergedb
import pydb.foreigndb
import pydb.maindb

import copy
import os

import mock

logging.basicConfig(level=logging.INFO)

def get_schema_dir():
    return os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'db-schemas'))


def build_main_db_memory_only(schema_path):
    """ builds a database with all subdatabases in memory """
    local_db = pydb.localdb.LocalDB(":memory:", schema_path, enable_db_sync=False)
    merge_db = pydb.mergedb.MergeDB(":memory:", schema_path, enable_db_sync=False)
    merge_db.add_source(local_db)
    friends_db = pydb.friendsdb.FriendsDB(":memory:", schema_path)
    index_server = mock.MagicMock()

    def build_foreign_db(friend_id):
        db = pydb.foreigndb.ForeignDB(":memory:", schema_path, friend_id, enable_db_sync=False)
        return db

    file_store = None
    db = pydb.maindb.MainDB(local_db, friends_db, merge_db, file_store, build_foreign_db, index_server)

    logger.info("DBs initialized")
    return db


author_doc_1 = {
    "name": "some body",
    "fusion_sources": [],
    "fidelity": 60.0,
    "guid": "aaaaaaaaaabbbbbbbbbbccccccccccd1",
    "date_of_birth": "2014-01-01",
    "date_of_death": "2014-01-02"
}

author_doc_2 = {
    "name": "another body",
    "fusion_sources": [],
    "fidelity": 80.0,
    "guid": "aaaaaaaaaabbbbbbbbbbccccccccccd2",
    "date_of_birth": "2015-01-01",
    "date_of_death": "2015-01-02"
}


class TestAuthorFusion(unittest.TestCase):
    def setUp(self):
        self.main_db = build_main_db_memory_only(get_schema_dir())
        self.main_db.load_own_author_document(author_doc_1)
        self.main_db.load_own_author_document(author_doc_2)

        self.assertEqual(len(self.main_db.get_all_authors()), 2)

    def test_fusing_two_authors_results_in_having_one_less_author(self):
        author_doc_2b = copy.deepcopy(author_doc_2)
        author_doc_2b['fusion_sources'] = [{'fidelity': 60,
                                            'source_guid': author_doc_1['guid']}]

        self.main_db.load_own_author_document(author_doc_2b)

        self.assertEqual(len(self.main_db.get_all_authors()), 1)

    def test_fusing_two_authors_results_the_remaining_author_keeping_its_name(self):
        author_doc_2b = copy.deepcopy(author_doc_2)
        author_doc_2b['fusion_sources'] = [{'fidelity': 60,
                                            'source_guid': author_doc_1['guid']}]

        self.main_db.load_own_author_document(author_doc_2b)

        all_authors = self.main_db.get_all_authors()
        author = all_authors[0]
        self.assertEqual(author['name'], 'another body')

    def test_fusing_two_authors_results_the_remaining_author_keeping_its_name_even_if_fidelity_smaller_than_source(self):
        author_doc_2b = copy.deepcopy(author_doc_2)
        author_doc_2b['fidelity'] = 45
        author_doc_2b['fusion_sources'] = [{'fidelity': 60,
                                            'source_guid': author_doc_1['guid']}]

        self.main_db.load_own_author_document(author_doc_2b)

        all_authors = self.main_db.get_all_authors()
        author = all_authors[0]
        self.assertEqual(author['name'], 'another body')
        print author


if __name__ == '__main__':
    unittest.main()