from CFG import *
from optimizations.opt_pass import OptPass


class PropagateConstants(OptPass):
    def __init__(self):
        super().__init__()
        self.const_table = {}
        self.scope_stack = [set()]
        self.function_vars_table = {}

    def deepen_scope_level(self):
        self.scope_stack.append(set())

    def unwind_scope_level(self):
        scoped_vars = self.scope_stack.pop()
        for var_name in scoped_vars:
            self.pop_var(var_name)

    def push_var(self, var_name, const_node):
        self.scope_stack[-1].add(var_name)
        if var_name not in self.const_table.keys():
            self.const_table[var_name] = []
        self.const_table[var_name].append(const_node)

    def pop_var(self, var_name):
        return self.const_table[var_name].pop()

    def invalidate_var(self, var_name):
        if var_name in self.scope_stack[-1]:
            self.scope_stack[-1].remove(var_name)
        if var_name in self.const_table.keys():
            del self.const_table[var_name]

    def foldAssignVarStmt(self, node):
        var, evaluation = node.var, node.evaluation
        if isinstance(evaluation, Constant):
            self.push_var(var.var_name, evaluation)
        elif isinstance(evaluation, Variable):
            if evaluation.var_name in self.const_table:
                const_node = self.const_table[evaluation.var_name][-1]
                node.evaluation = const_node
                node = self.foldAssignVarStmt(node)
        elif isinstance(evaluation, ArithmeticExpr):
            node.evaluation = self.foldArithmetixExpr(evaluation)
            node = self.foldAssignVarStmt(node)
        return node

    def foldEvaluatable(self, node):
        if isinstance(node, ArithmeticExpr):
            return self.foldArithmetixExpr(node)
        elif isinstance(node, FuncCall):
            return self.foldFuncCall(node)
        elif isinstance(node, Constant) or isinstance(node, Variable):
            return node

    def foldArithmetixExpr(self, node):
        op1, op2 = node.op1, node.op2
        if isinstance(op1, Variable):
            if op1.var_name in self.const_table.keys():
                node.op1 = self.const_table[op1.var_name][-1]
        elif isinstance(op1, ArithmeticExpr):
            node.op1 = self.foldArithmetixExpr(op1)
        if isinstance(op2, Variable):
            if op2.var_name in self.const_table.keys():
                node.op2 = self.const_table[op2.var_name][-1]
        elif isinstance(op2, ArithmeticExpr):
            node.op2 = self.foldArithmetixExpr(op2)

        if isinstance(node.op1, Constant) and isinstance(node.op2, Constant):
            val = None
            if node.op == '+':
                val = node.op1.val + node.op2.val
            elif node.op == '-':
                val = node.op1.val - node.op2.val
            elif node.op == '*':
                val = node.op1.val * node.op2.val
            return Constant(val)
        return node

    def foldIfElseBlock(self, node):
        true_block = node.true_block
        false_block = node.false_block
        self.deepen_scope_level()
        self.run_pass(true_block)
        self.unwind_scope_level()
        self.deepen_scope_level()
        self.run_pass(false_block)
        self.deepen_scope_level()
        altered_vars = self.get_altered_vars(true_block).union( self.get_altered_vars(false_block) )
        for var_name in altered_vars:
            self.invalidate_var(var_name)

        bool_cond = node.bool_cond
        bool_cond.lhs = self.foldEvaluatable(bool_cond.lhs)
        bool_cond.rhs = self.foldEvaluatable(bool_cond.rhs)
        return node

    def foldWhileBlock(self, node):
        code_block = node.code_block
        self.deepen_scope_level()
        self.run_pass(code_block)
        self.unwind_scope_level()
        altered_vars = self.get_altered_vars(code_block)
        for var_name in altered_vars:
            self.invalidate_var(var_name)
        return node

    def foldFunctionDef(self, node):
        altered_vars = self.get_altered_vars(node.code_block)
        # Allow for dynamic re-defining of functions by just keeping
        # track of any variables that are defined in function def
        if node.func_name not in self.function_vars_table.keys():
            self.function_vars_table[node.func_name] = set()
        self.function_vars_table[node.func_name].union(altered_vars)

        # Only perform constant propagation for variables defined in the function
        # foldFuncCall invalidates all vars defined in the func, so no need to
        # keep track of changes in const_table or scope_stack
        scope_stack, const_table = self.scope_stack, self.const_table
        self.scope_stack, self.const_table = [], {}
        self.run_pass(node.code_block)
        self.scope_stack, self.const_table = scope_stack, const_table
        return node

    def foldFuncCall(self, node):
        func_name, args = node.func_name, node.args
        # TODO, add propagation into functions for vars defined outside of func def
        altered_vars = self.function_vars_table[func_name]
        for var_name in altered_vars:
            self.invalidate_var(var_name)

    def get_altered_vars(self, code_block):
        altered_vars = set()
        for node in code_block:
            if isinstance(node, AssignStmt):
                altered_vars.add(node.var.var_name)
        return altered_vars

    def run_pass(self, cfg):
        super().run_pass(cfg)

        for i in range(len(cfg)):
            node = cfg[i]
            if isinstance(node, AssignVarStmt):
                node = self.foldAssignVarStmt(node)
            elif isinstance(node, IfElseBlock):
                node = self.foldIfElseBlock(node)
            elif isinstance(node, WhileBlock):
                node = self.foldWhileBlock(node)
            elif isinstance(node, FunctionDef):
                node = self.foldFunctionDef(node)
            elif isinstance(node, InterpreterDebugNode):
                pass
            else:
                raise Exception("Shouln't have happened: " + str(node))
            cfg[i] = node
