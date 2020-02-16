class EightBit:

  def __init__(self, bit):
    self.bit = self._wrapOver(bit)

  def get(self):
    return self.bit

  def set(self, newBit):
    self._wrapOver(newBit)

  def _wrapOver(self, newBit):
    if isinstance(newBit, bytes):
      newBit = int(newBit, 8)
    if newBit >= 0 and newBit <= 255:
      return bytes(newBit)
    else:
      return bytes(int(newBit) % 256)
