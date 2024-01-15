"""
A scorpion solitarie game.
"""

__author__ = "Jiameng Li"

import ctypes
from Card import *
from CardSet import *
from GameCanvas import *
from tkinter import *
from PIL import Image, ImageTk


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

ALL_CARDS: dict[str, Card] = {t + str(v): Card(t, v) for t in ["club", "diamond", "heart", "spade"] 
                         for v in range(1, 14)}
""" All playing cards that will be used in the game """


# --------------- Global variables ---------------

my_canvas = GameCanvas(ROOT)
""" Canvas the display cards """
my_menu = Menu(ROOT)
""" Menu on the top """
my_cards: CardSet = CardSet(ALL_CARDS)
""" A card set that contains all cards used in the game """
my_closet: str = None
""" The tag of the card closest to the mouse """
my_dragging = False
""" Whether the user is dragging cards """
my_started = False
""" Whether the game has started """


# --------------- Functions ---------------

def deal_cards() -> None:
    """
    Deal a list of cards and place them on canvas.
    If old stacks in not empty, means it's restarting the game. In this case, use old atacks.
    Else, shuffle cards.
    """   
    # Create cards on canvas
    my_canvas.create_cards(ALL_CARDS.values(), click_card, drag_card, confirm_drag)
    
    # Shuffle cards      
    if len(my_cards.old_stacks) > 0: 
        for x in my_cards.old_stacks: my_cards.stacks.append(x.copy())
    else: 
        #my_cards.shuffle_cards()
        my_cards.test_shuffle()
        for x in my_cards.stacks: my_cards.old_stacks.append(x.copy())
        
    # Hide some cards by displaying the backside of the card
    for i in [0, 1, 2, 3, 7]:
        for card in my_cards.stacks[i][:3]:
            card.hidden = True
            my_canvas.itemconfig(card.tag, image=BACKSIDE_IMAGE)
    
    # Place cards on canvas
    for i in range(7):
        for j in range(len(my_cards.stacks[i])):
            my_canvas.start_move_card(my_cards.stacks[i][j])

def shift_card(e, clicked=False) -> None:
    """
    Shift the card up when the mouse hovering the card, and down when leave.
    
    Parameters:
    - clicked: whether the card is clicked and is moving to another stack. In this case, always shift down.
    """
    global my_closet
    tags = my_canvas.gettags("current")
    different_card = len(tags) > 1 and tags[0] != my_closet
    # Shift previous card down
    if clicked or (my_closet != None and (different_card or len(tags) < 2)):
        ALL_CARDS[my_closet].move_id = my_canvas.move(my_closet, 0, H_GAP - 5)
        my_closet = None
    # shift next card up
    if len(tags) > 1 and different_card and not ALL_CARDS[tags[0]].hidden:
        my_closet = tags[0]
        ALL_CARDS[my_closet].move_id = my_canvas.move(my_closet, 0, -(H_GAP - 5))

def shrink_stack(stack_idx: int, old_len: int) -> None:
    new_len = len(my_cards.stacks[stack_idx])
    if new_len > 1:
        pass

def stretch_stack(stack_idx: int, old_len: int) -> None:
    new_len = len(my_cards.stacks[stack_idx])
    if new_len > 1:
        pass

def click_remaining(e) -> None:
    """
    Action when the stack of remaining cards on the topleft corner is clicked.
    """
    if my_started and len(my_cards.stacks[7]) == 3 and  len(my_canvas.gettags("current")) > 1 \
            and e.y >= CARD_Y and e.y <= CARD_Y + CARD_HEIGHT and e.x >= CARD_X and e.x <= CARD_X + CARD_WIDTH:
        for i in reversed(range(3)):
            c = my_cards.stacks[7][i]
            c.hidden = False
            my_canvas.itemconfig(c.tag, image=c.image)
            my_cards.switch_stack(7, i, 1)
            my_canvas.start_move_card(c)
            stretch_stack(i, len(my_cards.stacks[i]) - 1)

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
            last = my_cards.stacks[i][-1] if len(my_cards.stacks[i]) > 0 else None
            # Check for valid move
            if (last != None and i != card.stack_idx and card.type == last.type and card.value == last.value - 1) \
                    or (card.value == 13 and last == None):
                old_stack = card.stack_idx
                old_length = len(my_cards.stacks[i])
                gap = last.y - my_cards.stacks[i][-2].y if last != None and len(my_cards.stacks[i]) > 1 else H_GAP
                temp = my_cards.stacks[old_stack][card.card_idx:]
                # Move cards to the right stack
                my_cards.switch_stack(old_stack, i, len(temp))
                shift_card(None, True)
                for c in temp: 
                    my_canvas.start_move_card(c, gap)
                # Reveal the hidden card after move, if any
                reveal = my_cards.stacks[old_stack][-1] if len(my_cards.stacks[old_stack]) > 0 else None
                if reveal != None and reveal.hidden:
                    reveal.hidden = False
                    my_canvas.itemconfig(reveal.tag, image=reveal.image)
                # Stretch or shrink stacks to fit window
                shrink_stack(i, old_length)
                stretch_stack(old_stack, len(my_cards.stacks[old_stack]) + len(temp))
                check_win(i)
                break
                    
def drag_card(e) -> None:
    global my_dragging
    my_dragging = True

def confirm_drag(e) -> None:
    global my_dragging
    if my_dragging:
        my_dragging = False

def check_win(stack_idx: int) -> None:
    """
    If there's a completed set of cards in a stack, collect them and move them to top-right area.
    If win the game, notify the users.
    
    Parameters:
    - stack_idx: the index of stack to be checked
    """
    global my_started
    if my_cards.check_stack(stack_idx): 
        my_canvas.collect_finished(my_cards.stacks[7 + my_cards.win_num], my_cards.win_num)
        stretch_stack(stack_idx, len(my_cards.stacks[stack_idx]) - 13)
    if my_cards.win_num == 4:
        my_started = False
        my_canvas.create_text(10, 10, text="YOU WIN!", fill="white", font=("Helvetica 20 bold"), 
                              anchor="nw", justify="center")


# --------------- Commands for the menu ---------------

def new_or_restart(new: bool) -> None:
    """
    Restart the current game or start a new game.
    
    Parameters:
    - new: whether the user is starting a new game.
    """
    global my_started
    my_cards.reset(new)
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
    my_canvas.bind("<Motion>", shift_card)
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