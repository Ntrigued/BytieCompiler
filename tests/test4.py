from CfgGenerator import CfgGenerator

_ = CfgGenerator()
_.program = [
    _.set_var('x', 3),
    _.set_var('y', -10),
    _.if_else(bool_cond=_.is_greater('x', 1),
              true_block=[
                  _.set_var('y', 'x'),
                  _.set_var('a', 'y'),
                 _.set_var('b', 'y'),
              ],
              false_block=[
                  _.set_var('y', 123),
                  _.set_var('a', 'y'),
                  _.set_var('c', 'y'),
              ]),
    _.set_var('a', 'x'),
]