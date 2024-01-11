"""
A scorpion solitarie game.
"""

import ctypes
from Card import *
from tkinter import *
from PIL import Image, ImageTk


ROOT = Tk()
""" Game window """

WIN_WIDTH = 940
""" Width of the game window """

WIN_HEIGHT = 900
""" Height of the game window """

BACKSIDE_IMAGE = ImageTk.PhotoImage(Image.open("src/playing_cards/backside.png")
                                    .resize((CARD_WIDTH, CARD_HEIGHT), resample=Image.LANCZOS))
""" Image of the back side of the playing card """

ALL_TYPES = ["club", "diamond", "heart", "spade"]
""" All four types of card """

ALL_VALUES = list(range(1, 14))
""" All possible value of all types of card """


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
            c[j].y = CARD_Y + CARD_HEIGHT + (j + 1) * 30
        

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
ROOT.geometry(F"{WIN_WIDTH}x{WIN_HEIGHT}+40+40")
ROOT.resizable(False, False)

# Set up menu
menu = Menu(ROOT)
for x in ["New Game", "Restart", "Hint"]:
    # TODO Add correct command
    menu.add_command(label=x, command=None)
ROOT["menu"] = menu

# Set up canvas
canvas = Canvas(ROOT)
canvas.pack(expand=True, fill=BOTH)
canvas.config(background="#3B9212")

display_cards(all_cards, canvas)

ctypes.windll.shcore.SetProcessDpiAwareness(True)
ROOT.mainloop()