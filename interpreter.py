class Interpreter:
    def __init__(self):
        self.program_counter = 0
        self.labels = {}
        self.registers = {}

    def interpret(self, bytecode, max_instructions=False):
        self.setup_labels(bytecode)
        instrs_run = 0
        while self.program_counter < len(bytecode):
            if max_instructions:
                if instrs_run > max_instructions:
                    print("Hit max # of instructions to execute")
                    break
            self.interpret_instr(bytecode[self.program_counter])
            instrs_run += 1
        print("{} instructions were run in that execution".format(instrs_run))
        self.program_counter = 0

    def interpret_instr(self, instr):
            cmd = instr[0]
            if cmd == 'ADD':
                dest, src1, src2 = instr[1:4]
                self.registers[dest] = self.registers[src1] + self.registers[src2]
            elif cmd == 'CHK_JMP':
                reg_id, label = instr[1], instr[2]
                if self.registers[reg_id]:
                    self.program_counter = self.labels[label]
            elif cmd == 'NCHK_JMP':
                reg_id, label = instr[1], instr[2]
                if not self.registers[reg_id]:
                    self.program_counter = self.labels[label]
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
                self.program_counter = self.labels[label]
            elif cmd == 'SET':
                dest = instr[1]
                val = instr[2]
                if isinstance(val, str):
                    val = self.registers[val]
                self.registers[dest] = val
            self.program_counter += 1

    def setup_labels(self, bytecode):
        for instr_idx in range(len(bytecode)):
            instr = bytecode[instr_idx]
            if instr[0] == 'LABEL':
                self.labels[instr[1]] = instr_idx