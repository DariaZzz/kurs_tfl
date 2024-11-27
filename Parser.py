from Lexer import Lexer
# P -> DE | OP
# DE -> <тип> ID
# ID -> idID
# OP -> [SOP | POP | OPIF | OPFOR | OPWHILE | OPIN | OPUOT


class Parser:

    lex_types = {'SW': 1, 'LIM': 2, 'ID': 3, 'BIN': 4, 'OCT': 5, 'DEC': 6, 'HEX': 7, 'REAL': 8}
    service_words = {'or': 0, 'and': 1, 'not': 2, 'while': 3, 'read': 4, 'for': 5, 'to': 6, 'do': 7,
                     'int': 8, 'float': 9, 'bool': 10, 'write': 11, 'if': 12, 'then': 13, 'else': 14, 'as': 15, 'true': 16, 'false': 17}  # 1
    limiters = {0: '{', 1: '}', 2: ';', 3: '[', 4: ']', 5: '=', 6: '<>', 7: '<', 8: '<=', 9: '>', 10: '>=',
                11: '+', 12: '-', 13: '*', 14: '/', 15: '(', 16: ')', 17: ',', 18: ':', 19: '\n'}  # 2
    lex_num = 0
    lex = []
    lex_value = ''
    lex_type = -1
    errorMessage = ''

    def __init__(self, f): # конструктор
        self.lexer = Lexer(f)
        self.run()

    def gl(self): # взять лексему
        if self.lex_num < len(self.lexer.outputs):
            self.lex = self.lexer.outputs[self.lex_num]
            self.lex_value = self.lexer.outputs[self.lex_num][1]
            self.lex_type = self.lexer.outputs[self.lex_num][0]
            self.lex_num += 1
        else:
            self.lex = []
            self.lex_value = ''
            self.lex_type = -1

    def run(self):
        self.gl()
        self.P1()

    def P1(self):
        if self.lex_type == self.lex_types['LIM'] and self.lex_value == self.limiters['{']:
            self.gl()
            self.P()
        else:
            raise SyntaxError('Неправильное начало программы')
        if self.lex_type != self.lex_types['LIM'] or self.lex_value != self.limiters['}']:
            raise SyntaxError(f'Ожидалось "}}", получено {self.lex_value}')

    # <программа>::= «{» {/ (<описание> | <оператор>) ; /} «}»
    def P(self):
        if self.lex_type == 'SW':
            if self.lex_value == self.service_words['int'] or\
                    self.lex_value == self.service_words['float'] or\
                    self.lex_value == self.service_words['bool']:
                self.gl()
                self.D1()
                if self.lex_type == self.lex_types['LIM'] and self.lex_value == self.limiters[';']:
                    self.gl()
                    self.P()
                else:
                    raise SyntaxError(f'Ожидалось: ";", получено: "{self.lex_value}"')
            op_lexes = ['if', 'for', 'while', 'read', 'write']

            for op_lex in op_lexes:
                if self.lex_value == self.service_words[op_lex]:
                    self.OP()
                    if self.lex_type == self.lex_types['LIM'] and self.lex_value == self.limiters[';']:
                        self.gl()
                        self.P()
                    else:
                        raise SyntaxError(f'Ожидалось: ";", получено: "{self.lex_value}"')
                    break
        elif self.lex_type == 'LIM':
            if self.lex_value == self.limiters['[']:
                self.OP()
                if self.lex_type == self.lex_types['LIM'] and self.lex_value == self.limiters[';']:
                    self.gl()
                    self.P()
                else:
                    raise SyntaxError(f'Ожидалось: ";", получено: "{self.lex_value}"')
        elif self.lex_type == 'ID':
            self.OP()
            if self.lex_type == self.lex_types['LIM'] and self.lex_value == self.limiters[';']:
                self.gl()
                self.P()
            else:
                raise SyntaxError(f'Ожидалось: ";", получено: "{self.lex_value}"')
        else:
            raise SyntaxError
        # if self.lex_type == self.lex_types['LIM'] and self.lex_value == self.limiters[';']:
        #     self.gl()
        #     self.P()
        # elif self.lex_type == self.lex_types['LIM'] and self.lex_value == self.limiters['}']:
        #     return
        # else:
        #     raise SyntaxError(f'Ожидалось: ";", получено: "{self.lex_value}"')
        # посмотреть потом проверку на конец строки и конец программы


        # elif

    # <описание>::= <тип> <идентификатор> { , <идентификатор> }
    # D1 -> <тип> D { , D }
    def D1(self):
        self.D()
        while self.lex_type == self.lex_types['LIM'] and\
                self.lex_value == self.limiters[',']:
            self.gl()
            self.D()


    def D(self):
        if self.lex_type != self.lex_types['ID']:
            raise SyntaxError(f'Ожидался идентификатор, получена лексема "{self.lex_value}"')
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
                raise SyntaxError(f'Неопознанный ограничитель в начале оператора: "{self.lex_value}"')
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
                raise SyntaxError(f'Неопознанная лексема начала оператора: "{self.lex_value}"')

    # <присваивания>::= <идентификатор> as <выражение>
    def AOP(self):
        if self.lex_type != self.lex_types['SW'] or\
            self.lex_value != self.service_words['as']:
            raise SyntaxError(f'Ожидалось "as", получено "{self.lex_value}"')
        self.gl()
        self.EXPR()

    # <составной>::= «[» <оператор> { ( : | перевод строки) <оператор> } «]»
    def MULTI_OP(self):
        pass

    # <условный>::= if <выражение> then <оператор> [ else <оператор>]
    def IFOP(self):
        self.EXPR()
        if self.lex_type != self.lex_types["SW"] or\
                self.lex_value != self.service_words['then']:
            raise SyntaxError(f'Ожидалось "then", получено "{self.lex_value}"')
        self.gl()
        self.OP()
        if self.lex_type == self.lex_types['SW'] and\
                self.lex_value == self.service_words['else']:
            self.gl()
            self.OP()

    # <фиксированного_цикла>::= for <присваивания> to <выражение> do
    # <оператор>
    def FOROP(self):
        if self.lex_type != self.lex_types['ID']:
            raise SyntaxError(f'Ожидался идентификатор, получена лексема "{self.lex_value}"')
        self.gl()
        self.AOP()
        if self.lex_type != self.lex_types['SW'] or\
            self.lex_value != self.service_words['to']:
            raise SyntaxError(f'Ожидался "to", получена лексема "{self.lex_value}"')
        self.gl()
        self.EXPR()
        if self.lex_type != self.lex_types['SW'] or \
                self.lex_value != self.service_words['do']:
            raise SyntaxError(f'Ожидался "do", получена лексема "{self.lex_value}"')
        self.gl()
        self.OP()


    def WHILEOP(self):
        self.EXPR()
        if self.lex_type != self.lex_types['SW'] or \
                self.lex_value != self.service_words['do']:
            raise SyntaxError(f'Ожидался "do", получена лексема "{self.lex_value}"')
        self.gl()
        self.OP()

    # <ввода>::= read «(»<идентификатор> {, <идентификатор> } «)»
    def ROP(self):
        if self.lex_type != self.lex_types['LIM'] or \
                self.lex_value != self.service_words['(']:
            raise SyntaxError(f'Ожидалась скобка "(", получена лексема "{self.lex_value}"')
        self.gl()
        self.D()
        while self.lex_type == self.lex_types['LIM'] and\
            self.lex_value == self.limiters[',']:
            self.gl()
            self.D()
        if self.lex_type != self.lex_types['LIM'] or \
                self.lex_value != self.service_words[')']:
            raise SyntaxError(f'Ожидалась скобка ")", получена лексема "{self.lex_value}"')

    # <вывода>::= write «(»<выражение> {, <выражение> } «)»
    def WOP(self):
        if self.lex_type != self.lex_types['LIM'] or \
                self.lex_value != self.service_words['(']:
            raise SyntaxError(f'Ожидалась скобка "(", получена лексема "{self.lex_value}"')
        self.gl()
        self.EXPR()
        while self.lex_type == self.lex_types['LIM'] and \
                self.lex_value == self.limiters[',']:
            self.gl()
            self.EXPR()
            # self.gl()
        if self.lex_type != self.lex_types['LIM'] or \
                self.lex_value != self.service_words[')']:
            raise SyntaxError(f'Ожидалась скобка ")", получена лексема "{self.lex_value}"')

    # <выражение>::= <операнд>{<операции_группы_отношения> <операнд>}
    # сама проверяет
    def EXPR(self):
        self.OPER()
        while self.lex_type == self.lex_types['LIM'] and \
                (self.lex_value == self.limiters['<>'] or
                 self.lex_value == self.limiters['='] or
                 self.lex_value == self.limiters['<'] or
                 self.lex_value == self.limiters['<='] or
                 self.lex_value == self.limiters['>'] or
                 self.lex_value == self.limiters['>='] ):
            self.gl()
            self.OPER()

    # <операнд>::= <слагаемое> {<операции_группы_сложения> <слагаемое>}
    def OPER(self): # операнд
        self.SUMM()
        while self.lex_type == self.lex_types['LIM'] and \
                (self.lex_value == self.limiters['+'] or
                 self.lex_value == self.limiters['-']) or \
                self.lex_type == self.lex_types['SW'] and \
                self.lex_value == self.service_words['or']:
            self.gl()
            self.SUMM()

    # <слагаемое>::= <множитель> {<операции_группы_умножения> <множитель>}
    def SUMM(self):
        self.MUL()
        while self.lex_type == self.lex_types['LIM'] and \
                (self.lex_value == self.limiters['*'] or
                self.lex_value == self.limiters['/']) or \
                self.lex_type == self.lex_types['SW'] and \
                self.lex_value == self.service_words['and']:
            self.gl()
            self.MUL()

    # <множитель>::= <идентификатор> | <число> | <логическая_константа> |
    #  <унарная_операция> <множитель> | «(»<выражение>«)»
    def MUL(self):
        if self.lex_type == self.lex_types['ID']:
            return
        elif self.lex_type == self.lex_types['BIN'] or \
                self.lex_type == self.lex_types['OCT'] or\
                self.lex_type == self.lex_types['DEC'] or\
                self.lex_type == self.lex_types['HEX'] or\
                self.lex_type == self.lex_types['REAL']:
            return
        elif self.lex_type == self.lex_types['SW']:
            if self.lex_value == self.service_words['true'] or\
                self.lex_value == self.service_words['false']:
                return
            elif self.lex_value == self.service_words['not']:
                self.gl()
                self.MUL()
            else:
                raise SyntaxError(f'Ошибка в синтаксисе множителя "{self.lex_value}"')
        elif self.lex_type == self.lex_types['LIM']:
            if self.lex_value != self.limiters['(']:
                raise SyntaxError(f'Ожидалась скобка "(", получена лексема "{self.lex_value}"')
            self.gl()
            self.EXPR()
            # self.gl()
            if self.lex_value != self.limiters[')']:
                raise SyntaxError(f'Ожидалась скобка ")", получена лексема "{self.lex_value}"')
        else:
            raise SyntaxError(f'Ошибка в синтаксисе множителя "{self.lex_value}"')
        self.gl()













