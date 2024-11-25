#123312

# <выражение>::= <операнд>{<операции_группы_отношения> <операнд>}
# <операнд>::= <слагаемое> {<операции_группы_сложения> <слагаемое>}
# <слагаемое>::= <множитель> {<операции_группы_умножения> <множитель>}
# <множитель>::= <идентификатор> | <число> | <логическая_константа> |
#  <унарная_операция> <множитель> | «(»<выражение>«)»
# <число>::= <целое> | <действительное>
# <логическая_константа>::= true | false

# <идентификатор>::= <буква> {<буква> | <цифра>}
# <буква>::= A | B | C | D | E | F | G | H | I | J | K | L | M | N | O | P | Q | R | S | T |
#  U | V | W | X | Y | Z | a | b | c | d | e | f | g | h | i | j | k | l | m | n | o | p
#  q | r | s | t | u | v | w | x | y | z
# <цифра>::= 0 | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9

# <целое>::= <двоичное> | <восьмеричное> | <десятичное> |
#  <шестнадцатеричное>
# <двоичное>::= {/ 0 | 1 /} (B | b)
# <восьмеричное>::= {/ 0 | 1 | 2 | 3 | 4 | 5 | 6 | 7 /} (O | o)
# <десятичное>::= {/ <цифра> /} [D | d]
# <шестнадцатеричное>::= <цифра> {<цифра> | A | B | C | D | E | F | a | b |
#  c | d | e | f} (H | h)

# <действительное>::= <числовая_строка> <порядок> |
#  [<числовая_строка>] . <числовая_строка> [порядок]
# <числовая_строка>::= {/ <цифра> /}
# <порядок>::= ( E | e )[+ | -] <числовая_строка>


# Операции языка
# <операции_группы_отношения>:: = < > | = | < | <= | > | >=
# <операции_группы_сложения>:: = + | - | or
# <операции_группы_умножения>::= * | / | and
# <унарная_операция>::= not

# Структура программы
# <программа>::= «{» {/ (<описание> | <оператор>) ; /} «}»

# Синтаксис команд описания данных
# <описание>::= <тип> <идентификатор> { , <идентификатор> }

# Описание типов данных
# <тип>::= int | float | bool

# <оператор>::= <составной> | <присваивания> | <условный> |
#  <фиксированного_цикла> | <условного_цикла> | <ввода> |
#  <вывода>

# Синтаксис составного оператора
# <составной>::= «[» <оператор> { ( : | перевод строки) <оператор> } «]»

# Синтаксис оператора присваивания
# <присваивания>::= <идентификатор> as <выражение>

# Синтаксис оператора условного перехода
# <условный>::= if <выражение> then <оператор> [ else <оператор>]

# Синтаксис оператора цикла с фиксированным числом повторений
# <фиксированного_цикла>::= for <присваивания> to <выражение> do
# <оператор>

# Синтаксис условного оператора цикла
# <условного_цикла>::= while <выражение> do <оператор>

# Синтаксис оператора ввода
# <ввода>::= read «(»<идентификатор> {, <идентификатор> } «)»

# Синтаксис оператора вывода
# <вывода>::= write «(»<выражение> {, <выражение> } «)»
# /**/ - многострочные комментарии

import re

class Lexer:
    service_words = ['or', 'and', 'not', 'while', 'read', 'for', 'to', 'do',
                     'int', 'float', 'bool', 'write', 'if', 'then', 'else', 'as', 'true', 'false'] #1
    limiters = ['{', '}', ';', '[', ']', '=', '<>', '<', '<=', '>', '>=',
                '+', '-', '*', '/', '(', ')', ','] #2
    digits = '0123456789'
    letters = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz'
    identifiers = [] #3
    states = ['S', 'ID', 'NM', 'ADD', 'END', 'ERR', 'COMM']
    state = 'S'

    symbol = ' '
    numbers_bin = [] #4
    numbers_oct = [] #5
    numbers_dec = [] #6
    numbers_hex = [] #7
    numbers_real = [] #8
    word = ''
    outputs = []
    errorMessage = ''

    def checkNum(self, num):
        if num[0] == 0:
            return True
        if num[-1] in 'Bb' and len(num) > 1:
            for n in num[:-1:]:
                if n not in '01':
                    return True
        elif num[-1] in 'Oo':
            for n in num[:-1:]:
                if n not in '01234567':
                    return True
        elif (num[-1] in self.digits or num[-1] in 'Dd') and num.count('.') == 0 and num.count('E') == 0 and num.count('e') == 0:
            for n in num[:-1:]:
                if n not in self.digits:
                    return True
        elif num[-1] in 'Hh' and len(num) > 1:
            for n in self.digits:
                if n not in self.digits and n not in 'ABCDEFabcdef':
                    return True
        else:
            if self.word.count('.') == 0:
                check = re.compile('\d+([Ee][+-]?\d+)?')
            else:
                check = re.compile('\d*\.\d+([Ee][+-]?\d+)?')
            if not re.match(check, self.word):
                return True
        return False

    def __init__(self, f):
        self.run(f)


    def run(self, f):
        while self.state != 'END':
            match self.state:
                case 'S':
                    while self.symbol == ' ' or self.symbol == '\t' or self.symbol == '\n':
                        self.symbol = f.read(1)
                    if self.symbol == '':
                        self.state = 'END'
                    elif self.symbol in self.letters:
                        self.state = 'ID'
                    elif self.symbol in self.digits or self.symbol == '.':
                        self.state = 'NM'
                    elif self.symbol == '/':
                        self.state = 'COMM'
                    else:
                        self.state = 'LIM'

                case 'ID':
                    while self.symbol in self.letters or self.symbol in self.digits or self.symbol == '_':
                        self.word += self.symbol
                        self.symbol = f.read(1)
                    if self.symbol != ' ' and self.symbol != '' and self.symbol != '\n' and self.symbol != '\t':
                        while self.symbol != ' ' and self.symbol != '' and self.symbol != '\n' and self.symbol != '\t':
                            self.word += self.symbol
                            self.symbol = f.read(1)
                        self.state = 'ERR'
                        self.errorMessage = f'Ошибка в лексеме "{self.word}".'
                    else:
                        self.state = 'ADD'

                case 'NM':
                    while self.symbol != '' and self.symbol != ' ' and (self.symbol in self.digits or self.symbol in 'ABCDEFOabcdefo+-.'):
                        self.word += self.symbol
                        self.symbol = f.read(1)
                    if self.symbol == ' ' or self.symbol == '' or self.symbol == '\n' or self.symbol == '\t':
                        if self.checkNum(self.word):
                            self.state = 'ERR'
                            self.errorMessage = f'Неверный формат числа "{self.word}". Повторите попытку.'
                        else:
                            self.state = 'ADD'
                    else:
                        while not (self.symbol == ' ' or self.symbol == '' or self.symbol == '\n' or self.symbol == '\t'):
                            self.word += self.symbol
                            self.symbol = f.read(1)
                        self.state = 'ERR'
                        self.errorMessage = f'Неверный формат числа "{self.word}". Проверьте символы и повторите попытку.'

                case 'COMM':
                    while '*/' not in self.word and self.symbol != '':
                        self.word += self.symbol
                        self.symbol = f.read(1)
                    if self.symbol == '':
                        self.state = 'ERR'
                        self.errorMessage = f'Комментарий  "{self.word}" не закрыт.'
                    else:
                        self.word = ''
                        self.state = 'S'
                case 'LIM':
                    while self.symbol != ' ' and self.symbol != '' and self.symbol != '\n' and self.symbol != '\t':
                        self.word += self.symbol
                        self.symbol = f.read(1)
                    self.state = 'ADD'

                case 'ADD':
                    if self.word in self.service_words:
                        self.outputs.append([1, self.service_words.index(self.word)])
                    elif self.word in self.limiters:
                        self.outputs.append([2, self.limiters.index(self.word)])
                    elif self.word != '':
                        if self.word[0] in self.letters:
                            if self.word not in self.identifiers:
                                self.identifiers.append(self.word)
                            self.outputs.append([3, self.identifiers.index(self.word)])
                        elif self.word[0] in self.digits or self.word[0] == '.':
                            if self.word[-1] in 'Bb':
                                if self.word not in self.numbers_bin:
                                    self.numbers_bin.append(self.word)
                                self.outputs.append([4, self.numbers_bin.index(self.word)])
                            elif self.word[-1] in 'Oo':
                                if self.word not in self.numbers_oct:
                                    self.numbers_oct.append(self.word)
                                self.outputs.append([5, self.numbers_oct.index(self.word)])
                            elif self.word[-1] in 'Hh':
                                if self.word not in self.numbers_hex:
                                    self.numbers_hex.append(self.word)
                                self.outputs.append([7, self.numbers_hex.index(self.word)])
                            elif (self.word[-1] in self.digits or self.word[-1] in 'Dd') and self.word.count('.') == 0\
                                  and self.word.count('E') == 0 and self.word.count('e') == 0:
                                if self.word not in self.numbers_dec:
                                    self.numbers_dec.append(self.word)
                                self.outputs.append([6, self.numbers_dec.index(self.word)])
                            else:
                                if self.word not in self.numbers_real:
                                    self.numbers_real.append(self.word)
                                self.outputs.append([8, self.numbers_real.index(self.word)])
                        else:
                            self.state = 'ERR'
                            self.errorMessage = f'Ошибка в лексеме "{self.word}"'
                    else:
                        self.state = 'ERR'
                        self.errorMessage = f'Слово пустое....{self.symbol}'
                    if self.state != 'ERR':
                        self.word = ''
                        self.state = 'S'
                case 'ERR':
                    print(self.errorMessage)
                    self.state = 'END'
                    exit(1)

f = open('8.txt', 'r')
lexer = Lexer(f)
print(lexer.outputs)
# print(lexer.errorMessage)
f.close()
