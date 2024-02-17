from definitions import Definitions

class Token:
    def __init__(self, type, value):
        self.type = type
        self.value = value

    def __str__(self):
        return f"Token({self.type}, {self.value})"

    def __repr__(self) -> str:
        return self.__str__()


class Lexer:
    def __init__(self, text):
        self.text = text
        self.pos = 0
        self.current_char = self.text[self.pos]
        
    def error(self):
        raise Exception("Invalid character", self.current_char, ord(self.current_char))

    def advance(self):
        self.pos += 1
        if self.pos > len(self.text) - 1:
            self.current_char = None
        else:
            self.current_char = self.text[self.pos]

    def make_number(self):
        result = ""
        while self.current_char is not None and self.current_char.isdigit():
            result += self.current_char
            self.advance()
        return result

    def make_word(self):
        result = ""
        while self.current_char is not None and self.current_char != '\n':
            if self.current_char == ' ':
                result += self.handle_whitespace()
            result += self.current_char
            self.advance()
        return result

    def make_heading(self):
        result = ""
        token_type = None
        while self.current_char is not None and self.current_char == '#':
            result += self.current_char
            self.advance()
        if len(result) > 6:
            token_type = Definitions.WORD
        elif len(result) == 6:
            token_type = Definitions.HEADING6
        elif len(result) == 5:
            token_type = Definitions.HEADING5
        elif len(result) == 4:
            token_type = Definitions.HEADING4
        elif len(result) == 3:
            token_type = Definitions.HEADING3
        elif len(result) == 2:
            token_type = Definitions.HEADING2
        elif len(result) == 1:
            token_type = Definitions.HEADING1
        else:
            self.error()
        
        if token_type in Definitions.HEADINGS:
            return Token(token_type, None)
        else:
            return Token(Definitions.WORD, None)

    def handle_whitespace(self):
        while self.current_char is not None and self.current_char.isspace():
            self.advance()
        return ' '
    
    def make_list_element(self):
        char = self.current_char
        self.advance()
        return char

    def make_dot(self):
        char = self.current_char
        self.advance()
        return char

    def get_next_token(self):
        while self.current_char is not None:
            #print(ord(self.current_char), f"({self.current_char}-)")

            if self.current_char.isdigit():
                return Token(Definitions.INTEGER, self.make_number())

            if self.current_char == ' ':
                return Token(Definitions.WHITESPACE ,self.handle_whitespace())

            if self.current_char == '.':
                return Token(Definitions.DOT, self.make_dot())

            if self.current_char == '#':
                return self.make_heading()

            if self.current_char == '\n':
                self.advance()
                continue

            if self.current_char.isalpha():
                return Token(Definitions.WORD, self.make_word())
            
            # Unordered list
            if self.current_char in ['-', '*', '+']:
                return Token(Definitions.UNORDERED_LIST_MARKER, self.make_list_element())

            self.error()

        return Token(Definitions.EOF, None)


class List:
    pass

class RootList:
    def __init__(self):
        self.start_tag = '<html>'
        self.end_tag = '</html>'
        self.list = []
    
    def __str__(self):
        return f"RootList({self.list})"

    def __repr__(self) -> str:
        return self.__str__()

class UnorderedList(List):
    def __init__(self):
        self.start_tag = '<ul>'
        self.end_tag = '</ul>'
        self.list = []

    def __str__(self):
        return f"UnorderedList({self.list})"

    def __repr__(self) -> str:
        return self.__str__()

class OrderedList(List):
    def __init__(self):
        self.start_tag = '<ol>'
        self.end_tag = '</ol>'
        self.list = []

    def __str__(self):
        return f"OrderedList({self.list})"

    def __repr__(self) -> str:
        return self.__str__()


class Parser:
    def __init__(self, lexer):
        self.lexer = lexer
        self.current_token = self.lexer.get_next_token()
        self.qu = RootList()
    def error(self):
        raise Exception('Invalid Syntax')


    def eat(self, type):
        if self.current_token.type == type:
            self.current_token = self.lexer.get_next_token()
        else:
            self.error()

    def markdown(self):
        while self.current_token.type != Definitions.EOF:
 
            self.qu.list.append(self.block())

    def block(self):
        if self.current_token.type in Definitions.HEADINGS:
            return self.heading()
        if self.current_token.type == Definitions.WORD or self.current_token.type == Definitions.WHITESPACE:
            return self.paragraph()
        if self.current_token.type == Definitions.UNORDERED_LIST_MARKER:
            return self.unordered_list()
        if self.current_token.type == Definitions.INTEGER:
            return self.ordered_list()
        self.error()


    def heading(self):
        token = self.current_token
        self.eat(token.type)
        if self.current_token.type == Definitions.WHITESPACE:
            token.type = token.type
            self.eat(Definitions.WHITESPACE)
        else:
            token.type = Definitions.PARAGRAPH
        token.value = self.current_token.value
        self.eat(Definitions.WORD)
        return token
    
    def paragraph(self):
        token = self.current_token
        """
        while self.current_token == Definitions.WHITESPACE:
            token.value += ' '
            print(self.current_token)
            self.eat(Definitions.WHITESPACE)
        """
        
        if self.current_token.type == Definitions.WHITESPACE:
            self.eat(Definitions.WHITESPACE)
        
        token.value = self.current_token.value
        self.eat(Definitions.WORD)
        token.type = Definitions.PARAGRAPH
        return token

    def unordered_list(self):
        list = UnorderedList()
        while self.current_token.type == Definitions.UNORDERED_LIST_MARKER:
            marker_token = self.current_token
            self.eat(Definitions.UNORDERED_LIST_MARKER)


            if self.current_token.type == Definitions.WORD:
                token = self.paragraph()
                token.value = marker_token.value + token.value
                list.list.append(token)
                continue


            self.eat(Definitions.WHITESPACE)
            token = self.current_token
            self.eat(Definitions.WORD)
            token.type = Definitions.UNORDERED_LIST_ELEMENT
            list.list.append(token)
        return list

        """
        while self.current_token.type in [Definitions.WORD, Definitions.UNORDERED_LIST_MARKER]:
            print(self.current_token)
            self.eat(Definitions.UNORDERED_LIST_MARKER)
            token = self.current_token
            print(token)
            self.eat(Definitions.WORD)
            # TODO: get unordered list element as seperate token, not as paragraph
            token.type = Definitions.UNORDERED_LIST_ELEMENT
            list.list.append(token)
        return list
        """

    def ordered_list(self):
        list = OrderedList()

        while self.current_token.type == Definitions.INTEGER:
            marker_token = self.current_token
            self.eat(Definitions.INTEGER)
            if self.current_token.type == Definitions.DOT:
                self.eat(Definitions.DOT)

                if self.current_token.type != Definitions.WHITESPACE:
                    token = self.paragraph()
                    token.value = marker_token.value + '.' + token.value
                    return token


                self.eat(Definitions.WHITESPACE)
                token = self.current_token
                self.eat(Definitions.WORD)
                token.type = Definitions.ORDERED_LIST_ELEMENT
                print(token)
                list.list.append(token)
                continue


            if self.current_token.type == Definitions.WHITESPACE:
                marker_token.value += ' '
            token = self.paragraph()
            token.value = marker_token.value + token.value
            return token

        return list  
     
        """
        list = OrderedList()
        integer = self.current_token
        self.eat(Definitions.INTEGER)
        if self.current_token.type == Definitions.DOT:
            self.eat(Definitions.DOT)
            self.eat(Definitions.WHITESPACE)
            token = self.current_token
            return
        """


class Interpreter:
    def __init__(self, parser):
        self.parser = parser

    def print_token(self, token):
        print(f"<{token.type}>")
        print(token.value)
        print(f"</{token.type}>")

    def print_list(self, list):
        print(list.start_tag)
        for i in list.list:
            if isinstance(i, UnorderedList) or isinstance(i, OrderedList):
                self.print_list(i)
                continue
            self.print_token(i)
        print(list.end_tag)

    def convert_to_html(self):
        self.print_list(self.parser.qu)

    def interpret(self):
        self.parser.markdown()
        self.convert_to_html()

if __name__ == "__main__":
    text = "### Heading\ndeneme1234\n- a\n-a\nasdasd\n1asdadasd"
    
    
    I = Interpreter(Parser(Lexer(text)))
    I.interpret()
    

    """
    L = Lexer(text)
    token = L.get_next_token()
    while token.type != Definitions.EOF:
        print(token)
        token = L.get_next_token()
    """




