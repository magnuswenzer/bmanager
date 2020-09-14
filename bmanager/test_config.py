import unittest
from bmanager import utils

from bmanager.config import ModelConfig
from bmanager.model import Model

from bmanager import utils

CONFIG_FILE_PATH = 'default_model_config.json'


class TestModel(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.config_data = utils.load_json(CONFIG_FILE_PATH)

    @classmethod
    def tearDownClass(cls):
        pass

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_active_database(self):
        all_active = []
        for database in self.config_data.get('databases'):
            if database.get('activated'):
                all_active.append(database.get('name'))
        self.assertEqual(len(all_active), 1)

    def test_primary_key(self):
        has_id = []
        is_activated = []
        for table in self.config_data.get('tables'):
            if not table.get('activated'):
                continue
            has_key_id = False
            for col in table.get('columns'):
                if col.get('name') == 'id':
                    has_key_id = True
                    is_activated.append(col.get('activated', False))
            has_id.append(has_key_id)

        


if __name__ == '__main__':
    # c = TestModel()
    unittest.main()

