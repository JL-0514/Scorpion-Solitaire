from PIL import Image, ImageTk

CARD_WIDTH = 110
""" Width of playing cards """

CARD_HEIGHT = 160
""" Height of playing cards """

CARD_X = 20
""" The leftmost position a card can be placed """

CARD_Y = 20
""" The topmost position a card can be placed """

V_GAP = 20
""" Vertical gap between different stacks of cards """

H_GAP = 30
""" Initial horizontal gap between the top of each cards """

class Card:
    """
    Represent a playing card
    """
    
    def __init__(self, type: str, value: int) -> None:
        """
        Create a playing card based in the given type and value.
        
        Parameters:
        - type: type of the card (club, diamong, heart, or spade)
        - value: value of the card (1 to 13)
        """
        self.type = type
        self.value = value
        self.tag = type + str(value)
        self.image = ImageTk.PhotoImage(Image.open(f"src/playing_cards/{type}{str(value)}.png")
                                        .resize((CARD_WIDTH, CARD_HEIGHT), resample=Image.LANCZOS))
        self.hidden = False
        self.x = CARD_X
        self.y = CARD_Y
        self.stack_idx = -1
        self.card_idx = 13 - value