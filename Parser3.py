from pydoc import describe
import re

from Lexer2 import Lexer

class Parser:

    lex_types = {'SW': 1, 'LIM': 2, 'ID': 3, 'BIN': 4, 'OCT': 5, 'DEC': 6, 'HEX': 7, 'REAL': 8}
    service_words = {'or': 0, 'and': 1, 'not': 2, 'while': 3, 'read': 4, 'for': 5, 'to': 6, 'do': 7,
                     'int': 8, 'float': 9, 'bool': 10, 'write': 11, 'if': 12, 'then': 13, 'else': 14,
                     'as': 15, 'true': 16, 'false': 17}  # 1
    limiters = {'{': 0, '}': 1, ';': 2, '[': 3, ']': 4, '=': 5, '<>': 6, '<': 7, '<=': 8, '>': 9, '>=': 10,
                '+': 11, '-': 12, '*': 13, '/': 14, '(': 15, ')': 16, ',': 17, ':': 18}  # 2
    lex_num = 0
    lex = []
    lex_value = ''
    lex_type = -1
    errorMessage = ''
    lexer = None
    last_n = -1

    described_ides = {}
    last_type = ''

    stack_of_operations = []
    required_type = []

    def __init__(self, f): # конструктор
        self.lexer = Lexer(f)
        self.run()
        print("OK!")

    def check_if_exist(self):
        return self.get_lex() in self.described_ides.keys()

    def gl(self): # взять лексему
        if self.lex_num < len(self.lexer.outputs):
            self.lex = self.lexer.outputs[self.lex_num]
            self.lex_value = self.lexer.outputs[self.lex_num][1]
            self.lex_type = self.lexer.outputs[self.lex_num][0]
            self.lex_num += 1
            while self.get_lex() == '\n':
                self.last_n = self.lex_num
                self.gl()
        else:
            self.lex = []
            self.lex_value = ''
            self.lex_type = -1

    def run(self):
        self.gl()
        self.P1()

    # <программа>::= «{» {/ (<описание> | <оператор>) ; /} «}»
    def P1(self):
        if self.get_lex() == "{":
            self.gl()
            self.P()
        else:
            raise SyntaxError('Неправильное начало программы')
        while self.get_lex() == ";":
            self.gl()
            self.P()
        if self.get_lex() != "}":
            raise SyntaxError(f'Ожидалось "}}", получено {self.get_lex()}')

    # <программа>::= «{» {/ (<описание> | <оператор>) ; /} «}»
    def P(self):
        if self.lex_type == self.lex_types['SW']:
            if self.get_lex() in ['int', 'float', 'bool']:
                self.last_type = self.get_lex()
                self.gl()
                self.D1()
            elif self.get_lex() in ['if', 'for', 'while', 'read', 'write']:
                    self.OP()
        elif self.lex_type == self.lex_types['LIM']:
            if self.get_lex() == '[':
                self.OP()
            elif self.get_lex() == '}':
                return
        elif self.lex_type == self.lex_types['ID']:
            self.OP()
        else:
            raise SyntaxError(f'Получено: "{self.get_lex()}"')
        if self.get_lex() == ';':
            self.gl()
            self.P()
        else:
            raise SyntaxError(f'Получено: "{self.get_lex()}"')

    # <описание>::= <тип> <идентификатор> { , <идентификатор> }
    # D1 -> <тип> D { , D }
    def D1(self):
        self.D()
        while self.get_lex() == ',':
            self.gl()
            self.D()

    def D(self):
        if self.lex_type != self.lex_types['ID']:
            raise SyntaxError(f'Ожидался идентификатор, получена лексема "{self.get_lex()}"')
        if not self.check_if_exist():
            self.described_ides[self.get_lex()] = self.last_type
            self.gl()
        else:
            raise SyntaxError(f'Идентификатор "{self.get_lex()}" уже описан.')


    def desc_D(self):
        if self.lex_type != self.lex_types['ID']:
            raise SyntaxError(f'Ожидался идентификатор, получена лексема "{self.get_lex()}"')
        if self.check_if_exist():
            self.gl()
        else:
            raise SyntaxError(f'Идентификатор "{self.get_lex()}" не был описан.')

    # <оператор>::= <составной> | <присваивания> | <условный> |
    #  <фиксированного_цикла> | <условного_цикла> | <ввода> |
    #  <вывода>
    def OP(self):
        if self.lex_type == self.lex_types['ID']:
            self.AOP()
        elif self.lex_type == self.lex_types['LIM']:
            if self.lex_value != self.limiters['[']:
                raise SyntaxError(f'Неопознанный ограничитель в начале оператора: "{self.get_lex()}"')
            else:
                self.gl()
                self.MULTI_OP()
        elif self.lex_type == self.lex_types['SW']:

            if self.lex_value == self.service_words['if']:
                self.gl()
                self.required_type.append('bool')
                self.IFOP()
            elif self.lex_value == self.service_words['for']:
                self.gl()
                self.FOROP()
            elif self.lex_value == self.service_words['while']:
                self.gl()
                self.required_type.append('bool')
                self.WHILEOP()
            elif self.lex_value == self.service_words['read']:
                self.gl()
                self.ROP()
            elif self.lex_value == self.service_words['write']:
                self.gl()
                self.required_type.append('any')
                self.WOP()
            else:
                raise SyntaxError(f'Неопознанная лексема начала оператора: "{self.get_lex()}"')
        else:
            raise SyntaxError(f"Неопознанный оператор {self.lex_value}")


    # <присваивания>::= <идентификатор> as <выражение>
    def AOP(self):
        if not self.check_if_exist():
            raise SyntaxError(f'Идентификатор {self.get_lex()} не был описан.')
        self.required_type.append(self.described_ides[self.get_lex()])
        self.gl()

        if self.get_lex() != 'as':
            raise SyntaxError(f'Ожидалось "as", получено "{self.get_lex()}"')
        self.gl()
        self.EXPR()

    # <составной>::= «[» <оператор> { ( : | перевод строки) <оператор> } «]»
    def MULTI_OP(self):
        self.OP()
        while self.get_lex() == ':' or self.last_n == self.lex_num - 1:
            if self.get_lex() == ':':
                self.gl()
            self.OP()

        if self.get_lex() != ']':
            raise SyntaxError(f'Ожидалась скобка "]", получена лексема "{self.get_lex()}"')
        else:
            self.gl()

    # <условный>::= if <выражение> then <оператор> [ else <оператор>]
    def IFOP(self):
        self.EXPR()
        if self.get_lex() != 'then':
            raise SyntaxError(f'Ожидалось "then", получено "{self.get_lex()}"')
        self.gl()
        self.OP()
        if self.get_lex() == 'else':
            self.gl()
            self.OP()

    # <фиксированного_цикла>::= for <присваивания> to <выражение> do
    # <оператор>
    def FOROP(self):
        if self.lex_type != self.lex_types['ID']:
            raise SyntaxError(f'Ожидался идентификатор, получена лексема "{self.get_lex()}"')
        self.gl()
        self.AOP()
        if self.get_lex() != 'to':
            raise SyntaxError(f'Ожидался "to", получена лексема "{self.get_lex()}"')
        self.gl()
        self.EXPR()
        if self.get_lex() != 'do':
            raise SyntaxError(f'Ожидался "do", получена лексема "{self.get_lex()}"')
        self.gl()
        self.OP()

    # <условного_цикла>::= while <выражение> do <оператор>
    def WHILEOP(self):
        self.EXPR()
        if self.get_lex() != 'do':
            raise SyntaxError(f'Ожидался "do", получена лексема "{self.get_lex()}"')
        self.gl()
        self.OP()

    # <ввода>::= read «(»<идентификатор> {, <идентификатор> } «)»
    def ROP(self):
        if self.get_lex() != '(':
            raise SyntaxError(f'Ожидалась скобка "(", получена лексема "{self.get_lex()}"')
        self.gl()
        self.desc_D()
        while self.get_lex() == ',':
            self.gl()
            self.desc_D()
        if self.get_lex() != ')':
            raise SyntaxError(f'Ожидалась скобка ")", получена лексема "{self.get_lex()}"')

    # <вывода>::= write «(»<выражение> {, <выражение> } «)»
    def WOP(self):
        if self.get_lex() != '(':
            raise SyntaxError(f'Ожидалась скобка "(", получена лексема "{self.get_lex()}"')
        self.stack_of_operations.append(self.get_lex())
        self.gl()
        self.EXPR()
        while self.get_lex() == ',':
            self.gl()
            self.EXPR()
        if self.get_lex() != ')':
            raise SyntaxError(f'Ожидалась скобка ")", получена лексема "{self.get_lex()}"')
        self.stack_of_operations.append(self.get_lex())

    # <выражение>::= <операнд>{<операции_группы_отношения> <операнд>}
    def EXPR(self):
        self.OPER()
        while self.get_lex() in ['<>', '=', '<', '<=', '>', '>=']:
            self.stack_of_operations.append(self.get_lex())
            self.gl()
            self.OPER()
        print('---------------------------')
        print(self.stack_of_operations)
        print(self.required_type)
        self.type_of_exp()
        print(self.stack_of_operations)
        print(self.required_type)

        if self.stack_of_operations[-1] != 'None':
            if self.stack_of_operations[-1] == 'any':
                pass
            elif self.stack_of_operations[-1] != self.required_type[-1]:
                raise SyntaxError(f'Ожидался тип выражения "{self.required_type[-1]}", получен "{self.stack_of_operations[-1]}"')
            else:
                self.stack_of_operations = []
                self.required_type = self.required_type[:-1]
                print('success')
        else:
            self.stack_of_operations = []
        # print(self.required_type)

    # <операнд>::= <слагаемое> {<операции_группы_сложения> <слагаемое>}
    def OPER(self): # операнд
        self.SUMM()
        while self.get_lex() in ['+', '-', 'or']:
            self.stack_of_operations.append(self.get_lex())
            self.gl()
            self.SUMM()

    # <слагаемое>::= <множитель> {<операции_группы_умножения> <множитель>}
    def SUMM(self): # слагаемое
        self.MUL()
        while self.get_lex() in ['*', '/', 'and']:
            self.stack_of_operations.append(self.get_lex())
            self.gl()
            self.MUL()

    # <множитель>::= <идентификатор> | <число> | <логическая_константа> |
    #  <унарная_операция> <множитель> | «(»<выражение>«)»
    def MUL(self): # множитель
        if self.lex_type == self.lex_types['ID']:
            if not self.check_if_exist():
                raise SyntaxError(f'Идентификатор {self.get_lex()} не был описан.')
            self.stack_of_operations.append(self.described_ides[self.get_lex()])
            self.gl()
        elif self.lex_type == self.lex_types['REAL']:
            self.stack_of_operations.append('float')
            self.gl()
        elif self.lex_type in [self.lex_types['BIN'],
                self.lex_types['OCT'],
                self.lex_types['DEC'],
                self.lex_types['HEX']]:
            self.stack_of_operations.append('int')
            self.gl()
        elif self.lex_type == self.lex_types['SW']:
            if self.get_lex() in ['true', 'false']:
                self.stack_of_operations.append('bool')
                self.gl()
            elif self.get_lex() == 'not':
                self.gl()
                self.stack_of_operations.append('not')
                self.MUL()
            else:
                raise SyntaxError(f'Ошибка в синтаксисе множителя "{self.get_lex()}"')
        elif self.lex_type == self.lex_types['LIM']:
            if self.get_lex() != '(':
                raise SyntaxError(f'Ожидалась скобка "(", получена лексема "{self.get_lex()}"')
            self.stack_of_operations.append('(')
            self.gl()
            self.EXPR()
            if self.get_lex() != ')':
                raise SyntaxError(f'Ожидалась скобка ")", получена лексема "{self.get_lex()}"')
            self.stack_of_operations.append(')')
            self.gl()
        else:
            raise SyntaxError(f'Ошибка в синтаксисе множителя "{self.get_lex()}"')

    def type_of_exp(self):
        if len(self.stack_of_operations) == 0:
            self.stack_of_operations.append('None')
            return self.stack_of_operations
        elif len(self.stack_of_operations) == 1:
            return self.stack_of_operations

        # elif len(self.stack_of_operations) == 2:
        #     if self.stack_of_operations[0] == 'not':
        #         return self.stack_of_operations[1]
        #     else:
        #         raise SyntaxError("Ожидалась унарная операция")
        # while '(' in

        stack = self.stack_of_operations
        while len(stack) != 1:
            while '(' in stack:
                pass
            while '*' in stack or\
                '/' in stack:
                for i in range(len(stack)):
                    if stack[i] in ['*', '/']:
                        now_op = stack[i-1:i+2]
                        if now_op[0] != now_op[2]:
                            raise SyntaxError("Операнды должны быть одного типа")
                        elif now_op[0] not in ['int', 'float']:
                            raise SyntaxError(f'Знак "{now_op[1]}" недопустим между булевыми операндами')
                        stack = stack[:i-1] + [now_op[0]] + stack[i+2:]
                        break

            while '+' in stack or\
                '-' in stack:
                for i in range(len(stack)):
                    if stack[i] in ['+', '-']:
                        now_op = stack[i-1:i+2]
                        if now_op[0] != now_op[2]:
                            raise SyntaxError("Операнды должны быть одного типа")
                        elif now_op[0] not in ['int', 'float']:
                            raise SyntaxError(f'Знак "{now_op[1]}" недопустим между булевыми операндами')
                        stack = stack[:i-1] + [now_op[0]] + stack[i+2:]
                        break

            while '<>' in stack or\
                '=' in stack or\
                '<' in stack or\
                '<=' in stack or\
                '>' in stack or\
                '>=' in stack:
                for i in range(len(stack)):
                    if stack[i] in ['<>', '=', '<', '<=', '>', '>=']:
                        now_op = stack[i-1:i+2]
                        if now_op[0] != now_op[2]:
                            raise SyntaxError("Операнды должны быть одного типа")
                        # elif now_op[0] not in ['int', 'float']:
                        #     raise SyntaxError(f'Знак "{now_op[1]}" недопустим между операндами')
                        stack = stack[:i-1] + ['bool'] + stack[i+2:]
                        break

            while 'and' in stack:
                for i in range(len(stack)):
                    if stack[i] == 'and':
                        now_op = stack[i-1:i+2]
                        if now_op[0] != now_op[2]:
                            raise SyntaxError("Операнды должны быть одного типа")
                        elif now_op[0] != 'bool':
                            raise SyntaxError(f'Знак "{now_op[1]}" недопустим между численными операндами')
                        stack = stack[:i-1] + [now_op[0]] + stack[i+2:]
                        break

            while 'or' in stack:
                for i in range(len(stack)):
                    if stack[i] == 'or':
                        now_op = stack[i - 1:i + 2]
                        if now_op[0] != now_op[2]:
                            raise SyntaxError("Операнды должны быть одного типа")
                        elif now_op[0] != 'bool':
                            raise SyntaxError(f'Знак "{now_op[1]}" недопустим между численными операндами')
                        stack = stack[:i - 1] + [now_op[0]] + stack[i + 2:]
                        break

            while 'not' in stack:
                for i in range(len(stack)):
                    if stack[i] == 'not':
                        now_op = stack[i:i+2]
                        if now_op != 'bool':
                            raise SyntaxError(f' Унарный оператор "{now_op[0]}" может использоваться только с булевыми значениями')
                        stack = stack[:i] + [now_op[1]] + stack[i+2:]
                        break

            # new_op = self.stack_of_operations[-3::]
            # self.stack_of_operations = self.stack_of_operations[:-3]
            #
            # if new_op[0] != new_op[2]:
            #     raise SyntaxError("Операнды должны быть одного типа")
            #
            # now_type = new_op[0]
            # op = new_op[1]
            # if now_type == 'int' or now_type == 'float':
            #     if op in ['<>', '=', '<', '<=', '>', '>=']:
            #         self.stack_of_operations.append('bool')
            #     elif op in ['+', '-', '*', '/']:
            #         self.stack_of_operations.append(now_type)
            #     else:
            #         raise SyntaxError(f'Знак {op} недопустим между численными операндами')
            # elif now_type == 'bool':
            #     if op in ['or', 'and']:
            #         self.stack_of_operations.append('bool')
            #     else:
            #         raise SyntaxError(f'Знак {op} недопустим между булевыми операндами')

    def get_lex(self): # получить лексему по номеру
        match self.lex_type:
            case 1:
                return self.lexer.service_words[self.lex_value]
            case 2:
                return self.lexer.limiters[self.lex_value]
            case 3:
                return self.lexer.identifiers[self.lex_value]
            case 4:
                return self.lexer.numbers_bin[self.lex_value]
            case 5:
                return self.lexer.numbers_oct[self.lex_value]
            case 6:
                return self.lexer.numbers_dec[self.lex_value]
            case 7:
                return self.lexer.numbers_hex[self.lex_value]
            case 8:
                return self.lexer.numbers_real[self.lex_value]


f = open('17.txt', 'r')
parser = Parser(f)
