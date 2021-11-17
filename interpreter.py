class Interpreter:
    def __init__(self):
        self.labels = {}
        self.registers = {}

    def interpret(self, bytecode):
        self.setup_labels(bytecode)

        program_counter = 0
        while program_counter < len(bytecode):
            instr = bytecode[program_counter]

            cmd = instr[0]
            if cmd == 'ADD':
                dest, src1, src2 = instr[1:4]
                self.registers[dest] = self.registers[src1] + self.registers[src2]
            elif cmd == 'CHK_JMP':
                reg_id, label = instr[1], instr[2]
                if self.registers[reg_id]:
                    program_counter = self.labels[label]
            elif cmd == 'CMP_EQ':
                dest, src1, src2 = instr[1:4]
                if self.registers[src1] == self.registers[src2]:
                    self.registers[dest] = 1
                else:
                    self.registers[dest] = 0
            elif cmd == 'CMP_GT':
                dest, src1, src2 = instr[1:4]
                if self.registers[src1] > self.registers[src2]:
                    self.registers[dest] = 1
                else:
                    self.registers[dest] = 0
            elif cmd == 'DEBUG_PRINT':
                output = instr[1]
                print(output)
            elif cmd == 'LABEL':
                pass
            elif cmd == 'JMP':
                label = instr[1]
                program_counter = self.labels[label]
            elif cmd == 'SET':
                dest = instr[1]
                val = instr[2]
                self.registers[dest] = val
            program_counter += 1

    def setup_labels(self, bytecode):
        for instr_idx in range(len(bytecode)):
            instr = bytecode[instr_idx]
            if instr[0] == 'LABEL':
                self.labels[instr[1]] = instr_idx