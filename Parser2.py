from pydoc import describe

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

    def __init__(self, f): # конструктор
        self.lexer = Lexer(f)
        self.run()
        print("OK!")

    def gl(self): # взять лексему
        if self.lex_num < len(self.lexer.outputs):
            self.lex = self.lexer.outputs[self.lex_num]
            self.lex_value = self.lexer.outputs[self.lex_num][1]
            self.lex_type = self.lexer.outputs[self.lex_num][0]
            self.lex_num += 1
            while self.get_lexema() == '\n':
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
        if self.get_lexema() == "{":
            self.gl()
            self.P()
        else:
            raise SyntaxError('Неправильное начало программы')
        while self.get_lexema() == ";":
            self.gl()
            self.P()
        if self.get_lexema() != "}":
            raise SyntaxError(f'Ожидалось "}}", получено {self.get_lexema()}')

    # <программа>::= «{» {/ (<описание> | <оператор>) ; /} «}»
    def P(self):
        if self.lex_type == self.lex_types['SW']:
            if self.get_lexema() in ['int', 'float', 'bool']:
                self.gl()
                self.D1()
            else:
                op_lexes = ['if', 'for', 'while', 'read', 'write']
                for op_lex in op_lexes:
                    if self.lex_value == self.service_words[op_lex]:
                        self.OP()
        elif self.lex_type == self.lex_types['LIM']:
            if self.get_lexema() == '[':
                self.OP()
            elif self.get_lexema() == '}':
                return
        elif self.lex_type == self.lex_types['ID']:
            self.OP()
        else:
            raise SyntaxError(f'Получено: "{self.get_lexema()}"')
        if self.get_lexema() == ';':
            self.gl()
            self.P()
        else:
            raise SyntaxError(f'Получено: "{self.get_lexema()}"')

    # <описание>::= <тип> <идентификатор> { , <идентификатор> }
    # D1 -> <тип> D { , D }
    def D1(self):
        self.D()
        while self.get_lexema() == ',':
            self.gl()
            self.D()

    def D(self):
        if self.lex_type != self.lex_types['ID']:
            raise SyntaxError(f'Ожидался идентификатор, получена лексема "{self.get_lexema()}"')
        self.gl()

    # <оператор>::= <составной> | <присваивания> | <условный> |
    #  <фиксированного_цикла> | <условного_цикла> | <ввода> |
    #  <вывода>
    def OP(self):
        if self.lex_type != self.lex_types['ID'] and\
                self.lex_type != self.lex_types['SW'] and \
                self.lex_type != self.lex_types['LIM']:
            raise SyntaxError(f"Неопознанный оператор {self.lex_value}")
        if self.lex_type == self.lex_types['ID']:
            self.gl()
            self.AOP()
        elif self.lex_type == self.lex_types['LIM']:
            if self.lex_value != self.limiters['[']:
                raise SyntaxError(f'Неопознанный ограничитель в начале оператора: "{self.get_lexema()}"')
            else:
                self.gl()
                self.MULTI_OP()
        elif self.lex_type == self.lex_types['SW']:
            if self.lex_value == self.service_words['if']:
                self.gl()
                self.IFOP()
            elif self.lex_value == self.service_words['for']:
                self.gl()
                self.FOROP()
            elif self.lex_value == self.service_words['while']:
                self.gl()
                self.WHILEOP()
            elif self.lex_value == self.service_words['read']:
                self.gl()
                self.ROP()
            elif self.lex_value == self.service_words['write']:
                self.gl()
                self.WOP()
            else:
                raise SyntaxError(f'Неопознанная лексема начала оператора: "{self.get_lexema()}"')

    # <присваивания>::= <идентификатор> as <выражение>
    def AOP(self):
        if self.get_lexema() != 'as':
            raise SyntaxError(f'Ожидалось "as", получено "{self.get_lexema()}"')
        self.gl()
        self.EXPR()

    # <составной>::= «[» <оператор> { ( : | перевод строки) <оператор> } «]»
    def MULTI_OP(self):
        self.OP()
        while self.get_lexema() == ':' or self.last_n == self.lex_num - 1:
            if self.get_lexema() == ':':
                self.gl()
            self.OP()

        if self.get_lexema() != ']':
            raise SyntaxError(f'Ожидалась скобка "]", получена лексема "{self.get_lexema()}"')
        else:
            self.gl()

    # <условный>::= if <выражение> then <оператор> [ else <оператор>]
    def IFOP(self):
        self.EXPR()
        if self.get_lexema() != 'then':
            raise SyntaxError(f'Ожидалось "then", получено "{self.get_lexema()}"')
        self.gl()
        self.OP()
        if self.get_lexema() == 'else':
            self.gl()
            self.OP()

    # <фиксированного_цикла>::= for <присваивания> to <выражение> do
    # <оператор>
    def FOROP(self):
        if self.lex_type != self.lex_types['ID']:
            raise SyntaxError(f'Ожидался идентификатор, получена лексема "{self.get_lexema()}"')
        self.gl()
        self.AOP()
        if self.get_lexema() != 'to':
            raise SyntaxError(f'Ожидался "to", получена лексема "{self.get_lexema()}"')
        self.gl()
        self.EXPR()
        if self.get_lexema() != 'do':
            raise SyntaxError(f'Ожидался "do", получена лексема "{self.get_lexema()}"')
        self.gl()
        self.OP()

    # <условного_цикла>::= while <выражение> do <оператор>
    def WHILEOP(self):
        self.EXPR()
        if self.get_lexema() != 'do':
            raise SyntaxError(f'Ожидался "do", получена лексема "{self.get_lexema()}"')
        self.gl()
        self.OP()

    # <ввода>::= read «(»<идентификатор> {, <идентификатор> } «)»
    def ROP(self):
        if self.get_lexema() != '(':
            raise SyntaxError(f'Ожидалась скобка "(", получена лексема "{self.get_lexema()}"')
        self.gl()
        self.D()
        while self.get_lexema() == ',':
            self.gl()
            self.D()
        if self.get_lexema() != ')':
            raise SyntaxError(f'Ожидалась скобка ")", получена лексема "{self.get_lexema()}"')

    # <вывода>::= write «(»<выражение> {, <выражение> } «)»
    def WOP(self):
        if self.get_lexema() != '(':
            raise SyntaxError(f'Ожидалась скобка "(", получена лексема "{self.get_lexema()}"')
        self.gl()
        self.EXPR()
        while self.get_lexema() == ',':
            self.gl()
            self.EXPR()
        if self.get_lexema() != ')':
            raise SyntaxError(f'Ожидалась скобка ")", получена лексема "{self.get_lexema()}"')

    # <выражение>::= <операнд>{<операции_группы_отношения> <операнд>}
    # сама проверяет
    def EXPR(self):
        self.OPER()
        while self.get_lexema() in [ '<>', '=', '<', '<=', '>', '>=' ]:
            self.gl()
            self.OPER()

    # <операнд>::= <слагаемое> {<операции_группы_сложения> <слагаемое>}
    def OPER(self): # операнд
        self.SUMM()
        while self.get_lexema() in ['+', '-', 'or' ]:
            self.gl()
            self.SUMM()

    # <слагаемое>::= <множитель> {<операции_группы_умножения> <множитель>}
    def SUMM(self): # слагаемое
        self.MUL()
        while self.get_lexema() in ['*', '/', 'and']:
            self.gl()
            self.MUL()

    # <множитель>::= <идентификатор> | <число> | <логическая_константа> |
    #  <унарная_операция> <множитель> | «(»<выражение>«)»
    def MUL(self): # множитель
        if self.lex_type == self.lex_types['ID']:
            self.gl()
        elif self.lex_type in [self.lex_types['BIN'],
                self.lex_types['OCT'],
                self.lex_types['DEC'],
                self.lex_types['HEX'],
                self.lex_types['REAL']]:
            self.gl()
        elif self.lex_type == self.lex_types['SW']:
            if self.get_lexema() in ['true', 'false']:
                self.gl()
            elif self.get_lexema() == 'not':
                self.gl()
                self.MUL()
            else:
                raise SyntaxError(f'Ошибка в синтаксисе множителя "{self.get_lexema()}"')
        elif self.lex_type == self.lex_types['LIM']:
            if self.get_lexema() != '(':
                raise SyntaxError(f'Ожидалась скобка "(", получена лексема "{self.get_lexema()}"')
            self.gl()
            self.EXPR()
            if self.get_lexema() != ')':
                raise SyntaxError(f'Ожидалась скобка ")", получена лексема "{self.get_lexema()}"')
        else:
            raise SyntaxError(f'Ошибка в синтаксисе множителя "{self.get_lexema()}"')

    def get_lexema(self): # получить лексему по номеру
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

f = open('14.txt', 'r')
parser = Parser(f)
