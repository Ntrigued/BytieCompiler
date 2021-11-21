from test4 import _

from pprint import pprint

from bytecode_generator import BytecodeGenerator
from optimizations.cfg.propagate_constants import  PropagateConstants
from interpreter import Interpreter

_.print()

print('\n')

pc = PropagateConstants()
pc.run_pass(_.program)
_.print()

#bg = BytecodeGenerator()
#bytecode = bg.generate_bytecode(_.program)
#pprint(bytecode)

#intrptr = Interpreter()
#intrptr.interpret(bytecode, max_instructions=10000)