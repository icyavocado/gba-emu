class SixteenBit:

  def __init__(self, bit):
    self.bit = self._wrapOver(bit)

  def get(self):
    return self.bit

  def set(self, newBit):
    self._wrapOver(newBit)

  def _wrapOver(self, newBit):
    if isinstance(newBit, bytes):
      newBit = int(newBit, 16)
    if newBit >= 0 and newBit <= 65535:
      return newBit
    else:
      return newBit % 65536
