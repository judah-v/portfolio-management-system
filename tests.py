import unittest
import main

class TestApp(unittest.TestCase):
    def setUp(self):
        self.conn = main.mc.connect(**main.DB_CONFIG)
        self.app = main.App()
    
    def tearDown(self):
        return self.conn.close()
    
    def test_app_creates_new_tkwindow(self):
        return self.assertIs(type(self.app.home.win), type(main.tk.Tk()))
