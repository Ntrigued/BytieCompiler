from pprint import pprint

from CfgGenerator import CfgGenerator
from bytecode_generator import BytecodeGenerator
from interpreter import Interpreter

_ = CfgGenerator()
_.program = [
    _.set_var('x', 3),
    _.set_var('y', -1),
    _.set_var('z',
              _.calc('+', 'x', 'y')
    ),
_   .if_else(bool_cond=_.is_greater('x', 'z'),
            true_block=[
                  _.interpreter_debug('Condition succeeded')
            ],
            false_block=[
                 _.interpreter_debug('Condition failed')
            ]
    ),
    _.interpreter_debug('Execution Completed')
]
_.print()

bg = BytecodeGenerator()
bytecode = bg.generate_bytecode(_.program)
pprint(bytecode)

intrptr = Interpreter()
intrptr.interpret(bytecode)