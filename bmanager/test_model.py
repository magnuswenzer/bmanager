import unittest
from bmanager import utils

from bmanager.config import ModelConfig
from bmanager.model import Model

CONFIG_FILE_PATH = 'default_model_config.json'


class TestModel(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.config = ModelConfig(CONFIG_FILE_PATH, activate='test_local')
        print(cls.config.get('databases')[0].get('initiation').get('location'))
        cls.model = Model(config=cls.config)
        cls.model.login()

        cls._fill_database()

    @classmethod
    def tearDownClass(cls):
        pass

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def _fill_database(self):
        projects = [dict(project_name='test project 1'),
                    dict(project_name='test project 2'),
                    dict(project_name='test project 3')]
        for proj in projects:
            self.model.add_to_table('project', **proj)


if __name__ == '__main__':
    # c = TestModel()
    unittest.main()

