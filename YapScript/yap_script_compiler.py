import sys
import random as b_random
class NotEnoughArgumentsError(Exception):
	def __init__(self):
		super().__init__("Not Enough Arguments!")

class ParsingError(Exception):
	def __init__(self, pos):
		super().__init__(f"Parsing Failed at Token Position: {pos}")

class LibraryNotFound(Exception):
    def __init__(self, lib_name):
        super().__init__(f"Library not found: {lib_name}")

class Token:
	def __init__(self, name, value):
		self.name, self.value = name, value
	def __repr__(self):
		return f"{self.name}: {self.value}"

# Keywords and macros
KeywordTokens = {
	"lowkey": 10,
	"isfinnabe": 11,
	"cooked": 12,
	"when": 13,
	"lit": 14,
	"clapback": 15,
	"then": 16,
	"periodt": 17,
	"airdrop": 18
}

Macros = [
	"yap",
	"grasp"
]

# Check for input file
if len(sys.argv) <= 1: raise NotEnoughArgumentsError

try:
	with open(sys.argv[1], "r") as f:
		code = f.read()
except FileNotFoundError:
	print("File not found, Quitting!")
	quit()

# Token identification function
def idf(token):
	if token.startswith("\"") and token.endswith("\""):
		return "STRING"
	elif token.isdigit():
		return "NUMBER"
	elif token in Macros:
		return "MACRO"
	elif token in KeywordTokens:
		return KeywordTokens[token]
	elif token[0]=="?":
	    return "RETURNFUNCTION"
	else:
		return "IDENTIFIER"

# Tokenizer function
def tokenize(code):
	tokens = []
	in_string = False
	current_token = ""

	i = 0
	while i < len(code):
		char = code[i]

		# Handle strings
		if char == "\"":
			if in_string:
				# End of string
				current_token += char
				tokens.append(Token(current_token, "STRING"))
				current_token = ""
				in_string = False
			else:
				# Start of string
				if current_token:
					tokens.append(Token(current_token, idf(current_token)))
				current_token = char
				in_string = True
		elif in_string:
			# Collect all characters in the string, including spaces
			current_token += char
		elif char in " \t\n":  # Handle whitespace outside of strings
			if current_token:
				tokens.append(Token(current_token.removeprefix("?"), idf(current_token)))
				current_token = ""
		else:
			current_token += char

		i += 1

	# Append the last token, if any
	if current_token:
		tokens.append(Token(current_token.removeprefix("?"), idf(current_token)))

	return tokens

def execute(tokens):
    variables = {}

    def random(args):
        min,max=int(args[0]),int(args[1])
        return str(b_random.randint(min,max))

    internal_libs = {
        "math": {
            "random": random
        }
    }

    def create_var(name, value, type):
        value = int(value) if type == "NUMBER" else value
        variables[name] = value

    def yap(args): 
        print(" ".join(args).strip("\""))

    def grasp(args):
        return input(args[0].strip("\""))

    def use(macros, library):
        lib = internal_libs[library]

        for name, function in lib.items():
            macros[library+name] = function
        return macros

    macros = {
        "yap": yap,
        "grasp": grasp
    }

    variable_creation = False
    vname = None
    current_macro = None
    import_use=False
    args = []

    for pos, token in enumerate(tokens):
        v = token.value

        # Start variable creation
        if v == 10:  # Corresponds to "lowkey"
            variable_creation = True
        elif v == 18:
            import_use=True
        elif v == "RETURNFUNCTION":
            deep_args = token.name.split(",")

            true_args = token.name.split(",")
            true_args.pop(0)
            if variable_creation:
                returnval = macros[deep_args[0]](true_args)
                create_var(vname, returnval, None)

        elif v == "IDENTIFIER":
            if variable_creation:
                vname = token.name

            if current_macro:
                if token.name.startswith("$"):
                    args.append(variables[token.name[1:]])
            if import_use:
                import_use = False

                if token.name in internal_libs:
                    macros = use(macros, token.name)
                else:
                    raise LibraryNotFound(token.name)
        if v in ["STRING", "NUMBER", 12, 14]: # Handles "cooked" (12), "lit" (14)
            if variable_creation:
                create_var(vname, token.name, v)
                variable_creation = False
            if current_macro:
                args.append(token.name)
        else:
            # If we reach a non-macro token, execute the current macro
            if current_macro:
                current_macro(args)
                current_macro = None  # Reset current macro
                args = []  # Clear args for next macro execution

        if v == "MACRO":
            current_macro = macros[token.name]

    # Handle any remaining macro execution if it was still in progress
    if current_macro:
        current_macro(args)

# Assuming `tokens` are correctly generated from `tokenize(code)`
tokens = tokenize(code)

execute(tokens)

