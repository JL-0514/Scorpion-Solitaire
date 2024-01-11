from PIL import Image, ImageTk

CARD_WIDTH = 110
""" Width of playing cards """

CARD_HEIGHT = 160
""" Height of playing cards """

CARD_X = 75
""" The leftmost position a card can be placed """

CARD_Y = 105
""" The topmost position a card can be placed """

class Card:
    """
    Represent a playing card
    """
    def __init__(self, type: str, value: int) -> None:
        self.type = type
        self.value = value
        self.image = ImageTk.PhotoImage(Image.open(f"src/playing_cards/{type}{str(value)}.png")
                                        .resize((CARD_WIDTH, CARD_HEIGHT), resample=Image.LANCZOS))
        self.hidden = False
        self.x = CARD_X
        self.y = CARD_Y