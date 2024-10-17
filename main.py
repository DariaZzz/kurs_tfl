#123312

# <идентификатор>::= <буква> {<буква> | <цифра>}
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

# <программа>::= «{» {/ (<описание> | <оператор>) ; /} «}»
# <описание>::= <тип> <идентификатор> { , <идентификатор> }

# <оператор>::= <составной> | <присваивания> | <условный> |
#  <фиксированного_цикла> | <условного_цикла> | <ввода> |
#  <вывода>

# <составной>::= «[» <оператор> { ( : | перевод строки) <оператор> } «]»
# <присваивания>::= <идентификатор> as <выражение>
# <условный>::= if <выражение> then <оператор> [ else <оператор>]
# <фиксированного_цикла>::= for <присваивания> to <выражение> do
# <оператор>
# <условного_цикла>::= while <выражение> do <оператор>
# <ввода>::= read «(»<идентификатор> {, <идентификатор> } «)»
# <вывода>::= write «(»<выражение> {, <выражение> } «)»
# /**/ - многострочные комментарии

import re

def checkNum(num):
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
    elif (num[-1] in digits or num[-1] in 'Dd') and num.count('.') == 0 and num.count('E') == 0 and num.count('e') == 0:
        for n in num[:-1:]:
            if n not in digits:
                return True
    elif num[-1] in 'Hh' and len(num) > 1:
        for n in digits:
            if n not in digits and n not in 'ABCDEFabcdef':
                return True
    else:
        if word.count('.') == 0:
            check = re.compile('\d+([Ee][+-]?\d+)?')
        else:
            check = re.compile('\d*\.\d+([Ee][+-]?\d+)?')
        if not re.match(check, word):
            return True
    return False


service_words = ['or', 'and', 'not', 'while', 'read', 'for', 'to', 'do',
                 'int', 'float', 'bool', 'write', 'if', 'then', 'as']
limiters = ['{', '}', ';', '[', ']', '=', '<>', '<', '<=', '>', '>=',
            '+', '-', '*', '/', '/*', '*/', '(', ')', ',']
digits = '0123456789'
letters = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz'
identifiers = []
states = ['S', 'ID', 'NM', 'ADD', 'END', 'ERR']
state = 'S'

symbol = ' '
numbers = []
word = ''
outputs = []
errorMessage = ''

f = open('2.txt', 'r')

while state != 'END':
    match state:
        case 'S':
            while symbol == ' ' or symbol == '\t' or symbol == '\n':
                symbol = f.read(1)
            if symbol == '':
                state = 'END'
            elif symbol in letters or symbol == '_':
                state = 'ID'
            elif symbol in digits or symbol == '.':
                state = 'NM'
            else:
                state = 'LIM'

        case 'ID':
            while symbol in letters or symbol in digits or symbol =='_':
                word += symbol
                symbol = f.read(1)
            if symbol != ' ' and symbol != '' and symbol != '\n' and symbol != '\t':
                while symbol != ' ' and symbol != '' and symbol != '\n' and symbol != '\t':
                    word += symbol
                    symbol = f.read(1)
                state = 'ERR'
                errorMessage = f'Ошибка в лексеме {word}'
            else:
                state = 'ADD'

        case 'NM':
            while symbol != '' and symbol != ' ' and (symbol in digits or symbol in 'ABCDEFOabcdefo+-.'):
                word += symbol
                symbol = f.read(1)
            if symbol == ' ' or symbol == '' or symbol == '\n' or symbol == '\t':
                if checkNum(word):
                    state = 'ERR'
                    errorMessage = f'Неверный формат числа {word}. Повторите попытку.'
                else:
                    state = 'ADD'
            else:
                state = 'ERR'
                errorMessage = f'Неверный формат числа {word}. Проверьте символы и повторите попытку.'

        case 'LIM':
            while symbol != ' ' and symbol != '' and symbol != '\n' and symbol != '\t':
                word += symbol
                symbol = f.read(1)
            state = 'ADD'

        case 'ADD':
            if word in service_words:
                outputs.append([1, service_words.index(word) + 1])
            elif word in limiters:
                outputs.append([2, limiters.index(word) + 1])
            elif word != '':
                if word[0] in letters:
                    if word not in identifiers:
                        identifiers.append(word)
                    outputs.append([4, identifiers.index(word) + 1])
                elif word[0] in digits or word[0] == '.':
                    if word not in numbers:
                        numbers.append(word)
                    outputs.append([3, numbers.index(word) + 1])
                else:
                    state = 'ERR'
                    errorMessage = f'Ошибка в синтаксисе лексемы {word}'
            else:
                state = 'ERR'
                errorMessage = f'Слово пустое....{symbol}'
            if state != 'ERR':
                word = ''
                state = 'S'
        case 'ERR':
            print(errorMessage)
            state = 'END'
            exit(1)
f.close()
print(outputs)

