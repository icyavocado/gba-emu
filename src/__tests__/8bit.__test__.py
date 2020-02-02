import unittest
from src.bits.eightbit import EightBit

class TestNumberMethods(unittest.TestCase):

  def test_0(self):
    number = EightBit(0)
    bit = number.get()
    self.assertEqual(bit, 0)

  def test_255(self):
    number = EightBit(255)
    bit = number.get()
    self.assertEqual(bit, 255)

  def test_256(self):
    number = EightBit(256)
    bit = number.get()
    self.assertEqual(bit, 0)

  def test_765(self):
    number= EightBit(765)
    bit = number.get()
    self.assertEqual(bit, 253)

  def test_1276(self):
    number= EightBit(1276)
    bit = number.get()
    self.assertEqual(bit, 252)

if __name__ == '__main__':
  unittest.main()