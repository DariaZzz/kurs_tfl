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

my_code = input()
id = ''
outputs = []
for i in range(len(my_code)):
    a = my_code[i]
    if a != ' ':
        id += a
        if id in service_words:
            outputs.append([1, service_words.index(id)+1])
            id = ''
        elif id in limiters:
            outputs.append([2, limiters.index(id)+1])
            id = ''
    elif id != '':
        if id not in identifiers:
            identifiers.append(id)
        outputs.append([4, identifiers.index(id)+1])
        id = ''

print(outputs)

