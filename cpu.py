"""CPU functionality."""

import sys

HLT = 0b00000001
LDI = 0b10000010
PRN = 0b01000111
MUL = 0b10100010
POP = 0b01000110 
PUSH = 0b01000101
RET = 0b00010001
CALL = 0b01010000
JMP = 0b01010100
JEQ = 0b01010101 
JNE = 0b01010110 
CMP = 0b10100111

class CPU:
    """Main CPU class."""

    def __init__(self):
        """Construct a new CPU."""
        self.ram = [0] * 256
        self.reg = [0] * 8
        self.pc = 0               
        self.fl = 6               
        self.SP = 7          

    def load(self, program):
        """Load a program into memory."""

        address = 0

        try:
            with open(program) as file:
                for line in file:
                    comment_split = line.split('#')
                    maybe_command = comment_split[0].strip()

                    if maybe_command == '':
                        continue
                    self.ram[address] = int(maybe_command, 2)

                    address +=1

        except FileNotFoundError:
            print('File does not exist')

    def alu(self, op, reg_a, reg_b):
        """ALU operations."""

        if op == "ADD":
            self.reg[reg_a] += self.reg[reg_b]
        #elif op == "SUB": etc
        if op == "MUL":
            self.reg[reg_a] *= self.reg[reg_b]
        if op == "CMP":
            result = 0
            if self.reg[reg_a] == self.reg[reg_b]:
                result = 1
            elif self.reg[reg_a] > self.reg[reg_b]:
                result = 2
            elif self.reg[reg_a] < self.reg[reg_b]:
                result = 4

            self.reg[self.fl] = result
            self.pc += 3
        else:
            raise Exception("Unsupported ALU operation")

    def trace(self):
        """
        Handy function to print out the CPU state. You might want to call this
        from run() if you need help debugging.
        """

        print(f"TRACE: %02X | %02X %02X %02X |" % (
            self.pc,
            #self.fl,
            #self.ie,
            self.ram_read(self.pc),
            self.ram_read(self.pc + 1),
            self.ram_read(self.pc + 2)
        ), end='')

        for i in range(8):
            print(" %02X" % self.reg[i], end='')

        print()

    def run(self):
        """Run the CPU."""
        # Instruction Register
        running = True

        while running:

            ir = self.ram[self.pc]   
            operand_a = self.ram_read(self.pc+1)
            operand_b = self.ram_read(self.pc+2)

            if ir == LDI:
                print(f'LDI ir is: {ir}')
                self.reg[operand_a] = operand_b
                print(f'reg is now: {self.reg[operand_a]}')
                self.pc += 3

            elif ir == PRN:
                print(f'PRN ir is: {ir}')
                value = self.reg[operand_a]
                print(value)
                self.pc += 2

            elif ir == MUL:
                self.alu("MUL", operand_a, operand_b)
                self.pc += 3
                
            elif ir == CMP:
                self.alu("CMP", operand_a, operand_b)
                self.pc += 3

            elif ir == PUSH:
                # decrement the stack pointer
                self.reg[7] -= 1

                # get what is in the register
                reg_address = self.ram[self.pc + 1]
                value = self.reg[reg_address]

                # store it at that point in the stack
                self.SP = self.reg[7]
                self.ram[self.SP] = value

                self.pc += 2

            elif ir == POP:
                # Copy the value from the address pointed to by SP to the given register.
                self.SP = self.reg[7]
                value = self.ram[self.SP]
                target_reg_address = self.ram[self.pc + 1]
                self.reg[target_reg_address] = value

                # Increment SP
                self.reg[7] += 1

                self.pc += 2
            
            elif ir == CALL:
                self.reg[self.SP] -= 1
                self.ram[self.reg[self.SP]] = self.pc + 2
                self.pc = self.reg[operand_a]

            elif ir == RET:
                value = self.ram[self.reg[self.SP]]
                self.pc = value

                self.reg[self.SP] += 1
            
            elif ir == JMP:
                self.pc = self.reg[operand_a]

            elif ir == JEQ:
                if self.reg[self.fl] == 1:
                    self.pc = self.reg[operand_a]
                else:
                    self.pc += 2

            elif ir == JNE:
                if self.reg[self.fl] != 1:
                    self.pc = self.reg[operand_a]
                else:
                    self.pc += 2

            elif ir == HLT:
                print(f'Entered HLT. CPU ending...')
                running = False

    def ram_read(self, MAR):
        return self.ram[MAR]

    def ram_write(self, MAR, MDR):
        self.ram[MAR] = MDR
    