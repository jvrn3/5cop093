import string
import sys
from tokens import *
import re
def removeComment(inpt):
    comment_regex = re.compile(r"\(\*.*?\*\)", re.DOTALL)
    inpt = re.sub(comment_regex, "", inpt)
    return inpt

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

        #set the entire automata to -1
        for i in range(self.n_states):
            line = []
            for j in range(self.symbols):
                line.append(-1)
            self.delta.append(line)

        #A-Za-z IDS AND KEYWORDS
        for letter in string.ascii_letters:
            self.set_transition(1, letter, 6)
            self.set_transition(6, letter, 6)

        #_
        self.set_transition(6, '_', 6)

        #0-9
        for number in range(9):
            self.set_transition(6, number, 6)
            self.set_transition(7, number, 7)
            self.set_transition(8, number, 8)
            self.set_transition(9, number, 9)
            self.set_transition(10, number, 10)
            self.set_transition(1, number, 11)
            self.set_transition(11, number, 11)
            self.set_transition(12, number, 12)

        #Parenteses ou abre comentário
        self.set_transition(1, '(', 2 )
        self.set_transition(2, '*', 3)

        self.set_transition(1, '*', 4)
        self.set_transition(4, ')', 5)

        self. set_transition(1, '+',7 )
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

        for i, special in enumerate(['{', '}', '[', ']', ',', ';', '=', ')', '\"', '\''], 22) :
            self.set_transition(1, special, i)
        
        #set final states
        # 1 a 31
        for i in range(31):
            self.F.append(i)

    def set_transition(self, state, symbol, next_state):
        # print(state)
        self.delta[state-1][ord(str(symbol))] = next_state

    def is_final(self, state):
        return True if state -1 in self.F else False 

    def get_transition(self,state, symbol):
        return self.delta[state-1][ord(str(symbol))]

    #

if __name__ == '__main__':


    if len(sys.argv)!= 2:
        print("usage: python lexico.py file.txt")
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

    last_final_pos= 0
    start = 0
    pos = 0
    while pos < len(inpt):
        symbol = inpt[pos]
        curr_state = automato.get_transition(curr_state, symbol)
        # print("Symbol ",  symbol, "Curr", curr_state, "last_f", last_final_pos, end=" " )
        # print()

        if automato.is_final(curr_state):
            last_final = curr_state
            last_final_pos = pos

        #Quando le algum estado inválido
        if curr_state == -1:

            #estado final
            if last_final != -1:
                if last_final != 6:
                    print("< "   + tokens[last_final] + ", " +inpt[start:last_final_pos+1] +" >")
                else:
                    if inpt[start:last_final_pos +1] in keywords:
                        print("< keyword, " + inpt[start:last_final_pos+1] + " >")
                    else:
                        print("< identifier," , inpt[start:last_final_pos+1] + " >")

                start = last_final_pos +1
            else:
                if symbol not in [' ', '\n', '\0', '\t']:
                    print("Error " +inpt[start::])
                start+=1

            pos = start-1
            curr_state = 1
            last_final = -1

        pos+=1
