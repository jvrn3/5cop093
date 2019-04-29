import string
import sys
import re
import time

tokens_prof = {
    2: 'SIMBOLO_ESPECIAL',
    3: 'SIMBOLO_ESPECIAL_COMPOSTO',
    4: 'SIMBOLO_ESPECIAL_COMPOSTO',
    5: 'SIMBOLO_ESPECIAL_COMPOSTO',
    6: 'IDENTIFICADOR',
    7: 'NUMERO_POSITIVO',
    8: 'NUMERO_REAL_POSITIVO',
    9: 'NUMERO_NEGATIVO',
    10: 'NUMERO_REAL_NEGATIVO',
    11: 'NUMERO_INTEIRO',
    12: 'NUMERO_REAL',
    13: 'SIMBOLO_ESPECIAL',
    14: 'SIMBOLO_ESPECIAL_COMPOSTO',
    15: 'SIMBOLO_ESPECIAL',
    16: 'SIMBOLO_ESPECIAL_COMPOSTO',
    17: 'SIMBOLO_ESPECIAL_COMPOSTO',
    18: 'SIMBOLO_ESPECIAL_COMPOSTO',
    19: 'SIMBOLO_ESPECIAL_COMPOSTO',
    20: 'SIMBOLO_ESPECIAL_COMPOSTO',
    21: 'SIMBOLO_ESPECIAL_COMPOSTO',
    22: 'SIMBOLO_ESPECIAL',
    23: 'SIMBOLO_ESPECIAL',
    24: 'SIMBOLO_ESPECIAL',
    25: 'SIMBOLO_ESPECIAL',
    26: 'SIMBOLO_ESPECIAL',
    27: 'SIMBOLO_ESPECIAL',
    28: 'SIMBOLO_ESPECIAL',
    29: 'SIMBOLO_ESPECIAL',
    30: 'SIMBOLO_ESPECIAL_COMPOSTO',
    31: 'SIMBOLO_ESPECIAL'
}

tokens = {
    2: 'LPAR',
    3: 'token_OPENCOMMENT',
    4: 'op_MULT',
    5: 'token_CLOSECOMMENT',
    7: 'token_INT',
    8: 'token_REAL',
    9: 'token_INT',
    10: 'token_REAL',
    11: 'token_INT',
    12: 'token_REAL',
    13: 'DOT',
    14: 'DOT_DOT',
    15: 'COLON',
    16: 'token_ASSIGN',
    17: 'op_LT',
    18: 'op_LE',
    19: 'op_NE',
    20: 'op_GT',
    21: 'op_TE',
    22: 'LCURLYBRACK',
    23: 'RCURLYBRACK',
    24: 'LBRACKET',
    25: 'RBRACKET',
    26: 'COMMA',
    27: 'SEMICOLON',
    28: 'op_EQ',
    29: 'RPAR',
    30: 'DOUBLEQUOTE',
    31: 'SINGLEQUOTE'
}
keywords = [
    "and", "array", "begin", "case", "const", "constructor", "destructor",
    "div", "do", "downto", "else", "end", "file", "for", "function", "goto",
    "if", "inherited", "implementation", "in", "inline", "interface", "label",
    "mod", "nil", "not", "object", "of", "or", "packed", "procedure",
    "program", "record", "repeat", "set", "shl", "shr", "string", "then", "to",
    "type", "unit", "until", "uses", "var", "while", "with"
]


def removeComment(inpt):
    comment_regex = re.compile(r"\(\*.*?\*\)", re.DOTALL)
    inpt = re.sub(comment_regex, "", inpt)
    return inpt


class HashTrabalho:
    def __init__(self):
        self.hash_size = 256
        self.table = [[] for i in range(self.hash_size)]

    # def hash_func(self, word):
    #     hash = 5381
    #     for i in word:
    #         hash = ((hash << 5) + hash) + ord(i)
    #     return hash % self.hash_size
    def hash_func(self, word):
        hash = 0
        alfa = 10
        for i in word:
            hash = alfa * hash + ord(i)
        return hash % self.hash_size

    def insert(self, word):
        return self.table[self.hash_func(word)].append(word)

    def lookup(self, word):
        hash = self.hash_func(word)
        table = self.table[hash]
        for w in table:
            if w == word:
                return True
        return False


class Automata:
    # número de estados que o autômato tem
    """
    Gera o autômato com N estados
    """

    symbols = 128
    delta = []
    F = []

    # O autômato possui N estados, as funções delta e os estados finais

    def __init__(self, n_states):
        self.n_states = n_states
        self.delta = []
        self.F = []

        # set the entire automata to -1
        for i in range(self.n_states):
            line = []
            for j in range(self.symbols):
                line.append(-1)
            self.delta.append(line)

        # A-Za-z IDS AND KEYWORDS
        for letter in string.ascii_letters:
            self.set_transition(1, letter, 6)
            self.set_transition(6, letter, 6)

        # _
        self.set_transition(6, '_', 6)

        # 0-9
        for number in range(9):
            self.set_transition(6, number, 6)
            self.set_transition(7, number, 7)
            self.set_transition(8, number, 8)
            self.set_transition(9, number, 9)
            self.set_transition(10, number, 10)
            self.set_transition(1, number, 11)
            self.set_transition(11, number, 11)
            self.set_transition(12, number, 12)

        # Parenteses ou abre comentário
        self.set_transition(1, '(', 2)
        self.set_transition(2, '*', 3)

        self.set_transition(1, '*', 4)
        self.set_transition(4, ')', 5)

        self.set_transition(1, '+', 7)
        self.set_transition(7, '.', 8)

        self.set_transition(1, '-', 9)
        self.set_transition(9, '.', 10)

        self.set_transition(11, '.', 12)

        self.set_transition(1, '.', 13)

        self.set_transition(13, '.', 14)

        self.set_transition(1, ':', 15)
        self.set_transition(15, '=', 16)

        self.set_transition(1, '<', 17)
        self.set_transition(17, '=', 18)
        self.set_transition(17, '>', 19)

        self.set_transition(1, '>', 20)
        self.set_transition(20, '=', 21)

        #
        for i, special in enumerate(
            ['{', '}', '[', ']', ',', ';', '=', ')', '\"', '\''], 22):
            self.set_transition(1, special, i)

        # set final states
        # 1 a 31
        for i in range(31):
            self.F.append(i)

    def set_transition(self, state, symbol, next_state):
        self.delta[state - 1][ord(str(symbol))] = next_state

    def is_final(self, state):
        return True if state - 1 in self.F else False

    def get_transition(self, state, symbol):
        return self.delta[state - 1][ord(str(symbol))]


if __name__ == '__main__':

    if len(sys.argv) != 2:
        print("usage: python lexico.py file")
        sys.exit(1)

    try:
        file = open(sys.argv[1])
    except IOError:
        print("Error opening the file")
        sys.exit(1)

    inpt = file.read()
    inpt = removeComment(inpt)

    automato = Automata(31)

    print("File name ", sys.argv[1])

    curr_state = 1
    last_final = -1

    last_final_pos = 0
    start = 0
    pos = 0

    linha = 1
    with open("out_file", "w") as out_file:
        while pos < len(inpt):
            symbol = inpt[pos]
            curr_state = automato.get_transition(curr_state, symbol)

            if automato.is_final(curr_state):
                last_final = curr_state
                last_final_pos = pos

            # Leu algum estado e foi para o inválido
            # Por exemplo, se no primeiro estado ele leu um número, então o
            # proximo não pode ser uma letra. Caso seja, o curr_state
            # retornará -1
            if curr_state == -1:
                # Ultimo estado final
                if last_final is not -1:
                    # Se não for um id ou keyword
                    if last_final != 6:
                        # Printa o token indicando o estado, e a palavra lida
                        # Por exemplo, <Símbolo especial, : >
                        out_file.write("<" + tokens_prof[last_final] + ", " +
                                       inpt[start:last_final_pos + 1] + " >\n")

                        print("< " + tokens[last_final] + ", " +
                              inpt[start:last_final_pos + 1] + " >")
                    else:
                        if inpt[start:last_final_pos + 1].lower() in keywords:
                            out_file.write("<keyword, " +
                                           inpt[start:last_final_pos + 1] +
                                           " >\n")

                            print("<keyword, " +
                                  inpt[start:last_final_pos + 1] + " >")
                        else:
                            print("< identifier,",
                                  inpt[start:last_final_pos + 1] + " >")
                            out_file.write("< identifier, " +
                                           inpt[start:last_final_pos + 1] +
                                           " >\n")

                    start = last_final_pos + 1
                else:
                    if symbol == '\n':
                        linha += 1
                    if symbol not in [' ', '\n', '\0', '\t']:
                        out_file.write("Erro na linha {0}".format(linha) +
                                       "=> caracter invalido:" + inpt[start] +
                                       "\n")

                        print("Erro na linha", linha, "=> caracter invalido:",
                              inpt[start])
                        print("...Parando programa...")
                        time.sleep(1)

                        break

                    start += 1

                pos = start - 1
                curr_state = 1
                last_final = -1

            pos += 1
