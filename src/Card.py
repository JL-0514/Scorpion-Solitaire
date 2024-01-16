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
        """ Type of the card """
        self.value = value
        """ Value of the card """
        self.tag = type + str(value)
        """ Tag of the card used to get the card from the canvas """
        self.image = ImageTk.PhotoImage(Image.open(f"src/playing_cards/{type}{str(value)}.png")
                                        .resize((CARD_WIDTH, CARD_HEIGHT), resample=Image.LANCZOS))
        """ Image of the card """
        self.hidden = False
        """ Whether the card is hidden (including the completed set of cards) """
        self.x = CARD_X
        """ X-coordinate of the card """
        self.y = CARD_Y
        """ Y-coordinate of the card """
        self.stack_idx = -1
        """ Number of stack the card belongs to """
        self.card_idx = value - 1
        """ Number of card in a stack (from top to bottom) """
        self.move_id = None
        """ Id return by canvas.move() if the card is moving """