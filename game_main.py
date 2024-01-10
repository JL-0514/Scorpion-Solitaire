"""
A scorpion solitarie game.
"""

from tkinter import *
from PIL import Image, ImageTk


ROOT = Tk()
""" Game window """

WIN_WIDTH = 710
""" Width of the game window """

WIN_HEIGHT = 600
""" Height of the game window """

SCREEN_X = int(ROOT.winfo_screenwidth() / 2 - WIN_WIDTH / 2)
""" X-coordinate of the top-left corner of the game window """

SCREEN_Y = int(ROOT.winfo_screenheight() / 2 - WIN_HEIGHT / 2 - 40)
""" Y-coordinate of the top-left corner of the game window """

CARD_WIDTH = 80
""" Width of playing cards """

CARD_HEIGHT = 116
""" Height of playing cards """

CARD_X = 55
""" The leftmost position a card can be placed """

CARD_Y = 75
""" The topmost position a card can be placed """

BACKSIDE_IMAGE = ImageTk.PhotoImage(Image.open("playing_cards/backside.png")
                                    .resize((CARD_WIDTH, CARD_HEIGHT), resample=Image.LANCZOS))
""" Image of the back side of the playing card """

ALL_TYPES = ["club", "diamond", "heart", "spade"]
""" All four types of card """

ALL_VALUES = list(range(1, 14))
""" All possible value of all types of card """


class Card:
    """
    Represent a playing card
    """
    def __init__(self, type: str, value: int) -> None:
        self.type = type
        self.value = value
        self.image = ImageTk.PhotoImage(Image.open(f"playing_cards/{type}{str(value)}.png")
                                        .resize((CARD_WIDTH, CARD_HEIGHT), resample=Image.LANCZOS))
        self.hidden = False
        self.x = CARD_X
        self.y = CARD_Y


def deal_cards(cards: list[Card], stacks: list[list[Card]]) -> None:
    """
    Deal a list of cards. Shuffle cards into 7 stacks of cards while make sure 
    there's at least one way to win the game.
    
    Parameters:
    - cards: a list of cards to deal
    - stacks: stacks of shuffled cards
    """
    for i in range(7):
        s = cards[i * 7 : (i + 1) * 7]
        stacks.append(s)
    for i in range(7):
        c: list[Card] = stacks[i]
        for j in range(7):
            c[j].x = CARD_X + i * (CARD_WIDTH + 20)
            c[j].y = CARD_Y + CARD_HEIGHT + (j + 1) * 20
        

def display_cards(cards: list[Card], canvas: Canvas) -> None:
    """
    Put all cards on the canvas.
    
    Parameter:
    - cards: a list of cards to diaplay
    - canvas: the canvas used to display cards
    """
    for c in cards:
        if (c.hidden): canvas.create_image(c.x, c.y, image=BACKSIDE_IMAGE)
        else: canvas.create_image(c.x, c.y, image=c.image)


# --------------- Initialize playing cards ---------------

# Create a list of required cards
all_cards: list[Card] = []
for t in ALL_TYPES:
    for v in ALL_VALUES:
        all_cards.append(Card(t, v))

card_stacks: list[list[Card]] = []
deal_cards(all_cards, card_stacks)


# --------------- Diplay game window ---------------

# Set up game window
ROOT.iconphoto(False, BACKSIDE_IMAGE)
ROOT.title("Scorpion Solitaire")
ROOT.geometry(F"{WIN_WIDTH}x{WIN_HEIGHT}+{SCREEN_X}+{SCREEN_Y}")
ROOT.resizable(False, False)

# Set up canvas
canvas_frame = Frame(ROOT)
canvas_frame.pack(expand=True, fill=BOTH)
canvas = Canvas(canvas_frame)
canvas.pack(expand=True, fill=BOTH)
canvas.config(background="#3B9212")

display_cards(all_cards, canvas)

ROOT.mainloop()