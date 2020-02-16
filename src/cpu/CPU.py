#  The GameBoy uses a computer chip similar to an Intel
#  8080. It contains all of the instructions of an 8080
#  except there are no exchange instructions. In many
#  ways the processor is more similar to the Zilog Z80
#  processor. Compared to the Z80, some instructions
#  have been added and some have been taken away.


from src.bits.eightbit import EightBit
from src.bits.sixteenbit import SixteenBit

# For emulating 1Mhz cycle
from threading import Timer
import sched, time

class FlagsRegister:
  def __init__(self):
    self.Z = False;
    self.N = False;
    self.H = False;
    self.C = False;

  def get(self):
    return +(self.Z) << 7 | +(self.N) << 6 | +(self.H) << 5 | +(self.C) << 4;

class Clock:
  def __init__(self):
    self.m = SixteenBit(0)
    self.t = SixteenBit(0)

  def get(self, address):
    return self[address]

  def set(self, address, value):
    self[address].set(value)

class Register:
  def __init__(self):
    self.a = EightBit(0)
    self.b = EightBit(0)
    self.d = EightBit(0)
    self.h = EightBit(0)
    self.f = EightBit(0)
    self.c = EightBit(0)
    self.e = EightBit(0)
    self.l = EightBit(0)
    self.pc = SixteenBit(0) # Program counter
    self.sp = SixteenBit(0) # Stack Pointer

  def get(self, address):
    if isinstance(address, str):
      if len(address) == 1:
        return self[address]
      else:
        return self[address[0]] << 8 | self[address[1]]
    return self[address]

  def set(address, value):
    self[address].set(value)

class RAM:
  def __init__(self):
    # Create a 64k ram, set all address to 0
    self.m = [0] * pow(2, 16)

  # Expecting a byte array from rom
  def addROM(self, rom):
    if (isinstance(rom, list)):
      for i in range(len(rom)):
        self.set(i, bytes(rom[i], encoding='utf8'));
    else:
      print("ROM is not an array of bytes")

  def get(self, address):
    if isinstance(address, str):
      if len(address) == 1:
        return self.m[address]
      else:
        return self.m[address] << 8 | self.m[address + 1]
    return self.m[address]

  def set(self, address, value):
    self.m[address] = SixteenBit(value).get()

  def printMemoryToFile(self, address):
    f = open("ram.txt","a")
    f.write("address: " + str(address) + " | " + str(self.m[address]) + "\n")
    f.close()

class CPU:

  def __init__(self, rom):
    self.ops = [0] * pow(2, 9)
    for op in range(0, pow(2, 9)):
      def f():
        return 1
      self.ops[op] = f
    self.rom = rom
    self.r = Register()
    self.c = Clock()
    self.f = FlagsRegister()
    self.reset()
    self.running = 1

  def reset(self):
    self.r.pc.set(0x100)
    self.ram = RAM()
    self.populate8BitLoads()

  def start(self):
    self.ram.addROM(self.rom)
    self.cycle()

  def cycle(self):
    if self.running:
      self.ops[self.ram.get(self.r.pc.get())]()
      self.ram.printMemoryToFile(0xFF01)
      self.ram.printMemoryToFile(0xFF02)
      # INCREASE pc by 1 every cycle
      self.r.pc.set(self.r.pc.get() + 1)
      Timer(1 / 100, self.cycle).start()

  def de(opcode):
    # TODO: Find opcode destructure
    return 0

  def get8(self):
    return self.ram.get(self.r.pc.get());

  def get16(self):
    return self.ram.get(self.r.pc.get()) << 8 | self.ram.get(self.r.pc.get() + 1)

# 8-Bit Loads
  def populate8BitLoads(self):

    def op_0x00():
      v = 1 + 1

    self.ops[0] = op_0x00

    LDnn_n = [
      (0x06, "b", 8),
      (0x0E, "c", 8),
      (0x16, "d", 8),
      (0x1E, "e", 8),
      (0x26, "h", 8),
      (0x2E, "l", 8),
    ]

    for op in LDnn_n:
      op_code, nn, cycles = op
      def f(op_code, nn, cycles):
        # Description:
        #   Put value nn into n.
        # Use with:
        #   nn = B,C,D,E,H,L,BC,DE,HL,SP
        #   n = 8 bit immediate value
        self.ram.set(self.get8(), self.r[nn])
        self.clock.c.set(self.clock.c + cycles)
        f.__name__ = op_code
      self.ops[op_code] = f

    LDr1_r2 = [
      (0x7f, 'a', 'a', 4),(0x78, 'a', 'b', 4),(0x79, 'a', 'c', 4),(0x7a, 'a', 'd', 4),
      (0x7b, 'a', 'e', 4),(0x7c, 'a', 'h', 4),(0x7d, 'a', 'l', 4),(0x7e, 'a', 'hl', 8),
      (0x40, 'b', 'b', 4),(0x41, 'b', 'c', 4),(0x42, 'b', 'd', 4),(0x43, 'b', 'e', 4),
      (0x44, 'b', 'h', 4),(0x45, 'b', 'l', 4),(0x46, 'b', 'hl', 8),(0x48, 'c', 'b', 4),
      (0x49, 'c', 'c', 4),(0x4a, 'c', 'd', 4),(0x4b, 'c', 'e', 4),(0x4c, 'c', 'h', 4),
      (0x4d, 'c', 'l', 4),(0x4e, 'c', 'hl', 8),(0x50, 'd', 'b', 4),(0x51, 'd', 'c', 4),
      (0x52, 'd', 'd', 4),(0x53, 'd', 'e', 4),(0x54, 'd', 'h', 4),(0x55, 'd', 'l', 4),
      (0x56, 'd', 'hl', 8),(0x58, 'e', 'b', 4),(0x59, 'e', 'c', 4),(0x5a, 'e', 'd', 4),
      (0x5b, 'e', 'e', 4),(0x5c, 'e', 'h', 4),(0x5d, 'e', 'l', 4),(0x5e, 'e', 'hl', 8),
      (0x60, 'h', 'b', 4),(0x61, 'h', 'c', 4),(0x62, 'h', 'd', 4),(0x63, 'h', 'e', 4),
      (0x64, 'h', 'h', 4),(0x65, 'h', 'l', 4),(0x66, 'h', 'hl', 8),(0x68, 'l', 'b', 4),
      (0x69, 'l', 'c', 4),(0x6a, 'l', 'd', 4),(0x6b, 'l', 'e', 4),(0x6c, 'l', 'h', 4),
      (0x6d, 'l', 'l', 4),(0x6e, 'l', 'hl', 8),(0x70, 'hl', 'b', 8),(0x71, 'hl', 'c', 8),
      (0x72, 'hl', 'd', 8),(0x73, 'hl', 'e', 8),(0x74, 'hl', 'h', 8),(0x75, 'hl', 'l', 8),
      (0x36, 'hl', 'n', 12)
    ]

    for op in LDr1_r2:
      op_code, r1, r2, cycles = op
      def f(op_code, r1, r2, cycles):
        # Description:
        #   Put value r2 into r1.
        # Use with:
        #   r1,r2 = A,B,C,D,E,H,L,(HL)
        self.r.set(r1, self.r.get(r2))
        self.clock.c.set(self.clock.c + cycles)
        f.__name__ = op_code
      self.ops[op_code] = f

    LDA_n = [
      (0x7f,"a","a",4), (0x78,"a","b",4), (0x79,"a","c",4), (0x7a,"a","d",4),
      (0x7b,"a","e",4), (0x7c,"a","h",4), (0x7d,"a","l",4), (0x0a,"a","bc",8),
      (0x1a,"a","de",8), (0x7e,"a","hl",8), (0xfa,"a","nn",16), (0x3e,"a","#",8)
    ]

    for op in LDA_n:
      op_code, a, n, cycles = op
      def f(op_code, a, n, cycles):
        # Description:
        #   Put value n into A.
        # Use with:
        #   n = A,B,C,D,E,H,L,(BC),(DE),(HL),(nn),#
        #   nn = two byte immediate value. (LS byte first.)
        if n == "nn":
          self.r.set(a, self.get16())
        elif n == "#":
          self.r.set(a, self.get8())
        else:
          self.r.set(a, self.r.get(n))
        self.clock.c.set(self.clock.c + cycles)
      self.ops[op_code] = f

    LDn_A = [
      (0x7f,"a","a",4),(0x47,"b","a",4),(0x4f,"c","a",4),(0x57,"d","a",4),
      (0x5f,"e","a",4),(0x67,"h","a",4),(0x6f,"l","a",4),(0x02,"bc","a",8),
      (0x12,"de","a",8),(0x77,"hl","a",8),(0xea,"nn","a",16)
    ]

    for op in LDn_A:
      op_code, n, a, cycles = op
      def f(op_code, n, a, cycles):
        # Description:
        #   Put value A into n.
        # Use with:
        #   n = A,B,C,D,E,H,L,(BC),(DE),(HL),(nn)
        #   nn = two byte immediate value. (LS byte first.)
        self.r.set(n, self.r.get(a))
        self.clock.c.set(self.clock.c + cycles)
      self.ops[op_code] = f

    LDC_A = [
      (0xE2, "c", "a", 8)
    ]

    for op in LDn_A:
      op_code, c, a, cycles = op
      def f(op_code, c, a, cycles):
        # Description:
        # Put value at address $FF00 + register C into A.
        # Same as: LD A,($FF00+C)
        self.r.set(self.ram.get(0xFF) + self.r.get(c), a)
        self.clock.c.set(self.clock.c + cycles)
      self.ops[op_code] = f

    LDA_C = [
      (0xF2, "a", "c", 8)
    ]

    for op in LDn_A:
      op_code, a, c, cycles = op
      # Description:
      # Put value at address $FF00 + register C into A.
      # Same as: LD A,($FF00+C)
      def f(op_code, a, c, cycles):
        self.r.set(a, self.ram.get(0xFF) + self.r.get(c))
        self.clock.c.set(self.clock.c + cycles)
      self.ops[op_code] = f

    LDA_HL = [
      (0x3A, "a", "hl", 8)
    ]

    for op in LDA_HL:
      op_code, a, hl, cycles = op
      def f(op_code, a, hl, cycles):
        self.r["l1"].set(self.r["a"].get() & 0x00FF)
        self.r["h"].set(self.r["a"].get() << 4)
        self.clock.c.set(self.clock.c + cycles)
      self.ops[op_code] = f

    LDA_HL = [
      (0x32, "hl", "a", 8)
    ]

    for op in LDA_HL:
      op_code, a, hl, cycles = op
      def f(op_code, a, hl, cycles):
        self.r["a"].set(self.r["h"].get() << 4 | self.r["l"].get())
        self.clock.c.set(self.clock.c + cycles)
      self.ops[op_code] = f

    # Put value at address HL into A. Increment HL
    LDIA_HL = [
      (0x2a, "hl", "a", 8)
    ]

    # Put A into memory address HL. Increment HL.
    LDIHL_A = [
      (0x22, "a", "hl", 8)
    ]

    # Put A into memory address $FF00+n
    # n = one byte immediate value.
    LDHn_A = [
      (0xE0, 12)
    ]

    # Put memory address $FF00+n into A.
    # n = one byte immediate value.
    LDHA_n = [
      (0xF0, 12)
    ]

    # 16 BITS load
    LDn_nn = [
      (0x01, "bc", 12),
      (0x11, "de", 12),
      (0x21, "hl", 12),
      (0x31, "sp", 12)
    ]

    for op in LDn_nn:
      op_code, registers, cycles = op
      nn = self.get16();
      def f(op_code, register, cycles):
        top = nn & 0x00FF
        lower = nn >> 4
        registers = registers.split("")
        self.r[register[0]].set(top)
        self.r[register[1]].set(lower)
        self.clock.c.set(self.clock.c + cycles)
      self.ops[op_code] = f

    # Put HL into Stack Pointer (SP).
    LDSP_HL = [
      (0xF9, "sp", "hl", 8)
    ]

    # Put SP + n effective address into HL
    # n = one byte signed immediate value.
    # Flags affected:
    #  Z - Reset.
    #  N - Reset.
    #  H - Set or reset according to operation.
    #  C - Set or reset according to operation.
    LDHL_SP = [
      (0xF8, "sp", 12)
    ]

    # Put Stack Pointer (SP) at address n.
    # nn = two byte immediate address.
    LDnn_SP = [
      (0x08, "sp", 20)
    ]

    # Push register pair nn onto stack.
    # Decrement Stack Pointer (SP) twice
    PUSHnn = [
      (0xf5, "af", 16),
      (0xc5, "bc", 16),
      (0xd5, "de", 16),
      (0xe5, "hl", 16)
    ]

    # Pop two bytes off stack into register pair nn.
    # Increment Stack Pointer (SP) twice.
    POPnn = [
      (0xf1, "af", 12),
      (0xc1, "bc", 12),
      (0xd1, "de", 12),
      (0xe1, "hl", 12)
    ]

    ##############
    # 8-BIT ALU
    ##############
    # Description:
    #   Add n to A.
    # Use with:
    #   n = A,B,C,D,E,H,L,(HL),#
    # Flags affected:
    #   Z - Set if result is zero.
    #   N - Reset.
    #   H - Set if carry from bit 3.
    #   C - Set if carry from bit 7.
    ADDA_n = [
      (0x87, "a", "a", 4),
      (0x80, "b", "a", 4),
      (0x81, "c", "a", 4),
      (0x82, "d", "a", 4),
      (0x83, "e", "a", 4),
      (0x84, "h", "a", 4),
      (0x85, "l", "a", 4),
      (0x86, "hl", "a", 8),
      (0xc6, "#", "a", 8)
    ]

    #  Description:
    #    Add n + Carry flag to A.
    #  Use with:
    #    n = A,B,C,D,E,H,L,(HL),#
    #  Flags affected:
    #    Z - Set if result is zero.
    #    N - Reset.
    #    H - Set if carry from bit 3.
    #    C - Set if carry from bit 7.
    ADCA_n = [
      (0x8f, "a", "a", 4),
      (0x88, "b", "a", 4),
      (0x89, "c", "a", 4),
      (0x8a, "d", "a", 4),
      (0x8b, "e", "a", 4),
      (0x8c, "h", "a", 4),
      (0x8d, "l", "a", 4),
      (0x8e, "hl", "a", 8),
      (0xce, "#", "a", 8)
    ]

    #  Description:
    #    Subtract n from A.
    #  Use with:
    #    n = A,B,C,D,E,H,L,(HL),#
    #  Flags affected:
    #    Z - Set if result is zero.
    #    N - Set.
    #    H - Set if no borrow from bit 4.
    #    C - Set if no borrow.
    SUBn = [
      (0x97, "a", 4),
      (0x90, "b", 4),
      (0x91, "c", 4),
      (0x92, "d", 4),
      (0x93, "e", 4),
      (0x94, "h", 4),
      (0x95, "l", 4),
      (0x96, "hl", 8),
      (0xd6, "#", 8)
    ]

    #  Description:
    #    Subtract n + Carry flag from A.
    #  Use with:
    #    n = A,B,C,D,E,H,L,(HL),#
    #  Flags affected:
    #    Z - Set if result is zero.
    #    N - Set.
    #    H - Set if no borrow from bit 4.
    #    C - Set if no borrow.
    SBCA_n = [
      (0x9f, "a", "a", 4),
      (0x98, "b", "a", 4),
      (0x99, "c", "a", 4),
      (0x9a, "d", "a", 4),
      (0x9b, "e", "a", 4),
      (0x9c, "h", "a", 4),
      (0x9d, "l", "a", 4),
      (0x9e, "hl", "a", 8)
    ]

    #  Description:
    #    Logically AND n with A, result in A.
    #  Use with:
    #    n = A,B,C,D,E,H,L,(HL),#
    #  Flags affected:
    #    Z - Set if result is zero.
    #    N - Reset.
    #    H - Set.
    #    C - Reset.
    ANDn = [
      (0xa7, "a", "a", 4),
      (0xa0, "a", "b", 4),
      (0xa1, "a", "c", 4),
      (0xa2, "a", "d", 4),
      (0xa3, "a", "e", 4),
      (0xa4, "a", "h", 4),
      (0xa5, "a", "l", 4),
      (0xa6, "a", "hl", 8),
      (0xe6, "e", "#", 8)
    ]

    #  Description:
    #    Logical OR n with register A, result in A.
    #  Use with:
    #    n = A,B,C,D,E,H,L,(HL),#
    #  Flags affected:
    #    Z - Set if result is zero.
    #    N - Reset.
    #    H - Reset.
    #    C - Reset.
    ORn = [
      (0xb7, "a", 4),
      (0xb0, "b", 4),
      (0xb1, "c", 4),
      (0xb2, "d", 4),
      (0xb3, "e", 4),
      (0xb4, "h", 4),
      (0xb5, "l", 4),
      (0xb6, "hl", 8),
      (0xf6, "#", 8)
    ]

    #  Description:
    #    Logical exclusive OR n with register A, result in A.
    #  Use with:
    #    n = A,B,C,D,E,H,L,(HL),#
    #  Flags affected:
    #    Z - Set if result is zero.
    #    N - Reset.
    #    H - Reset.
    #    C - Reset.
    XORn = [
      (0xaf, "a", 4),
      (0xa8, "b", 4),
      (0xa9, "c", 4),
      (0xaa, "d", 4),
      (0xab, "e", 4),
      (0xac, "h", 4),
      (0xad, "l", 4),
      (0xae, "hl", 8),
      (0xee, "#", 8)
    ]

    # Description:
    #   Compare A with n. This is basically an A - n
    #   subtraction instruction but the results are thrown
    #   away.
    # Use with:
    #   n = A,B,C,D,E,H,L,(HL),#
    # Flags affected:
    #   Z - Set if result is zero. (Set if A = n.)
    #   N - Set.
    #   H - Set if no borrow from bit 4.
    #   C - Set for no borrow. (Set if A < n.)
    CPn = [
      (0xbf, "a", 4),
      (0xb8, "b", 4),
      (0xb9, "c", 4),
      (0xba, "d", 4),
      (0xbb, "e", 4),
      (0xbc, "h", 4),
      (0xbd, "l", 4),
      (0xbe, "hl", 8),
      (0xfe, "#", 8)
    ]

    # Description:
    #   Increment register n.
    # Use with:
    #   n = A,B,C,D,E,H,L,(HL)
    # Flags affected:
    #   Z - Set if result is zero.
    #   N - Reset.
    #   H - Set if carry from bit 3.
    #   C - Not affected.
    INCn = [
      (0x3c, "a", 4),
      (0x04, "b", 4),
      (0x0c, "c", 4),
      (0x14, "d", 4),
      (0x1c, "e", 4),
      (0x24, "h", 4),
      (0x2c, "l", 4),
      (0x34, "hl", 12)
    ]

    # Description:
    #   Decrement register n.
    # Use with:
    #   n = A,B,C,D,E,H,L,(HL)
    # Flags affected:
    #   Z - Set if reselt is zero.
    #   N - Set.
    #   H - Set if no borrow from bit 4.
    #   C - Not affected.
    DECn = [
      (0x3d, "a", 4),
      (0x05, "b", 4),
      (0x0d, "c", 4),
      (0x15, "d", 4),
      (0x1d, "e", 4),
      (0x25, "h", 4),
      (0x2d, "l", 4),
      (0x35, "hl", 12)
    ]

    #######
    # 16 BIT Arithmetic
    #######

    # Description:
    #   Add n to HL.
    # Use with:
    #   n = BC,DE,HL,SP
    # Flags affected:
    #   Z - Not affected.
    #   N - Reset.
    #   H - Set if carry from bit 11.
    #   C - Set if carry from bit 15.
    ADDHL_n = [
      (0x09, "HL", "BC" 8),
      (0x19, "HL", "DE" 8),
      (0x29, "HL", "HL" 8),
      (0x39, "HL", "SP" 8)
    ]

    # Description:
    #   Add n to Stack Pointer (SP).
    # Use with:
    #   n = one byte signed immediate value (#).
    # Flags affected:
    #   Z - Reset.
    #   N - Reset.
    #   H - Set or reset according to operation.
    #   C - Set or reset according to operation.

    ADDSP_n = [
      (0xE8, "SP", "#", 16)
    ]

    # Description:
    #   Increment register nn.
    # Use with:
    #   nn = BC,DE,HL,SP
    # Flags affected:
    #   None.
    INCnn = [
      (0x03, "bc", 8),
      (0x13, "de", 8),
      (0x23, "hl", 8),
      (0x33, "sp", 8)
    ]

    # Description:
    #   Decrement register nn.
    # Use with:
    #   nn = BC,DE,HL,SP
    # Flags affected:
    #   None.
    DECnn = [
      (0x0b, "bc", 8),
      (0x1b, "de", 8),
      (0x2b, "hl", 8),
      (0x3b, "sp", 8)
    ]

    # Description:
    #   Swap upper & lower nibles of n.
    # Use with:
    #   n = A,B,C,D,E,H,L,(HL)
    # Flags affected:
    #   Z - Set if result is zero.
    #   N - Reset.
    #   H - Reset.
    #   C - Reset.
    SWAPn = [
      (0x37, 0xcb, "a", 8),
      (0x30, 0xcb, "b", 8),
      (0x31, 0xcb, "c", 8),
      (0x32, 0xcb, "d", 8),
      (0x33, 0xcb, "e", 8),
      (0x34, 0xcb, "h", 8),
      (0x35, 0xcb, "l", 8),
      (0x36, 0xcb, "hl", 16)
    ]

    # Description:
    #   Decimal adjust register A.
    #   This instruction adjusts register A so that the
    #   correct representation of Binary Coded Decimal (BCD)
    #   is obtained.
    # Flags affected:
    #   Z - Set if register A is zero.
    #   N - Not affected.
    #   H - Reset.
    #   C - Set or reset according to operation.
    DAA = [
      (0x27, 4)
    ]

    # Description:
    #   Complement A register. (Flip all bits.)
    # Flags affected:
    #   Z - Not affected.
    #   N - Set.
    #   H - Set.
    #   C - Not affected.
    CPL = [
      (0x2f, 4)
    ]

    # Description:
    #   Complement carry flag.
    #   If C flag is set, then reset it.
    #   If C flag is reset, then set it.
    # Flags affected:
    #   Z - Not affected.
    #   N - Reset.
    #   H - Reset.
    #   C - Complemented.
    CCF = [
      (0x3f, 4)
    ]

    # Description:
    #   Set Carry flag.
    # Flags affected:
    #   Z - Not affected.
    #   N - Reset.
    #   H - Reset.
    #   C - Set.
    SCF = [
      (0x37, 4)
    ]

    # Description:
    #   No operation.
    NOP = [
      (0x00, 4)
    ]

    # Description:
    #   Power down CPU until an interrupt occurs. Use this
    #   when ever possible to reduce energy consumption.
    HALT = [
      (0x76, 4)
    ]

    # Description:
    #   Halt CPU & LCD display until button pressed.
    STOP = [
      (0x10, 0x00, 4)
    ]

    # Description:
    #   This instruction disables interrupts but not
    #   immediately. Interrupts are disabled after
    #   instruction after DI is executed.
    # Flags affected:
    #   None.
    DI = [
      (0xf3, 4)
    ]

    # Description:
    #   Enable interrupts. This intruction enables interrupts
    #   but not immediately. Interrupts are enabled after
    #   instruction after EI is executed.
    # Flags affected:
    #   None.
    EI = [
      (0xfb, 4)
    ]

    ########
    # Rotates & Shifts
    #######

    # Description:
    #   Rotate A left. Old bit 7 to Carry flag.
    # Flags affected:
    #   Z - Set if result is zero.
    #   N - Reset.
    #   H - Reset.
    #   C - Contains old bit 7 data.
    RLCA = [
      (0x07, 4)
    ]

    # Description:
    #   Rotate A left through Carry flag.
    # Flags affected:
    #   Z - Set if result is zero.
    #   N - Reset.
    #   H - Reset.
    #   C - Contains old bit 7 data.
    RLA = [
      (0x17, 4)
    ]

    # Description:
    #   Rotate A right. Old bit 0 to Carry flag.
    # Flags affected:
    #   Z - Set if result is zero.
    #   N - Reset.
    #   H - Reset.
    #   C - Contains old bit 0 data.
    RRCA = [
      (0x0f, 4)
    ]

    # Description:
    #   Rotate A right through Carry flag.
    # Flags affected:
    #   Z - Set if result is zero.
    #   N - Reset.
    #   H - Reset.
    #   C - Contains old bit 0 data.
    RRA = [
      (0x1f, 4)
    ]

    # Description:
    #   Rotate n left. Old bit 7 to Carry flag.
    # Use with:
    #   n = A,B,C,D,E,H,L,(HL)
    # Flags affected:
    #   Z - Set if result is zero.
    #   N - Reset.
    #   H - Reset.
    #   C - Contains old bit 7 data.
    RLCn = [
      (0xcb, 0x07, "a", 8),
      (0xcb, 0x00, "b", 8),
      (0xcb, 0x01, "c", 8),
      (0xcb, 0x02, "d", 8),
      (0xcb, 0x03, "e", 8),
      (0xcb, 0x04, "h", 8),
      (0xcb, 0x05, "l", 8),
      (0xcb, 0x06, "hl", 16)
    ]

    # Description:
    #   Rotate n left through Carry flag.
    # Use with:
    #   n = A,B,C,D,E,H,L,(HL)
    # Flags affected:
    #   Z - Set if result is zero.
    #   N - Reset.
    #   H - Reset.
    #   C - Contains old bit 7 data.
    RLn = [
      (0xcb, 0x17, "a", 8),
      (0xcb, 0x10, "b", 8),
      (0xcb, 0x11, "c", 8),
      (0xcb, 0x12, "d", 8),
      (0xcb, 0x13, "e", 8),
      (0xcb, 0x14, "h", 8),
      (0xcb, 0x15, "l", 8),
      (0xcb, 0x16, "hl", 16)
    ]

    # Description:
    #   Rotate n right. Old bit 0 to Carry flag.
    # Use with:
    #   n = A,B,C,D,E,H,L,(HL)
    # Flags affected:
    #   Z - Set if result is zero.
    #   N - Reset.
    #   H - Reset.
    #   C - Contains old bit 0 data.
    RRCn = [
      (0xcb, 0x0f, "a", 8),
      (0xcb, 0x08, "b", 8),
      (0xcb, 0x09, "c", 8),
      (0xcb, 0x0a, "d", 8),
      (0xcb, 0x0b, "e", 8),
      (0xcb, 0x0c, "h", 8),
      (0xcb, 0x0d, "l", 8),
      (0xcb, 0x0e, "hl", 16)
    ]

    # Description:
    #   Rotate n right through Carry flag.
    # Use with:
    #   n = A,B,C,D,E,H,L,(HL)
    # Flags affected:
    #   Z - Set if result is zero.
    #   N - Reset.
    #   H - Reset.
    #   C - Contains old bit 0 data.
    RRn = [
      (0xcb, 0x1f, "a", 8),
      (0xcb, 0x18, "b", 8),
      (0xcb, 0x19, "c", 8),
      (0xcb, 0x1a, "d", 8),
      (0xcb, 0x1b, "e", 8),
      (0xcb, 0x1c, "h", 8),
      (0xcb, 0x1d, "l", 8),
      (0xcb, 0x1e, "hl", 16)
    ]

    # Description:
    #   Shift n left into Carry. LSB of n set to 0.
    # Use with:
    #   n = A,B,C,D,E,H,L,(HL)
    # Flags affected:
    #   Z - Set if result is zero.
    #   N - Reset.
    #   H - Reset.
    #   C - Contains old bit 7 data.
    SLAn = [
      (0xcb, 0x27, "a", 8),
      (0xcb, 0x20, "b", 8),
      (0xcb, 0x21, "c", 8),
      (0xcb, 0x22, "d", 8),
      (0xcb, 0x23, "e", 8),
      (0xcb, 0x24, "h", 8),
      (0xcb, 0x25, "l", 8),
      (0xcb, 0x26, "hl", 16)
    ]

    # Description:
    #   Shift n right into Carry. MSB doesn't change.
    # Use with:
    #   n = A,B,C,D,E,H,L,(HL)
    # Flags affected:
    #   Z - Set if result is zero.
    #   N - Reset.
    #   H - Reset.
    #   C - Contains old bit 0 data.
    SRAn = [
      (0xcb, 0x2f, "a", 8),
      (0xcb, 0x28, "b", 8),
      (0xcb, 0x29, "c", 8),
      (0xcb, 0x2a, "d", 8),
      (0xcb, 0x2b, "e", 8),
      (0xcb, 0x2c, "h", 8),
      (0xcb, 0x2d, "l", 8),
      (0xcb, 0x2e, "hl", 16)
    ]

    # Description:
    #   Shift n right into Carry. MSB set to 0.
    # Use with:
    #   n = A,B,C,D,E,H,L,(HL)
    # Flags affected:
    #   Z - Set if result is zero.
    #   N - Reset.
    #   H - Reset.
    #   C - Contains old bit 0 data.
    SRLn = [
      (0xcb, 0x3f, "a", 8),
      (0xcb, 0x38, "b", 8),
      (0xcb, 0x39, "c", 8),
      (0xcb, 0x3a, "d", 8),
      (0xcb, 0x3b, "e", 8),
      (0xcb, 0x3c, "h", 8),
      (0xcb, 0x3d, "l", 8),
      (0xcb, 0x3e, "hl", 16)
    ]

    ######
    # Bit Opcodes
    #####
    # Description:
    #   Test bit b in register r.
    # Use with:
    #   b = 0 - 7, r = A,B,C,D,E,H,L,(HL)
    # Flags affected:
    #   Z - Set if bit b of register r is 0.
    #   N - Reset.
    #   H - Set.
    #   C - Not affected.
    BITb_r = [
      (0xcb, 0x47, "a", 8),
      (0xcb, 0x40, "b", 8),
      (0xcb, 0x41, "c", 8),
      (0xcb, 0x42, "d", 8),
      (0xcb, 0x43, "e", 8),
      (0xcb, 0x44, "h", 8),
      (0xcb, 0x45, "l", 8),
      (0xcb, 0x46, "hl", 16)
    ]

    # Description:
    #   Set bit b in register r.
    # Use with:
    #   b = 0 - 7, r = A,B,C,D,E,H,L,(HL)
    # Flags affected:
    #   None.
    SETb_r = [
      (0xcb, 0xc7, "a", 8),
      (0xcb, 0xc0, "b", 8),
      (0xcb, 0xc1, "c", 8),
      (0xcb, 0xc2, "d", 8),
      (0xcb, 0xc3, "e", 8),
      (0xcb, 0xc4, "h", 8),
      (0xcb, 0xc5, "l", 8),
      (0xcb, 0xc6, "hl", 16)
    ]

    # Description:
    #   Reset bit b in register r.
    # Use with:
    #   b = 0 - 7, r = A,B,C,D,E,H,L,(HL)
    # Flags affected:
    #   None.
    RESb_r = [
      (0xcb, 0x87, "a", 8),
      (0xcb, 0x80, "b", 8),
      (0xcb, 0x81, "c", 8),
      (0xcb, 0x82, "d", 8),
      (0xcb, 0x83, "e", 8),
      (0xcb, 0x84, "h", 8),
      (0xcb, 0x85, "l", 8),
      (0xcb, 0x86, "hl", 16)
    ]

    # Description:
    #   Jump to address nn.
    # Use with:
    #   nn = two byte immediate value. (LS byte first.)
    JPnn = [
      (0xc3, 12)
    ]

    # Description:
    #   Jump to address n if following condition is true:
    #   cc = NZ, Jump if Z flag is reset.
    #   cc = Z, Jump if Z flag is set.
    #   cc = NC, Jump if C flag is reset.
    #   cc = C, Jump if C flag is set.
    # Use with:
    #   nn = two byte immediate value. (LS byte first.)
    JPcc_nn = [
      (0xc2, "nz", 12),
      (0xca, "z", 12),
      (0xd2, "nc", 12),
      (0xda, "c", 12)
    ]

    # Description:
    #  Jump to address contained in HL.
    JPHL = [
      (0xe9, 4)
    ]

    # Description:
    #   Add n to current address and jump to it.
    # Use with:
    #   n = one byte signed immediate value
    JRn = [
      (0x18, 8)
    ]

    # Description:
    #   If following condition is true then add n to current
    #   address and jump to it:
    # Use with:
    #   n = one byte signed immediate value
    #   cc = NZ, Jump if Z flag is reset.
    #   cc = Z, Jump if Z flag is set.
    #   cc = NC, Jump if C flag is reset.
    #   cc = C, Jump if C flag is set.
    JRcc_n = [
      (0x20, "nz", 8),
      (0x28, "z", 8),
      (0x30, "nc", 8),
      (0x38, "c", 8)
    ]

    # Description:
    #   Push address of next instruction onto stack and then
    #   jump to address nn.
    # Use with:
    #   nn = two byte immediate value. (LS byte first.)
    CALLnn = [
      (0xcd, 12)
    ]

    # Description:
    #   Call address n if following condition is true:
    #   cc = NZ, Call if Z flag is reset.
    #   cc = Z, Call if Z flag is set.
    #   cc = NC, Call if C flag is reset.
    #   cc = C, Call if C flag is set.
    # Use with:
    #   nn = two byte immediate value. (LS byte first.)
    CALLcc_nn = [
      (0xc4, "nz", 12),
      (0xcc, "z", 12),
      (0xd4, "nc", 12),
      (0xdc, "c", 12)
    ]

    # Description:
    #   Push present address onto stack.
    #   Jump to address $0000 + n.
    # Use with:
    #   n = $00,$08,$10,$18,$20,$28,$30,$38
    RSTn = [
      (0xc7, 00, 32),
      (0xcf, 08, 32),
      (0xd7, 10, 32),
      (0xdf, 18, 32),
      (0xe7, 20, 32),
      (0xef, 28, 32),
      (0xf7, 20, 32),
      (0xff, 38, 32)
    ]