class OptionalToken:
    def __init__(self, optional_token_type):
        self.optional_token_type = optional_token_type

    def eat(self, str_data):
        try:
            return self.optional_token_type.eat(str_data)
        except ValueError:
            return [], str_data