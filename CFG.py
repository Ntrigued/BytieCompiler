from abc import ABC

from data_types import DataTypes


class CFGNode(ABC):
    """
      All CFGs start with a base node, just for code simplification
    """
    def __init__(self):
        self.children = set()
        self.parents = set()

    def addChild(self, child):
        if not child in self.children:
            self.children.add(child)
            child.addParent(self)

    def addParent(self, parent):
        if not parent in self.parents:
            self.parents.add(parent)

    def print(self, indent=0):
        raise NotImplementedError()


class TopLevel(CFGNode):
    """
        Node that can appear at the top-level of the program list
    """
    pass


class BranchPoint(CFGNode):
    pass


class AssignStmt(CFGNode):
    pass


class Evaluatable(CFGNode):
    def __init__(self, return_type):
        super().__init__()

        assert isinstance(return_type, DataTypes)
        self.return_type = return_type


class FuncCall(Evaluatable):
    def __init__(self, func_name, args, return_type):
        super().__init__(return_type)

        assert isinstance(func_name, str)
        assert isinstance(args, list)
        for arg in args:
            assert isinstance(arg, Evaluatable)
        self.func_name = func_name
        self.args = args

    def print(self, indent=0):
        print("{}FuncCall: {}(".format('\t'*indent, self.func_name))
        for arg in self.args:
            arg.print(indent+1)
        print('\t'*indent +')')


class FunctionDef(CFGNode):
    def __init__(self, func_name, code, return_type, arg_list=[]):
        super().__init__()

        assert isinstance(func_name, str)
        assert isinstance(code, list)
        for item in code:
            assert isinstance(item, CFGNode)
        assert isinstance(return_type, DataTypes)
        assert isinstance(arg_list, list)

        self.func_name = func_name
        self.return_type = return_type
        self.arg_list = arg_list


class Constant(Evaluatable):
    def __init__(self, val):
        if isinstance(val, list):
            super().__init__(DataTypes.ARRAY)
            for item in val:
                assert (isinstance(item, int) and -127 < item < 128)
        elif isinstance(val, int):
            super().__init__(DataTypes.SCALAR)
        else:
            raise Exception("val must be either of type int or list, val = {}".format(val))
        self.val = val

    def print(self, indent=0):
        print('\t'*indent + 'Constant<{}>({})'.format(self.return_type, self.val))


class Variable(Evaluatable):
    def __init__(self, var_name, return_type, length=''):
        super().__init__(return_type)

        if return_type == DataTypes.ARRAY:
            assert isinstance(var_name, str)
            assert isinstance(length, int)
            self.length = length
        elif return_type == DataTypes.SCALAR:
            assert isinstance(var_name, str)
            self.length = None
        self.var_name = var_name

    def print(self, indent=0):
        print('\t'*indent + 'Variable<{}>({})'.format(self.return_type, self.var_name))


class ArithmeticExpr(Evaluatable):
    def __init__(self, op, op1, op2):
        assert op1.return_type == op2.return_type
        super().__init__(op1.return_type)

        assert (op in ['+', '-', '*'])
        self.op = op
        self.op1 = op1
        self.op2 = op2

    def print(self, indent=0):
        print('\t'*indent + 'ArithmeticExpr<{}>('.format(self.return_type))
        self.op1.print(indent+1)
        print('\t'*indent + self.op)
        self.op2.print(indent+1)
        print('\t'*indent + ')')


class AssignVarStmt(AssignStmt):
    def __init__(self, var, evaluatable):
        super().__init__()
        assert var.return_type == evaluatable.return_type
        self.var = var
        self.evaluation = evaluatable

    def print(self, indent=0):
        print('\t'*indent + 'AssignVarStmt(')
        self.var.print(indent+1)
        print('\t'*indent + '=')
        if self.evaluation:
            self.evaluation.print(indent+1)
        print('\t'*indent + ')')


class UpdateArrayIndexStmt(CFGNode): #TODO what should this inherit from?
    def __init__(self, var, idx, evaluatable):
        super().__init__()

        assert var.return_type == DataTypes.ARRAY
        assert isinstance(idx, int)
        assert evaluatable.return_type == DataTypes.SCALAR
        self.var = var
        self.idx = idx
        self.evaluation = evaluatable

    def print(self, indent=0):
        print('\t'*indent + 'UpdateArrayIndexStmt(')
        self.var.print(indent+1)
        print('\t'*indent + 'index: {}'.format())
        self.evaluation.print(indent+1)
        print('\t'*indent + ')')


class BooleanCondition(CFGNode):
    pass


class Comparison(BooleanCondition):
    def __init__(self, lhs, rhs):
        super().__init__()

        assert isinstance(lhs, Evaluatable) and isinstance(rhs, Evaluatable)
        assert lhs.return_type == rhs.return_type
        self.lhs = lhs
        self.rhs = rhs

    def print(self, indent=0):
        print('\t'*indent + '{}('.format(self.__class__.__qualname__))
        self.rhs.print(indent+1)
        self.lhs.print(indent+1)
        print('\t'*indent + ')')


class CompareEquals(Comparison):
    pass


class CompareGreater(Comparison):
    pass


class IfElseBlock(BranchPoint):
    def __init__(self, bool_cond, true_block, false_block):
        super().__init__()

        assert isinstance(bool_cond, BooleanCondition)
        assert isinstance(true_block, list)
        for item in true_block:
            assert isinstance(item, CFGNode)
        assert isinstance(false_block, list)
        for item in false_block:
            assert isinstance(item, CFGNode)
        self.bool_cond = bool_cond
        self.true_block = true_block
        self.false_block = false_block

    def print(self, indent=0):
        print('\t'*indent + 'IfElseBlock(')
        print('\t'*(indent+1) + 'BooleanCondition:')
        self.bool_cond.print(indent+2)
        print('\t'*(indent+1) + 'true block:')
        for node in self.true_block:
            node.print(indent+2)
        print('\t'*(indent+1) + 'false block:')
        for node in self.false_block:
            node.print(indent+2)
        print('\t'*indent + ')')


class InterpreterDebugNode(CFGNode):
    """
        Used to output debug info while interpreting the program
    """
    def __init__(self, output):
        super().__init__()
        self.output = output

    def print(self, indent=0):
        print('\t'*indent + 'InterpreterDebugNode(')
        print('\t'*(indent+1) + 'Output:')
        print('\t'*(indent+2) + '"{}"'.format(self.output))
        print('\t'*indent + ')')
