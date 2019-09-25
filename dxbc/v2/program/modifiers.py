class Modifier:
    def surround(self, normal_function: str):
        raise NotImplementedError()


class SaturateModifier(Modifier):
    def surround(self, normal_function: str):
        return f"saturate({normal_function})"


modifier_map = {
    "sat": SaturateModifier
}