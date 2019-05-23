import string
import sys
import re

tokens = {
    2: 'LPAR',
    3: 'token_OPENCOMMENT',
    4: 'op_MULT',
    5: 'token_CLOSECOMMENT',
    7: 'NUMBER',  # token_int
    8: 'token_REAL',
    9: 'NUMBER',  # token_INT
    10: 'token_REAL',
    11: 'NUMBER',
    12: 'token_REAL',
    13: 'DOT',
    14: 'DOTDOT',
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


class Token:
    def __init__(self, state, tok, description):
        self.state = state
        self.tok = tok
        self.description = description

    def __str__(self):
        return "<{0}, {1}>".format(self.description, self.tok)


class Automata:
    # número de estados que o autômato tem
    """
    Gera o autômato com N estados
    """

    symbols = 128
    delta = []
    F = []

    # O autômato possui N estados, as funções delta de mudança de estado e os
    # estados finais
    def __init__(self, n_states):
        # Posição atual para obter o token
        self.start = 0
        self.linha = 1

        self.n_states = n_states
        self.delta = []
        self.F = []

        # set the entire automata to -1
        for i in range(self.n_states):
            line = []
            for j in range(self.symbols):
                line.append(-1)
            self.delta.append(line)

        self.set_transitions()

        # set final states
        for i in range(31):
            self.F.append(i)

    # Definição de todas as transições
    def set_transitions(self):

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

    def set_transition(self, state, symbol, next_state):
        self.delta[state - 1][ord(str(symbol))] = next_state

    def is_final(self, state):
        return True if state - 1 in self.F else False

    def get_transition(self, state, symbol):
        return self.delta[state - 1][ord(str(symbol))]

    def get_token_state(self, state):
        return tokens[state]

    def get_token(self, inpt):
        token = None
        curr_state = 1
        last_final_state = -1

        last_final_pos = 0
        # start = 0

        pos = self.start

        while pos < len(inpt):
            symbol = inpt[pos]
            curr_state = self.get_transition(curr_state, symbol)

            if self.is_final(curr_state):
                last_final_state = curr_state
                last_final_pos = pos

            # Leu algum estado e foi para o inválido
            # Por exemplo, se no primeiro estado ele leu um número, então o
            # proximo não pode ser uma letra. Caso seja, o curr_state
            # retornará -1
            # Dead state
            if curr_state == -1:

                # Chegou ao final. Printar
                if last_final_state is not -1:
                    token_symbol = inpt[self.start:last_final_pos + 1]

                    # Se não for um id ou keyword
                    if last_final_state != 6:
                        token_name = self.get_token_state(last_final_state)

                    else:

                        # Verifica se eh uma keyword
                        if token_symbol.lower() in keywords:
                            token_name = "keyword"
                        else:
                            token_name = "ID"

                    token = Token(last_final_state, token_symbol, token_name)
                    self.start = last_final_pos + 1
                    break
                else:

                    # Atualiza o valor da linha
                    if symbol == '\n':
                        self.linha += 1

                    # Caso de erro
                    if symbol not in [' ', '\n', '\0', '\t']:

                        token_name = "Error: "
                        token_symbol = inpt[self.start]
                        token = Token(last_final_state, token_name,
                                      token_symbol)
                        break

                    self.start += 1
                    curr_state = 1
                    last_final_state = -1

            pos += 1
        if token is not None:
            if token.description == "keyword":
                return token.tok.upper()
            else:
                return token.description.upper()
        else:
            return None


class Parser:
    def __init__(self, automato, inpt):
        self.automato = automato
        self.input = inpt
        self.current = self.automato.get_token(self.input)

    def advance(self):
        # pega o proximo token
        self.current = self.automato.get_token(self.input)
        print("Advance ", self.current)

    def eat(self, token):
        #
        if self.current is not None:
            print("Current", self.current, "Eats", token)
            if self.current == token:
                self.advance()
            else:
                self.error(self.current)
        else:
            if token is not None:
                self.error(token)

    # Productions
    def PROGRAM(self):
        """ 
        program <identificador> (<lista de identificadores>);
        <bloco>.

        """
        if self.current == "PROGRAM":

            self.eat("PROGRAM")
            self.eat("ID")
            self.eat("LPAR")
            self.eat("ID")
            self.BLOCOID()
            self.eat("RPAR")
            self.eat("SEMICOLON")
            self.BLOCO()
            self.eat("DOT")
            print("Funfou")

    def BLOCO(self):
        """
        <bloco> ::= [<parte das declaraçõe de rótulos>]
                    [<parte de definições de tipos>]
                    [<parte de declarações de variáveis>]
                    [<parte de declarações de sub-rotinas>]
                    <comando composto>
        """
        # Declaração de variáveis
        if self.current == "VAR":
            # var id : tipo;
            self.eat("VAR")  # VAR
            self.eat("ID")  # ID
            self.BLOCOID()  # ,ID, ID, ...,
            self.eat("COLON")  # :
            self.TIPO()
            self.eat("SEMICOLON")  # ;
            self.BLOCOVAR()
            self.BLOCO()

        # Rotulos
        elif self.current == "LABEL":
            self.eat("LABEL")
            self.eat("NUMBER")
            self.BLOCOLABEL()
            self.eat("SEMICOLON")
        # Declaração de tipos: type id = tipo;
        elif self.current == "TYPE":
            self.eat("TYPE")
            self.eat("ID")
            self.eat("ASSIGN")
            self.TIPO()
            self.eat("SEMICOLON")
            self.BLOCOTIPO()
        elif self.current == "PROCEDURE":  # procedure id (var x1 : tipo)
            self.eat("PROCEDURE")
            self.eat("ID")
            if self.current == "SEMICOLON":
                self.eat("SEMICOLON")
            elif self.current == "LPAR":
                self.eat("LPAR")

                # x1, x2 ... : type
                if self.current == "ID":
                    self.eat("ID")
                    self.eat("COLON")
                    self.TIPO()
                    
                # VAR x1, x2 ... : type
                elif self.current == "VAR":
                    self.eat("VAR")
                    self.eat("ID")
                    self.eat("COLON")
                    self.TIPO()

                self.BLOCOPROCEDURE()
                self.eat("RPAR")
                self.eat("SEMICOLON")
                self.BLOCO()
        elif self.current == "FUNCTION":
            self.eat("FUNCTION")
        else:
            self.error(self.current)


    def BLOCOID(self):
        """
        {, <identificador>}
        """
        if self.current == "COMMA":  # ,
            self.eat("COMMA")  # eats ,
            self.eat("ID")  # ID
            self.BLOCOID()  # RECURSION OVER ids
        elif self.current == "COLON":
            pass

    def BLOCOVAR(self):
        """
        {<lista de identificadores> : <tipo>}
        """
        if self.current == "ID":
            self.eat("ID")
            self.BLOCOID()
            self.eat("COLON")
            self.TIPO()
            self.eat("SEMICOLON")
            self.BLOCOVAR()

    def TIPO(self):
        """
        <identificador> | array [<indice> {, <indice}] of <tipo>
        """
        if self.current == "ID":
            self.eat("ID")
        elif self.current == "ARRAY":
            self.eat("ARRAY")  # Array
            self.eat("LBRACKET")  # [
            self.eat("NUMBER")  # n
            self.eat("DOTDOT")
            self.eat("NUMBER")
            self.BLOCOINDEX()  # , m
            self.eat("RBRACKET")  # ]
            self.eat("OF")  # of
            self.TIPO()  # Integer, for example

    def BLOCOINDEX(self):
        """
        {, <indice>}
        """
        if self.current == "COMMA":
            self.eat("COMMA")
            self.BLOCOINDEX()
            self.eat("NUMBER")
            self.eat("DOTDOT")
            self.eat("NUMBER")
            self.BLOCOINDEX()

    def BLOCOLABEL(self):

        """
        {, <numero> };
        """
        if self.current == "COMMA":
            self.eat("COMMA")
            self.eat("NUMBER")
            self.BLOCOLABEL()

    def BLOCOTIPO(self):
        """
        <identificador> = <tipo>; ...
        """
        if self.current == "ID":
            self.eat("ID")
            self.eat("ASSIGN")
            self.TIPO()
            self.eat("SEMICOLON")
            self.BLOCOTIPO()

    def BLOCOPROCEDURE(self):
        if self.current == "SEMICOLON":
            self.eat("SEMICOLON")
            if self.current == "ID":
                self.eat("ID")
                self.eat("COLON")
                self.TIPO()
                self.BLOCOPROCEDURE()

                # VAR x1, x2 ... : type
            elif self.current == "VAR":
                self.eat("VAR")
                self.eat("ID")
                self.eat("COLON")
                self.TIPO()
                self.BLOCOPROCEDURE()
            elif self.current == "RPAR":
                pass
            else:
                self.error(self.current)


    def start_parsing(self):
        self.PROGRAM()

    def error(self, error):
        print("Syntatic error at line\n ERROR HANDLING SHOULD BE DONE ")
        exit(-1)


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

    parser = Parser(automato, inpt)
    parser.start_parsing()
