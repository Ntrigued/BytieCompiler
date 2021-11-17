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
    _.if_else(bool_cond=_.is_equal('x', 'x'),
            true_block=[
                  _.interpreter_debug('x == x'),
                  _.if_else(bool_cond=_.is_greater('y', 'x'),
                            true_block=[
                                _.interpreter_debug('ERROR. y > x'),
                            ],
                            false_block=[
                                _.interpreter_debug('not y > x')
                            ],
                  ),
            ],
            false_block=[
                 _.interpreter_debug('ERROR. x != x')
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