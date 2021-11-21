from CFG import *

from data_types import DataTypes

class BytecodeGenerator:
    def __init__(self):
        self.symbol_table = {}
        self.reg_id = 0 # constantly increasing, uniquely identify each
        self.label_id = 0

    def get_next_register(self):
        reg_id = self.reg_id
        self.reg_id += 1
        return 'REG_' + str(reg_id)

    def get_next_label(self):
        label_id = self.label_id
        self.label_id += 1
        return 'LABEL_' + str(label_id)

    def generate_bytecode(self, program):
        bytecode = []
        for node in program:
            if isinstance(node, AssignStmt):
                bytecode += self.lowerAssignment(node)
            elif isinstance(node, ArithmeticExpr):
                bytecode += self.lowerArithmeticExpr(node)
            elif isinstance(node, FunctionDef):
                bytecode += self.lowerFunctionDef(node)
            elif isinstance(node, IfElseBlock):
                bytecode += self.lowerIfElseBlock(node)
            elif isinstance(node, WhileBlock):
                bytecode += self.lowerWhileBlock(node)
            elif isinstance(node, InterpreterDebugNode):
                bytecode += [('DEBUG_PRINT', node.output)]
            elif isinstance(node, Evaluatable):
                raise Exception("Evaluatable found at top outer-most level of CFG: {}".format(node))
            else:
                raise Exception("Invalid node found at top outer-most level of CFG: {}".format(node))
        return bytecode

    def lowerArithmeticExpr(self, node):
        if node.return_type == DataTypes.SCALAR:
            return self.lowerArithmeticExprScalar(node)
        elif node.return_type == DataTypes.ARRAY:
            return self.lowerArithmeticExprArray(node)

    def lowerArithmeticExprScalar(self, node):
        instrs_op1, value_at_op1= self.lowerEvaluatable(node.op1)
        instrs_op2, value_at_op2 = self.lowerEvaluatable(node.op2)
        instrs = instrs_op1 + instrs_op2

        op = node.op
        value_at_result = self.get_next_register()
        if op == '+':
            instrs.append(('ADD', value_at_result, value_at_op1, value_at_op2))
        elif op == '-':
            instrs.append(('SUB', value_at_result, value_at_op1, value_at_op2))
        elif op == '*':
            instrs.append(('MUL', value_at_result, value_at_op1, value_at_op2))
        else:
            raise Exception("This shouldn't of happened. ArithmeticExpression operator is {}".format(op))
        return instrs, value_at_result


    def lowerArithmeticExprArray(self, node):
        raise NotImplementedError()

    def lowerAssignment(self, node):
        instrs, value_at = self.lowerEvaluatable(node.evaluation)
        if not node.var.var_name in self.symbol_table:
            self.symbol_table[node.var.var_name] = [value_at]
        else:
            var_reg = self.symbol_table[node.var.var_name][-1]
            instrs += [('SET', var_reg, value_at)]
        return instrs

    def lowerEvaluatable(self, node):
        instrs = []
        value_at = None
        if isinstance(node, Constant):
            reg_id = self.get_next_register()
            instrs = [('SET', reg_id, node.val)]
            value_at = reg_id
        elif isinstance(node, Variable):
            try:
                reg_id = self.symbol_table[node.var_name][-1]
                value_at = reg_id
            except KeyError:
                raise Exception("Cannot resolve symbol: {}".format(node.var_name))
        elif isinstance(node, ArithmeticExpr):
            instrs, value_at = self.lowerArithmeticExpr(node)
        elif isinstance(node, FuncCall):
            raise NotImplementedError("Haven't Implemented function calls yet")
        else:
            raise Exception("Can't evaluate as an Evaluatable: {}".format(node)) #TODO: make node types implement
                                                                                 # # __str__ so something more useful can be printed
        return instrs, value_at

    def lowerFunctionDef(self, node):
        func_name = node.func_name
        arg_list = node.arg_list
        return_type = node.return_type
        code_block = node.code_block

        arg_mapping = []
        for arg in arg_list:
            var_name = arg.var_name
            reg_id = self.get_next_register()
            arg_mapping.append(reg_id)
        node.arg_mapping = arg_mapping

        if func_name not in self.function_table.keys():
            self.function_table[func_name] = []
        self.function_table[func_name].append(node)

    def lowerFuncCall(self, node):
        func_name = node.func_name
        args = node.args

        instrs = []
        #TODO: Check against definitions to named function with correct parameters
        func_info = self.function_table[func_name][-1]

        funcreg_to_args = {}
        for idx in range(len(node.arg_list)):
            # setup register holding arg value, and register which function will work on
            # save mapping for when we place the value back in the arg register
            arg = args[idx]
            arg_instrs, arg_value_at = self.lowerEvaluatable(arg)
            funcreg_id = func_info.arg_mapping[idx]
            funcreg_to_args[funcreg_id] = arg_value_at
            param = node.arg_list[idx]
            param_name = param.var_name
            instrs += arg_instrs
            # copy contents of arg register into func register
            instrs += [('SET', funcreg_id, arg_value_at)]
            # Temporarily, add function param names to symbol_table
            if not param_name in self.symbol_table.keys():
                self.symbol_table[param_name] = []
            self.symbol_table[param_name].append(funcreg_id)
        # execute func code
        #TODO
        instrs += func_instrs
        for idx in range(len(node.arg_list)):
            param = node.arg_list[idx]
            param_name = param.var_name
            funcreg_id = func_info.arg_mapping[idx]

            # copy contents of func register back to arg register
            # and remove symbol table entries for function params
            arg_reg = funcreg_to_args[func_reg]
            instrs += [('SET', arg_reg, func_reg)]
            self.symbol_table[param_name].pop()

        return instrs

    def lowerIfElseBlock(self, node):
        comp_instrs, cmp_value_at = self.lowerBooleanCondition(node.bool_cond)
        true_block, false_block = node.true_block, node.false_block

        instrs = comp_instrs
        if_label, else_label, done_label = self.get_next_label(), self.get_next_label(), self.get_next_label()
        instrs += [('CHK_JMP', cmp_value_at, if_label)]
        instrs += [('JMP',  else_label)]

        if_instrs = [('LABEL', if_label)]
        if_instrs += self.generate_bytecode(true_block)
        if_instrs.append(('JMP', done_label))
        else_instrs = [('LABEL', else_label)]
        else_instrs += self.generate_bytecode(false_block)
        else_instrs.append(('JMP', done_label)) # not needed, but doesn't hurt
        instrs += if_instrs + else_instrs
        instrs.append(('LABEL', done_label))

        return instrs

    def lowerWhileBlock(self, node):
        """
        Two boolean conidition checks are created, so that we can maintain SSA form in the cmp_value at registers
        :param node:
        :return:
        """
        code_block = node.code_block

        comp_instrs, cmp_value_at = self.lowerBooleanCondition(node.bool_cond)
        block_instrs = self.generate_bytecode(code_block)
        start_loop_label, end_loop_label = self.get_next_label(), self.get_next_label()
        instrs = [('LABEL', start_loop_label)]
        instrs += comp_instrs
        instrs += [('NCHK_JMP', cmp_value_at, end_loop_label)]
        instrs += block_instrs
        instrs += [('JMP', start_loop_label)]
        instrs += [('LABEL', end_loop_label)]

        return instrs

    def lowerBooleanCondition(self, bool_cond):
        lhs = bool_cond.lhs
        rhs = bool_cond.rhs
        if not (lhs.return_type == DataTypes.SCALAR or rhs.return_type == DataTypes.SCALAR):
            raise NotImplementedError('Currently, only boolean comparison of scalars is supported')
        lhs_instrs, lhs_value_at = self.lowerEvaluatable(lhs)
        rhs_instrs, rhs_value_at = self.lowerEvaluatable(rhs)
        cmp_value_at = self.get_next_register()
        if isinstance(bool_cond, CompareEquals):
            cmp_instr = ('CMP_EQ', cmp_value_at, lhs_value_at, rhs_value_at)
        elif isinstance(bool_cond, CompareGreater):
            cmp_instr = ('CMP_GT', cmp_value_at, lhs_value_at, rhs_value_at)
        instrs = lhs_instrs + rhs_instrs + [cmp_instr]
        return instrs, cmp_value_at