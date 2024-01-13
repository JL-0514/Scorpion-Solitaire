"""
A scorpion solitarie game.
"""

__author__ = "Jiameng Li"

import ctypes
from Card import *
from tkinter import *
from PIL import Image, ImageTk
from random import randint


# --------------- Constants ---------------

ROOT = Tk()
""" Game window """

WIN_WIDTH = 940
""" Width of the game window """

WIN_HEIGHT = 900
""" Height of the game window """

BACKSIDE_IMAGE = ImageTk.PhotoImage(Image.open("src/playing_cards/backside.png")
                                    .resize((CARD_WIDTH, CARD_HEIGHT), resample=Image.LANCZOS))
""" Image of the back side of the playing card """

FRAME_RATE = 5
""" Image move every n millionseconds when moving cards to destination position """

ALL_CARDS: dict[str, Card] = {t + str(v): Card(t, v) for t in ["club", "diamond", "heart", "spade"] 
                         for v in reversed(range(1, 14))}
""" All playing cards that will be used in the game """


# --------------- Global variables ---------------

my_canvas = Canvas(ROOT)
my_menu = Menu(ROOT)

my_stacks: list[list[Card]] = []
my_old_stacks: list[list[Card]] = []
my_current_stack = -1
my_current_card = -1
my_started = False


# --------------- Functions for shuffling cards ---------------

def deal_cards() -> None:
    """
    Deal a list of cards and place them on canvas.
    If old stacks in not empty, means it's restarting the game. In this case, use old atacks.
    Else, shuffle cards.
    """   
    # Create cards on canvas
    for card in ALL_CARDS.values():
            my_canvas.create_image(card.x, card.y, image=card.image, tag=card.tag, anchor="nw")
            my_canvas.tag_bind(card.tag, "<Button-1>", click_card)
    
    # Shuffle cards      
    if len(my_old_stacks) > 0: 
        for x in my_old_stacks: my_stacks.append(x.copy())
    else: 
        shuffle_cards()
        for x in my_stacks: my_old_stacks.append(x.copy())
        
    # Hide some cards by displaying the backside of the card
    for i in [0, 1, 2, 3, 7]:
        for card in my_stacks[i][:3]:
            card.hidden = True
            my_canvas.itemconfig(card.tag, image=BACKSIDE_IMAGE)
    
    # Place cards on canvas
    for i in range(7):
        for j in range(len(my_stacks[i])):
            move_card(my_stacks[i][j], True)

def shuffle_cards() -> None:
    """
    Shuffle cards into 7 stacks of cards while make sure there's at least one way to win the game.
    """ 
    # Assign 4 types of cards into 4 stacks order from highest to lowest value
    for i in range(4):
        s = list(ALL_CARDS.values())[i * 13 : (i + 1) * 13]
        my_stacks.append(s)
    my_stacks.extend([[], [], [], []])
    
    # Shuffle cards into 7 stacks by removing some cards from the end of a stack add them to another stack,
    for _ in range(5):
        for i in range(6):
            for j in range(i + 1, 7):
                # Move some cards from first stack to second stack
                f_idx = randint(0, len(my_stacks[i]))
                my_stacks[j].extend(my_stacks[i][f_idx:])
                for _ in range(len(my_stacks[i][f_idx:])):
                    my_stacks[i].pop()
                # Move some cards from second stack to first stack
                s_idx = randint(0, len(my_stacks[j]))
                my_stacks[i].extend(my_stacks[j][s_idx:])
                for _ in range(len(my_stacks[j][s_idx:])):
                    my_stacks[j].pop()
    
    # Deal three cards to the 8th stack
    for i in range(3):
        j = i
        while len(my_stacks[j]) == 0: j += 1
        my_stacks[7].append(my_stacks[j].pop())
    
    # Make sure each stack have 7 cards at the end.
    for i in range(7):
        if len(my_stacks[i]) > 7:
            my_stacks[i + 1].extend(my_stacks[i][7:])
            for _ in range(len(my_stacks[i]) - 7):
                my_stacks[i].pop()
        elif len(my_stacks[i]) < 7:
            j = i + 1
            while len(my_stacks[j]) < 7 - len(my_stacks[i]): j += 1
            temp = my_stacks[j][len(my_stacks[j]) - 7 + len(my_stacks[i]):]
            my_stacks[i].extend(temp)
            for _ in range(len(temp)):
                my_stacks[j].pop()
    
    #Updating stack and card indexes for each card
    for i in range(7):
        for j in range(7):
            c = my_stacks[i][j]
            c.stack_idx = i
            c.card_idx = j
            

# --------------- Functions for moving cards ---------------

def move_card(card: Card, new: bool, current_x: int = 0, current_y: int = 0, 
              dest_x: int = 0, dest_y: int = 0, move_x: int = 0, move_y: int = 0) -> None:
    """
    Place a card to its corresponding position.
    
    Parameters:
    - card: the card to move.
    - new: Whether it's staring to move a new card. If so, arguments after it need to be reassigned in the function.
    - current_x: current x coordinate of the card.
    - current_y: current y coordinate of the card.
    - dest_x: destination x coordinate of the card.
    - dest_y: destination y coordinate of the card.
    - move_x: how much should the card shift from its current position to the right in one move.
    - move_y: how much should the card shift from its current position to the bottom in one move.
    """
    # Starting to move a new card
    if new:
        my_canvas.lift(card.tag)
        current_x = card.x
        current_y = card.y
        card.x = dest_x = CARD_X + card.stack_idx * (CARD_WIDTH + V_GAP)
        card.y = dest_y = CARD_Y + CARD_HEIGHT + (card.card_idx + 1) * H_GAP
        move_x = int((dest_x - current_x) / 20)
        move_y = int((dest_y - current_y) / 20)
    # Adjust the length of move for the last move of a card
    if move_x > dest_x - current_x: move_x = dest_x - current_x
    if move_y > dest_y - current_y: move_y = dest_y - current_y
    # Move the card and update current position
    my_canvas.move(card.tag, move_x, move_y)
    current_x += move_x
    current_y += move_y
    # Continue to move card until the card is placed in its destination position
    if current_x != dest_x or current_y != dest_y:
        my_canvas.after(FRAME_RATE, 
                        lambda: move_card(card, False, current_x, current_y, dest_x, dest_y, move_x, move_y))

def shrink_stack(stack_idx: int, old_len: int) -> None:
    new_len = my_stacks[stack_idx]
    if new_len != 0:
        pass

def stretch_stack(stack_idx: int, old_len: int) -> None:
    new_len = my_stacks[stack_idx]
    if new_len != 0:
        pass

def click_remaining(e) -> None:
    """
    Action when the stack of remaining cards on the topleft corner is clicked.
    """
    if my_started and len(my_canvas.gettags("current")) > 1 and e.y >= CARD_Y and e.y <= CARD_Y + CARD_HEIGHT \
            and e.x >= CARD_X and e.x <= CARD_X + CARD_WIDTH:
        for i in reversed(range(3)):
            c = my_stacks[7].pop()
            c.hidden = False
            c.stack_idx = i
            c.card_idx = len(my_stacks[i])
            my_stacks[i].append(c)
            my_canvas.itemconfig(c.tag, image=c.image)
            move_card(c, True)
            shrink_stack(len(my_stacks[i]) - 1, len(my_stacks[i]))

def click_card(e) -> None:
    """
    Check whether the clicked card is movable. If so, move the clicked card and cards below it
    to the right stack.
    There're two possible valid moves:
    1. The last card in a stack (except for the stack of clicked card) has same type as clicked card
       and has value exactly one greater than the clicked card.
    2. The clicked card has value 13 and there's at least one empty stack. In this case,
       move to the leftmost empty stack.
    """
    if e.y > CARD_Y + CARD_HEIGHT + H_GAP:
        card = ALL_CARDS[my_canvas.gettags("current")[0]]
        for i in range(7):
            last = my_stacks[i][-1] if len(my_stacks[i]) > 0 else None
            # Check for valid move
            if (last != None and i != card.stack_idx and card.type == last.type and card.value == last.value - 1) \
                    or (card.value == 13 and last == None):
                old_stack = card.stack_idx
                new_card_idx = len(my_stacks[i])
                gap = last.y - my_stacks[i][-2].y if last != None and len(my_stacks[i]) > 1 else H_GAP
                temp = my_stacks[card.stack_idx][card.card_idx:]
                # Move cards to the right stack
                for c in temp:
                    my_stacks[old_stack].pop()
                    c.stack_idx = i
                    c.card_idx = new_card_idx
                    my_canvas.lift(c.tag)
                    dest_x = CARD_X + i * (CARD_WIDTH + V_GAP)
                    dest_y = CARD_Y + CARD_HEIGHT + H_GAP + new_card_idx * gap
                    my_canvas.move(c.tag, dest_x - c.x, dest_y - c.y)
                    c.x = dest_x
                    c.y = dest_y
                    my_stacks[i].append(c)
                    new_card_idx += 1
                # Reveal the hidden card after move, if any
                reveal = my_stacks[old_stack][-1] if len(my_stacks[old_stack]) > 0 else None
                if reveal != None and reveal.hidden == True:
                    reveal.hidden = False
                    my_canvas.itemconfig(reveal.tag, image=reveal.image)
                shrink_stack(i, len(my_stacks[i]) - len(temp))
                stretch_stack(old_stack, len(my_stacks[old_stack]) + len(temp))
                break
                    

def drag_card(e, stacks: list[list[Card]], canvas: Canvas):
    global my_current_stack, my_current_card

def confirm_drag(e, stacks: list[list[Card]], canvas: Canvas):
    global my_current_stack, my_current_card


# --------------- Commands for the menu ---------------

def new_or_restart(new: bool) -> None:
    """
    Restart the current game or start a new game.
    
    Parameters:
    - new: whether the user is starting a new game.
    """
    global my_started
    my_canvas.delete("all")
    if new: my_old_stacks.clear()
    my_stacks.clear()
    for c in ALL_CARDS.values():
        c.x = CARD_X
        c.y = CARD_Y
        c.hidden = False
    deal_cards()
    my_started = True
    

def main() -> None:

    # Set up game window
    ROOT.iconphoto(False, BACKSIDE_IMAGE)
    ROOT.title("Scorpion Solitaire")
    ROOT.geometry(F"{WIN_WIDTH}x{WIN_HEIGHT}+{int(ROOT.winfo_screenwidth() / 2)}+40")
    ROOT.resizable(False, False)

    # Set up canvas
    my_canvas.pack(expand=True, fill=BOTH)
    my_canvas.config(background="#3B9212")
    my_canvas.bind("<Button-1>", click_remaining)
    my_canvas.create_image(CARD_X, CARD_Y, image=BACKSIDE_IMAGE, anchor="nw")

    # Set up menu
    my_menu.add_command(label="New Game", command=lambda: new_or_restart(True))
    my_menu.add_command(label="Restart", command=lambda: new_or_restart(False))
    # TODO Implement undo feature
    my_menu.add_command(label="Undo", command=None)
    # TODO Implement hint feature
    my_menu.add_command(label="Hint", command=None)
    ROOT["menu"] = my_menu

    ctypes.windll.shcore.SetProcessDpiAwareness(1)
    ROOT.mainloop()


if __name__ == "__main__":
    main()