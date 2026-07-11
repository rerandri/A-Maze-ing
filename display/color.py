import random

class Color():
    @staticmethod
    def rgb(r: int, g: int, b: int) -> str:
        return f"\033[38;2;{r};{g};{b}m"

    @staticmethod
    def end() -> str:
        return "\033[0m"

    @staticmethod
    def random_color() -> str:
        red: int = 0
        green: int = 0
        blue: int = 0

        radiant = random.randint(0, 255)
        if radiant < 85:
            red = random.randint(0, 85)
            green = random.randint(0, 85)
            blue = random.randint(0, 85)
        elif radiant < 170:
            red = random.randint(85, 170)
            green = random.randint(85, 170)
            blue = random.randint(85, 170)
        else:
            red = random.randint(170, 255)
            green = random.randint(170, 255)
            blue = random.randint(170, 255)
        return f"\033[38;2;{red};{green};{blue}m"