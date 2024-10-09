#123312

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
service_words = ['or', 'and', 'not', 'while', 'read', 'for', 'to', 'do',
                 'int', 'float', 'bool', 'write', 'if', 'then']
limiters = ['{', '}', ';', '[', ']', '=', '<>', '<', '<=', '>', '>=',
            '+', '-', '*', '/', '/*', '*/', '(', ')']
digits = '0123456789'
letters = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz'
identifiers = []
states = ['S', 'ID', 'NM', 'ADD', 'END']
state = 'S'

symbol = ' '
numbers = []
word = ''
outputs = []

f = open('1.txt', 'r')

while state != 'END':
    match(state):
        case 'S':
            while symbol == ' ' or symbol == '\t' or symbol == '\n':
                    if symbol == '}':
                        print('')
                    symbol = f.read(1)
            if symbol == '':
                state = 'END'
            elif symbol in letters or symbol == '_':
                state = 'ID'
            elif symbol in digits:
                state = 'NM'
            else:
                state = 'LIM'

        case 'ID':
            while symbol in letters or symbol in digits or symbol =='_':
                word += symbol
                symbol = f.read(1)
            state = 'ADD'

        case 'NM':
            while symbol in digits or symbol == '.':
                word += symbol
                symbol = f.read(1)
            state = 'ADD'

        case 'LIM':
            while symbol != '' and symbol != ' ':
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
                else:
                    if word not in numbers:
                        numbers.append(word)
                    outputs.append([3, numbers.index(word) + 1])
            else:
                state = 'ERR'
            word = ''
            state = 'S'
f.close()
print(outputs)

