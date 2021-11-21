from CfgGenerator import CfgGenerator

_ = CfgGenerator()
_.program = [
    #_.set_var('x', 3),
    _.set_var('y', -1),
    _.while_loop(bool_cond=_.is_greater(300, 'y'),
                 code_block=[
                     _.set_var('y',
                               _.calc('+', 'y', -13)
                               ),
                     _.interpreter_debug('Run through while loop')
                 ],
    ),

    _.interpreter_debug('Execution Completed')
]