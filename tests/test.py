import unittest
import PR.core


class dummyTest(unittest.TestCase):
    def test_reverse(self):
        self.assertEqual(PR.core.reverse("Hey"),"yeH")
    def test_sqr(self):
        self.assertFalse(PR.core.square("Num"))

if __name__ == '__main__':
    unittest.main()