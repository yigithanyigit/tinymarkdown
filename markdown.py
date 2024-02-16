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
        return int(result)

    def make_parapraph(self):
        result = ""
        while self.current_char is not None and self.current_char != '\n' :
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
            token_type = Definitions.PARAGRAPH
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

        if self.current_char.isspace():
            self.handle_whitespace()
            result = self.make_parapraph()
        else:
            result += self.make_parapraph()
            token_type = Definitions.PARAGRAPH
 
        return Token(token_type, result)


    def handle_whitespace(self):
        while self.current_char is not None and self.current_char.isspace():
            self.advance()
        return ' '
    
    def make_list_element(self):
        char = self.current_char
        self.advance()
        return char

    def get_next_token(self):
        while self.current_char is not None:

            if self.current_char.isdigit():
                return Token(Definitions.INTEGER, self.make_number())

            if self.current_char == ' ':
                #return Token(Definitions.WHITESPACE ,self.handle_whitespace())
                self.advance()

            if self.current_char == '#':
                return self.make_heading()

            if self.current_char == '\n':
                self.advance()

            if self.current_char.isalpha():
                return Token(Definitions.PARAGRAPH, self.make_parapraph())
            
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
        if self.current_token.type == Definitions.PARAGRAPH:
            return self.paragraph()
        if self.current_token.type == Definitions.UNORDERED_LIST_MARKER:
            return self.unordered_list()


    def heading(self):
        token = self.current_token
        print(token)
        self.eat(token.type)
        return token
    
    def paragraph(self):
        token = self.current_token
        print(token)
        self.eat(Definitions.PARAGRAPH)
        return token

    def unordered_list(self):
        list = UnorderedList()
        while self.current_token.type in [Definitions.PARAGRAPH, Definitions.UNORDERED_LIST_MARKER]:
            print(self.current_token)
            self.eat(Definitions.UNORDERED_LIST_MARKER)
            token = self.current_token
            print(token)
            self.eat(Definitions.PARAGRAPH)
            # TODO: get unordered list element as seperate token, not as paragraph
            token.type = Definitions.UNORDERED_LIST_ELEMENT
            list.list.append(token)
        return list

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
            if isinstance(i, UnorderedList):
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
    text = "###    Heading\ndeneme1234\n- Deneme\n- Deneme"
    

    I = Interpreter(Parser(Lexer(text)))
    I.interpret()

    """
    while token != Token(Definitions.EOF, None):
        print(token)
        token = l.get_next_token()
    """




