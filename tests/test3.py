from pprint import pprint

from CfgGenerator import CfgGenerator
from bytecode_generator import BytecodeGenerator
from interpreter import Interpreter

_ = CfgGenerator()
_.program = [
    #_.set_var('x', 3),
    _.set_var('y', -1),
    _.while_loop(bool_cond=_.is_greater(300, 'y'),
                 code_block=[
                     _.set_var('y',
                               _.calc('+', 'y', 1)
                               ),
                     _.interpreter_debug('Run through while loop')
                 ],
    ),

    _.interpreter_debug('Execution Completed')
]
_.print()

bg = BytecodeGenerator()
bytecode = bg.generate_bytecode(_.program)
pprint(bytecode)

intrptr = Interpreter()
intrptr.interpret(bytecode, max_instructions=10000)