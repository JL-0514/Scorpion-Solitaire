"""
A scorpion solitarie game.
"""

import ctypes
from Card import *
from tkinter import *
from PIL import Image, ImageTk
from random import randint


ROOT = Tk()
""" Game window """

WIN_WIDTH = 940
""" Width of the game window """

WIN_HEIGHT = 900
""" Height of the game window """

BACKSIDE_IMAGE = ImageTk.PhotoImage(Image.open("src/playing_cards/backside.png")
                                    .resize((CARD_WIDTH, CARD_HEIGHT), resample=Image.LANCZOS))
""" Image of the back side of the playing card """


def deal_cards(cards: list[Card], old_stacks: list[list[Card]], stacks: list[list[Card]], canvas: Canvas) -> None:
    """
    Deal a list of cards and place them on canvas.
    If old stacks in not empty, means it's restarting the game. In this case, use old atacks.
    Else, shuffle cards.
    
    Parameters:
    - cards: a list of cards to deal
    - old_stacks: a copy of card stacks at the beginning of the game
    - stacks: stacks of shuffled cards
    - canvas: canvas that display cards
    """
    # Create cards on canvas
    for card in cards:
            canvas.create_image(card.x, card.y, image=card.image, tag=card.tag)
            
    if len(old_stacks) > 0: 
        for x in old_stacks: stacks.append(x.copy())
    else: 
        shuffle_cards(cards, stacks)
        for x in stacks: old_stacks.append(x.copy())
    
    # Place each card on its corresponding position.
    # Horizontal gap between cards in a stack should shrink to fit the canvas when there's too many cards
    for i in range(7):
        cstack: list[Card] = stacks[i]
        h_gap = 30 if len(cstack) < 15 else int(30 - CARD_WIDTH / len(cstack))
        j = 0
        prev = None
        for card in cstack:
            # Move card
            old_x = card.x
            old_y = card.y
            card.x = CARD_X + i * (CARD_WIDTH + 20)
            card.y = CARD_Y + CARD_HEIGHT + 30 + j * h_gap
            # Make sure cards overlay each other correctly
            canvas.move(card.tag, card.x - old_x, card.y - old_y)
            canvas.tag_raise(card.tag, prev)
            prev = card.tag
            j += 1
    
    # Hide some cards by displaying the backside of the card
    for i in [0, 1, 2, 3, 7]:
        for card in stacks[i][:3]:
            card.hidden = True
            canvas.itemconfig(card.tag, image=BACKSIDE_IMAGE)


def shuffle_cards(cards: list[Card], stacks: list[list[Card]]) -> None:
    """
    Shuffle cards into 7 stacks of cards while make sure there's at least one way to win the game.
    
    Parameters:
    - cards: a list of cards to deal
    - stacks: stacks of shuffled cards
    """
    # Assign 4 types of cards into 4 stacks order from highest to lowest value
    for i in range(4):
        s = cards[i * 13 : (i + 1) * 13]
        stacks.append(s)
    stacks.extend([[], [], [], []])
    
    # Shuffle cards into 7 stacks by removing some cards from the end of a stack add them to another stack,
    for _ in range(5):
        for i in range(6):
            for j in range(i + 1, 7):
                # Move some cards from first stack to second stack
                f_idx = randint(0, len(stacks[i]))
                stacks[j].extend(stacks[i][f_idx:])
                for _ in range(len(stacks[i][f_idx:])):
                    stacks[i].pop()
                # Move some cards from second stack to first stack
                s_idx = randint(0, len(stacks[j]))
                stacks[i].extend(stacks[j][s_idx:])
                for _ in range(len(stacks[j][s_idx:])):
                    stacks[j].pop()
    
    # Make sure each stack have 7 cards at the end. Move extras to 8th stack
    for i in range(7):
        if len(stacks[i]) > 7:
            stacks[7].extend(stacks[i][7:])
            for _ in range(len(stacks[i]) - 7):
                stacks[i].pop()
        elif len(stacks[i]) < 7:
            j = i + 1
            while len(stacks[j]) < 7 - len(stacks[i]): j += 1
            temp = stacks[j][len(stacks[j]) - 7 + len(stacks[i]):]
            stacks[i].extend(temp)
            for _ in range(len(temp)):
                stacks[j].pop()


def new_or_restart(cards: list[Card], old_stacks: list, stacks: list, canvas: Canvas, new: bool) -> None:
    """
    Restart the current game or start a new game.
    
    Parameters:
    - cards: a list of cards to deal
    - old_stacks: a copy of card stacks at the beginning of the game
    - stacks: stacks of shuffled cards
    - canvas: canvas that display cards
    """
    canvas.delete("all")
    if new: old_stacks.clear()
    stacks.clear()
    for c in cards:
        c.x = CARD_X
        c.y = CARD_Y
        c.hidden = False
    deal_cards(cards, old_stacks, stacks, canvas)
    


# --------------- Initialize playing cards ---------------

all_cards: list[Card] = []
for t in ["club", "diamond", "heart", "spade"]:
    for v in range(1, 14):
        all_cards.append(Card(t, v))
card_stacks = []
init_stacks = []


# --------------- Initialize game ---------------

# Set up game window
ROOT.iconphoto(False, BACKSIDE_IMAGE)
ROOT.title("Scorpion Solitaire")
ROOT.geometry(F"{WIN_WIDTH}x{WIN_HEIGHT}+{int(ROOT.winfo_screenwidth() / 2)}+40")
ROOT.resizable(False, False)

# Set up canvas
canvas = Canvas(ROOT)
canvas.pack(expand=True, fill=BOTH)
canvas.config(background="#3B9212")
canvas.create_image(CARD_X, CARD_Y, image=BACKSIDE_IMAGE)

# Set up menu
menu = Menu(ROOT)
menu.add_command(label="New Game", command=lambda: new_or_restart(all_cards, init_stacks, card_stacks, canvas, True))
menu.add_command(label="Restart", command=lambda: new_or_restart(all_cards, init_stacks, card_stacks, canvas, False))
# TODO Implement undo feature
menu.add_command(label="Undo", command=None)
# TODO Implement hint feature
menu.add_command(label="Hint", command=None)
ROOT["menu"] = menu


ctypes.windll.shcore.SetProcessDpiAwareness(1)
ROOT.mainloop()