import re

class Lexer:
    service_words = ['or', 'and', 'not', 'while', 'read', 'for', 'to', 'do',
                     'int', 'float', 'bool', 'write', 'if', 'then', 'else', 'as', 'true', 'false'] #1
    limiters = ['{', '}', ';', '[', ']', '=', '<>', '<', '<=', '>', '>=',
                '+', '-', '*', '/', '(', ')', ',', ':', '\n'] #2
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
