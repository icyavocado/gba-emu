import unittest
from sixteenbit import SixteenBit

class TestNumberMethods(unittest.TestCase):

  def test_0(self):
    number = SixteenBit(0)
    bit = number.get()
    self.assertEqual(bit, 0)

  def test_65535(self):
    number = SixteenBit(65535)
    bit = number.get()
    self.assertEqual(bit, 65535)

  def test_65536(self):
    number = SixteenBit(65536)
    bit = number.get()
    self.assertEqual(bit, 0)

  def test_65537(self):
    number= SixteenBit(65537)
    bit = number.get()
    self.assertEqual(bit, 1)

  def test_196611(self):
    number= SixteenBit(196611)
    bit = number.get()
    self.assertEqual(bit, 3)

if __name__ == '__main__':
  unittest.main()