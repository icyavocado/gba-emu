import os
import struct
from src.cpu.CPU import CPU

def loadFile(pathToFile):
  ROOT_DIR = os.path.abspath(os.curdir)
  file = open(ROOT_DIR + pathToFile, "rb")

  fileData = []

  if file.mode == "rb":
    byte = file.read(1)
    while byte:
      fileData.append(bytes(byte).hex())
      byte = file.read(1)
  file.close()
  return fileData


def main():
  gameBoyCPU = CPU(loadFile("/roms/cpu_instrs/cpu_instrs.gb"))
  gameBoyCPU.start()

if __name__ == '__main__':
  main()