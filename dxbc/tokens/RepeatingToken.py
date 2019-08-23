class RepeatingToken:
    def __init__(self, token_type, min_repeats = 0, max_repeats = -1):
        self.token_type = token_type
        self.min_repeats = min_repeats
        self.max_repeats = max_repeats

    def eat(self, str_data):
        tokens = []
        remaining_data = str_data
        reps = 0
        while True:
            try:
                new_token_list, remaining_data = self.token_type.eat(remaining_data)
            except ValueError:
                break
            tokens += new_token_list
            reps += 1
        if reps < self.min_repeats or (reps > self.max_repeats and self.max_repeats > 0):
            raise ValueError("Token {} should have repeated between {} and {} times, actually repeated {}".format(self.token_type, self.min_repeats, self.max_repeats, reps))

        return tokens, remaining_data