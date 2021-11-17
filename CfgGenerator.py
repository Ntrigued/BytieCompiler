from CFG import *
from data_types import DataTypes


class CfgGenerator():
    def __init__(self):
        self.symbol_type_table = {}
        self.function_def_table = {}
        self.program = []

    def verify_var_type(self, var_name, expected_type):
        var = self.to_evaluatable(var_name)
        if var.return_type != expected_type:
            raise Exception("Cannot coerce variable '{}' of type {} to {}".format(var_name, self.symbol_type_table[var_name], expected_type))

    def interpreter_debug(self, output):
        return InterpreterDebugNode(output)

    def print(self, initial_indent=0):
        for node in self.program:
            node.print(initial_indent)

    def to_evaluatable(self, var):
        if isinstance(var, Evaluatable):
            return var
        if isinstance(var, list) or isinstance(var, int):
            return Constant(var)
        if isinstance(var, str):
            if var not in self.symbol_type_table.keys():
                raise Exception("Attempting to evaluate an undefined variable '{}'".format(var))
            eval_type = self.symbol_type_table[var]
            return Variable(var, return_type=eval_type)

        raise Exception("Cannot convert to an Evaluatable: {}".format(var))

    def set_var(self, var_name, evaluation=None):
        var = Variable(var_name, DataTypes.SCALAR)
        if evaluation is None:
            eval_obj = Constant(0)
        elif isinstance(evaluation, int):
            eval_obj = Constant(evaluation)
        elif isinstance(evaluation, str):
            eval_obj = Variable(evaluation, return_type=DataTypes.SCALAR)
        else: # Assume evaluation is an Evaluatable and let AssignVarStmt deal with the consequences
            eval_obj = evaluation

        node = AssignVarStmt(var, eval_obj)
        self.symbol_type_table[var_name] = DataTypes.SCALAR
        return node

    def set_array(self, arr_name, length, evaluation=None):
        arr_var = Variable(arr_name, return_type=DataTypes.ARRAY, length=length)
        if evaluation is None:
            evaluation = []
            for i in range(length):
                evaluation._append(0)
            eval_obj = Constant(evaluation)
        elif isinstance(evaluation, list):
            if not len(evaluation) == length:
                raise Exception("Array {} of size {} created, but assigned initial value array that \
                                doesn't match that size".format(arr_name, length))
            eval_obj = Constant(evaluation)
        elif isinstance(evaluation, str):
            if not evaluation in self.symbol_type_table.keys():
                raise Exception("Attempting to evaluate an undefined scalar variable '{}'".format(evaluation))
            eval_type = self.symbol_type_table[evaluation]
            eval_obj = Variable(evaluation, return_type=eval_type)
        else: #Assume evaluation is Evaluatable and let AssignVarStmt deal with the consequences
            eval_obj = evaluation
        node = AssignVarStmt(arr_var, eval_obj)
        self.symbol_type_table[arr_name] = DataTypes.ARRAY
        return node

    def update_array_at(self, arr_name, idx, evaluation):
        self.verify_var_type(arr_name, DataTypes.ARRAY)
        self.verify_var_type(evaluation, DataTypes.SCALAR)

        arr_var = Variable(arr_name, return_type=DataTypes.ARRAY)
        if isinstance(evaluation, list):
            eval_obj = Constant(evaluation)
        elif isinstance(evaluation, str):
            eval_obj = Variable(evaluation)
        else: #Assume evaluation is Evaluatable and let AssignVarStmt deal with the consequences
            eval_obj = evaluation
        node = UpdateArrayIndexStmt(arr_var, idx, eval_obj)
        return node

    def is_equal(self, lhs, rhs):
        lhs_node = self.to_evaluatable(lhs)
        rhs_node = self.to_evaluatable(rhs)
        node = CompareEquals(lhs_node, rhs_node)
        return node

    def is_greater(self, lhs, rhs):
        lhs_node = self.to_evaluatable(lhs)
        rhs_node = self.to_evaluatable(rhs)
        node = CompareGreater(lhs_node, rhs_node)
        return node

    def if_else(self, bool_cond, true_block, false_block=None):
        return IfElseBlock(bool_cond, true_block, false_block)

    def create_func(self, func_name, params, func_code):
        pass

    def define_func(self, func_name, arg_list, code, return_type):
        if func_name not in self.function_def_table.keys():
            self.function_def_table[func_name] = []
        func_def = FunctionDef(func_name, code, return_type, arg_list)
        self.function_def_table[func_name].append(func_def)
        return func_def

    def calc(self, op, op1, op2):
        eval_op1 = self.to_evaluatable(op1)
        eval_op2 = self.to_evaluatable(op2)
        return ArithmeticExpr(op, eval_op1, eval_op2)

    def call(self, func_name, arg_list=[]):
        eval_args = []
        for arg in arg_list:
            eval_args.append( self.to_evaluatable(arg) )
        node = FuncCall(func_name, eval_args)
        return node

    #def parse_cfg(self, top_level = True):
    #    self.head = CFGNode()
    #    for stmt in self.program:
    #        if top_level and not isinstance(stmt, TopLevel):
    #            raise Exception("{} cannot appear at the top-level of the program".format(stmt))
    #        if isinstance(stmt, BranchPoint):
