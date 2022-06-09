import unittest
from notion import Notion


class NotionTestCase(unittest.TestCase): 
    # construct a Notion object
    base_info = {
        "token": 'secret_OiAX1w2anZHHXDhzkozBIJd5PWLJMaoy04ZsM1vix48',
        "database_id": '46aadc437ddd4017a2c4508801091956',
        "calendar_id": '10c551072e564b4580b5cc697c73ce2f',
        "review_cycle": [2, 7, 14]
    }
    notion = Notion(**base_info)

    # test compute_date
    def test_compute_date(self):
        dates = self.notion.compute_date()
        self.assertIsInstance(dates, dict)

    # test readCalendar
    def test_readCalendar(self):
        result = self.notion.readCalendar()
        self.assertIsInstance(result, dict)

    # readBlock
    def test_readBlock1(self):
        block_id1 = "fb9e45dd-03f4-414e-937f-642e3ebe4349"
        res1 = self.notion.readBlock(block_id1)
        self.assertIsInstance(res1, str)

    def test_readBlock2(self):
        block_id2 = "0309f75a-26b0-4755-b8c8-7744b2d75142"
        res2 = self.notion.readBlock(block_id2, job="find_num")
        self.assertIsInstance(res2, int)


if __name__ == '__main__':
    unittest.main()
