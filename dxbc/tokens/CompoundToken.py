class CompoundToken:
    def __init__(self, *token_types):
        self.token_types = token_types

    def eat(self, str_data):
        tokens = []
        remaining_data = str_data
        for token_type in self.token_types:
            new_token_list, remaining_data = token_type.eat(remaining_data)
            tokens += new_token_list
        return tokens, remaining_data