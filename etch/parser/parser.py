from sly import Parser
from etch.parser.lexer import EtchLexer

class EtchParser(Parser):
    tokens = EtchLexer.tokens

    precedence = (
        ('nonassoc', LT, GT, LE, GE, EQ, NE),
        ('left', ADD, SUB),
        ('left', MUL, TRUEDIV, FLOORDIV, MOD),
        ('right', UMINUS),
    )

    @_("statements statement",
       "statement")
    def statements(self, p):
        o = []
        if len(p) == 1:
            if p[0]:
                o.append(p[0])
        else:
            o = p[0] if p[0] else []
            if p[1]:
                o.append(p[1])
        return o

    @_("command NEWLINE")
    def statement(self, p):
        return p.command

    @_('')
    def empty(self, p):
        pass
    
    @_("empty",
       "expr",
       "if_block",
       "for_block",
       "while_block",
       "forever_block",
       "count_block",
       "assign",
       "somecrement")
    def command(self, p):
        return p[0]


    @_("args expr",
       "expr")
    def args(self, p):
        o = []
        if len(p) == 1:
            if p[0]:
                o.append(p[0])
        else:
            o = p[0] if p[0] else []
            if p[1]:
                o.append(p[1])
        return o

    @_("IF expr THEN NEWLINE statements DONE")
    def if_block(self, p):
        return ("BLOCK", ("IF", [None, p[1], p[4], None]))
    @_("IF expr THEN NEWLINE statements ELSE NEWLINE statements DONE")
    def if_block(self, p):
        return ("BLOCK", ("IF", [None, p[1], p[4], p[7]]))
    @_("IF expr THEN NEWLINE statements elifs DONE")
    def if_block(self, p):
        return ("BLOCK", ("IF", [p[5], p[1], p[4], None]))
    @_("IF expr THEN NEWLINE statements elifs ELSE NEWLINE statements DONE")
    def if_block(self, p):
        return ("BLOCK", ("IF", [p[5], p[1], p[4], p[8]]))
    @_("IF error THEN NEWLINE statements DONE",
       "IF error THEN NEWLINE statements ELSE NEWLINE statements DONE",
       "IF error THEN NEWLINE statements elifs DONE",
       "IF error THEN NEWLINE statements elifs ELSE NEWLINE statements DONE")
    def if_block(self, p):
        print("Syntax error in if statement, make sure you didn't use elif instead of else if.")
    @_("elifs elif_block",
       "elif_block")
    def elifs(self, p):
        o = []
        if len(p) == 1:
            if p[0]:
                o.append(p[0])
        else:
            o = p[0] if p[0] else []
            if p[1]:
                o.append(p[1])
        return o
    @_("ELSE IF command THEN statements")
    def elif_block(self, p):
        return (p.command, p.statements)

    @_("WHILE command DO statements DONE")
    def while_block(self, p):
        return ("BLOCK", ("WHILE", [p[1], p[3]]))
    @_("FOR ID IN command DO statements DONE")
    def for_block(self, p):
        return ("BLOCK", ("FOR", [p[1], p[3], p[5]]))
    @_("DO statements FOREVER")
    def forever_block(self, p):
        return ("BLOCK", ("FOREVER", p[1]))
    @_("DO NEWLINE statements expr TIMES")
    def count_block(self, p):
        return ("BLOCK", ("COUNT", [p[2], p[3]]))
    @_("expr ADD expr",
       "expr SUB expr",
       "expr MUL expr",
       "expr TRUEDIV expr",
       "expr FLOORDIV expr",
       "expr MOD expr",
       "expr EXP expr")
    def expr(self, p):
        return ("EXPRESSION", ("MATH", (p[1], [p.expr0, p.expr1])))
    @_("expr LT expr",
       "expr GT expr",
       "expr LE expr",
       "expr GE expr",
       "expr EQ expr",
       "expr NE expr")
    def expr(self, p):
        return ("EXPRESSION", ("LOGIC", (p[1], [p.expr0, p.expr1])))
    @_('SUB expr %prec UMINUS')
    def expr(self, p):
       return ("EXPRESSION", ("MATH", (p[0], [0, p.expr])))
    @_("NOT expr")
    def expr(self, p):
        return ("EXPRESSION", ("LOGIC", ("NOT", [p.expr])))
        
    @_("ID INCREMENT",
       "ID DECREMENT")
    def somecrement(self, p):
        return ("SOMECREMENT", (p[1], p[0]))

    @_("ID ASSIGN expr")
    def assign(self, p):
        return ("ASSIGN", [p[0], p[2]])

    @_("ID")
    def expr(self, p):
        return ("VARIABLE", p[0])
    @_("ID COLON ID args SEMICOLON",
       "empty COLON ID args SEMICOLON")
    def expr(self, p):
        return ("EXPRESSION", ("FUNCTION", (p[0], p.ID, p.args)))
    

    @_("INTEGER",
       "FLOAT",
       "STRING")
    def expr(self, p):
        return ("VALUE", p[0])
    @_("list_items COMMA expr",
       "expr")
    def list_items(self, p):
        o = []
        if len(p) == 1:
            if p[0]:
                o.append(p[0])
        else:
            o = p[0] if p[0] else []
            if p[2]:
                o.append(p[2])
        return o
    
    @_("OPEN_SQ list_items CLOSE_SQ")
    def expr(self, p):
        return ("VALUE", p[1])

def parse(code):
    lexer = EtchLexer()
    parser = EtchParser()
    if not code.endswith("\n"):
        code += "\n" # dirty trailing newline hacks
    return parser.parse(lexer.tokenize(code))
        