"""
A scorpion solitarie game.
"""

__author__ = "Jiameng Li"
__version__= "1.0"
__date__= "19 January 2024"
__name__="__main__"

import ctypes
from Card import *
from CardSet import *
from GameCanvas import *
from tkinter import *
from PIL import Image, ImageTk


# --------------- Constants ---------------

ROOT = Tk()
""" Game window """

CANVAS = GameCanvas(ROOT)
""" Canvas the display cards """

MENU = Menu(ROOT)
""" Menu on the top """

WIN_WIDTH = 940
""" Width of the game window """

WIN_HEIGHT = 900
""" Height of the game window """

BACKSIDE_IMAGE = ImageTk.PhotoImage(Image.open("src/img/backside.png")
                                    .resize((CARD_WIDTH, CARD_HEIGHT), resample=Image.LANCZOS))
""" Image of the back side of the playing card """

ALL_CARDS: dict[str, Card] = {t + str(v): Card(t, v) for t in ["club", "diamond", "heart", "spade"] 
                         for v in range(1, 14)}
""" All playing cards that will be used in the game """

MAX_IN_STACK = 16
""" Maximum number of visible cards in a stack without shrinking the stack """


# --------------- Global variables ---------------

my_cards: CardSet = CardSet(ALL_CARDS)
""" A card set that contains all cards used in the game """

my_closet: str = None
""" The tag of the card closest to the mouse """

my_dragging = False
""" Whether the user is dragging cards """

my_drag_cards: list[Card] = None
""" The list of cards being dragging """

my_started = False
""" Whether the game has started """

my_no_move = False
""" Whether there's no more moves """


# --------------- Functions for operating the game ---------------

def deal_cards() -> None:
    """
    Deal a list of cards and place them on canvas.
    If old stacks in not empty, means it's restarting the game. In this case, use old atacks.
    Else, shuffle cards.
    """   
    # Create cards on canvas
    CANVAS.create_cards(ALL_CARDS.values(), drag_card, release_card)
    
    # Shuffle cards      
    if len(my_cards.old_stacks) > 0: 
        for x in my_cards.old_stacks: my_cards.stacks.append(x.copy())
    else: 
        my_cards.shuffle_cards()
        #my_cards.test_shuffle()
        for x in my_cards.stacks: my_cards.old_stacks.append(x.copy())
        
    # Hide some cards by displaying the backside of the card
    for i in [0, 1, 2, 3, 7]:
        for card in my_cards.stacks[i][:3]:
            card.hidden = True
            CANVAS.itemconfig(card.tag, image=BACKSIDE_IMAGE)
    
    # Place cards on canvas
    for i in range(7):
        for j in range(len(my_cards.stacks[i])):
            CANVAS.start_move_card(my_cards.stacks[i][j])

def hover_card(e) -> None:
    """
    Make the card shift up after hovering the card for 1/5 second.
    """
    x = e.x
    y = e.y
    CANVAS.after(200, lambda: shift_card(e, x, y))

def shift_card(e, x=None, y=None, clicked=False) -> None:
    """
    Shift the card up when the mouse hovering the card, and down when leave.
    
    Parameters:
    - x: x coordinate of the mouse 1/5 second ago.
    - y: y coordinate of the mouse 1/5 second ago.
    - clicked: whether the card is clicked and is moving to another stack. In this case, always shift down.
    """
    global my_closet
    if clicked or e == None or (e.x == x and e.y == y):
        tags = CANVAS.gettags("current")
        if "NoMove" not in tags:
            different_card = len(tags) > 1 and tags[0] != my_closet
            # Shift previous card down
            if my_closet != None and (clicked or different_card or len(tags) < 2) and not my_dragging:
                ALL_CARDS[my_closet].move_id = CANVAS.move(my_closet, 0, H_GAP - 5)
                my_closet = None
            # shift next card up
            if len(tags) > 1 and different_card and not ALL_CARDS[tags[0]].hidden and not clicked and not my_dragging:
                my_closet = tags[0]
                ALL_CARDS[my_closet].move_id = CANVAS.move(my_closet, 0, -(H_GAP - 5))

def shrink_stack(stack_idx: int, old_len: int) -> None:
    """
    Shrink the stack when some cards are moved to the stack and the number of cards is greater than
    maximum visible number.
    
    Parameters:
    - stack_idx: the index of the stack to shrink
    - old_len: the length of the stack cards are moved
    """
    new_len = len(my_cards.stacks[stack_idx])
    if new_len > MAX_IN_STACK and new_len > old_len:
        gap = (H_GAP * MAX_IN_STACK) // new_len
        for c in my_cards.stacks[stack_idx]: CANVAS.start_move_card(c, gap)

def stretch_stack(stack_idx: int, old_len: int) -> None:
    """
    Stretch the stack when some cards are moved to another stack, if the stack is shrinked.
    
    Parameters:
    - stack_idx: the index of the stack to stretch
    - old_len: the length of the stack cards are moved
    """
    new_len = len(my_cards.stacks[stack_idx])
    if new_len > 1 and new_len < old_len and old_len > MAX_IN_STACK:
        gap = (H_GAP * MAX_IN_STACK) // new_len if new_len > MAX_IN_STACK else H_GAP
        for c in my_cards.stacks[stack_idx]: CANVAS.start_move_card(c, gap)

def check_win(stack_idx: int) -> None:
    """
    If there's a completed set of cards in a stack, collect them and move them to top-right area.
    If win the game, notify the users.
    
    Parameters:
    - stack_idx: the index of stack to be checked
    """
    global my_started
    while my_cards.check_stack(stack_idx): 
        CANVAS.collect_finished(my_cards.stacks[7 + my_cards.win_num], my_cards.win_num)
        stretch_stack(stack_idx, len(my_cards.stacks[stack_idx]) - 13)
    if my_cards.win_num == 4:
        my_started = False
        CANVAS.create_text(10, 10, text="YOU WIN!", fill="white", font=("Helvetica 20 bold"), anchor="nw")


# --------------- Actions that response to mouse events ---------------

def click_remaining() -> None:
    """
    Action when the stack of remaining cards on the topleft corner is clicked.
    """
    if my_started and len(my_cards.stacks[7]) == 3:
        for i in reversed(range(3)):
            c = my_cards.stacks[7][i]
            c.hidden = False
            CANVAS.itemconfig(c.tag, image=c.image)
            my_cards.switch_stack(7, i, 1)
            gap = (H_GAP * MAX_IN_STACK) // len(my_cards.stacks[i]) \
                if len(my_cards.stacks[i]) > MAX_IN_STACK else H_GAP
            CANVAS.start_move_card(c, gap)
            shrink_stack(i, len(my_cards.stacks[i]) - 1)

def click_card(checked=False, card=None, target=None, first_empty=0) -> None:
    """
    Check whether the clicked card is movable. If so, move the clicked card and cards below it
    to the right stack.
    There're two possible valid moves:
    1. The last card in a stack (except for the stack of clicked card) has same type as clicked card
       and has value exactly one greater than the clicked card.
    2. The clicked card has value 13 and there's at least one empty stack. In this case,
       move to the leftmost empty stack.
       
    Parameters:
    - checked: whether the move has been checked to be valid. If true, it must specify the parameter card and
               either target or first empty
    - card: the card clicked (or dragged)
    - target: the target card that the clicked card will be moving toward to
    - first_empty: the index of first empty stack from left to right
    """
    if not checked:
        card = ALL_CARDS[CANVAS.gettags("current")[0]]
        target = ALL_CARDS[card.type + str(card.value + 1)] if card.value != 13 else None
        first_empty = 0
        while len(my_cards.stacks[first_empty]) != 0 and first_empty < 7: first_empty += 1
    if checked or ((target != None and not target.hidden and target.stack_idx != card.stack_idx \
            and target.card_idx == len(my_cards.stacks[target.stack_idx]) - 1) \
            or (card.value == 13 and first_empty < 7)):
        old_s = card.stack_idx
        new_s = target.stack_idx if target != None else first_empty
        length = len(my_cards.stacks[new_s])
        gap = (H_GAP * MAX_IN_STACK) // len(my_cards.stacks[new_s]) \
            if len(my_cards.stacks[new_s]) > MAX_IN_STACK else H_GAP
        temp = my_cards.stacks[old_s][card.card_idx:]
        # Move cards to the right stack
        my_cards.switch_stack(old_s, new_s, len(temp))
        shift_card(None, True)
        for c in temp: 
            CANVAS.start_move_card(c, gap)
        # Reveal the hidden card after move, if any
        reveal = my_cards.stacks[old_s][-1] if len(my_cards.stacks[old_s]) > 0 else None
        if reveal != None and reveal.hidden:
            reveal.hidden = False
            CANVAS.itemconfig(reveal.tag, image=reveal.image)
        # Stretch or shrink stacks to fit window
        shrink_stack(new_s, length)
        stretch_stack(old_s, len(my_cards.stacks[old_s]) + len(temp))
        check_win(new_s)
                    
def drag_card(e) -> None:
    """
    Move cards when the mouse is dragging. If a card moves, other cards below it in the same
    stack move along with it. Hidden cards are not movable.
    """
    global my_dragging, my_drag_cards, my_closet
    if not my_dragging:
        my_dragging = True
        my_closet = None
        card = ALL_CARDS[CANVAS.gettags("current")[0]]
        my_drag_cards = my_cards.stacks[card.stack_idx][card.card_idx:] if not card.hidden else None
    if my_drag_cards != None:
        for i in range(len(my_drag_cards)):
            c = my_drag_cards[i]
            c.x = e.x - CARD_WIDTH // 2
            c.y = e.y + i * H_GAP
            CANVAS.lift(c.tag)
            c.move_id = CANVAS.moveto(c.tag, c.x, c.y)

def release_card(e) -> None:
    """
    After release the cards from drag or click evetn, move cards to either their destination
    stack or original stack.
    """
    global my_dragging, my_drag_cards
    # Release from drag
    if my_dragging and my_drag_cards != None:
        # Determine whether the move is valid and, if so, witch stack
        old_stack = my_drag_cards[0].stack_idx
        dest_stack: int = (e.x - CARD_X) // (CARD_WIDTH + V_GAP)
        if (len(my_cards.stacks[dest_stack]) == 0):
            if my_drag_cards[0].value == 13: 
                click_card(True, my_drag_cards[0], None, dest_stack)
        else:
            target = my_cards.stacks[dest_stack][-1]
            if my_drag_cards[0].type == target.type and my_drag_cards[0].value == target.value - 1:
                click_card(True, my_drag_cards[0], target)
        # If the move is invalid, move cards back to teir original stack
        if old_stack == my_drag_cards[0].stack_idx:
            gap = (H_GAP * MAX_IN_STACK) // len(my_cards.stacks[my_drag_cards[0].stack_idx]) \
                  if len(my_cards.stacks[my_drag_cards[0].stack_idx]) > MAX_IN_STACK else H_GAP
            for c in my_drag_cards: CANVAS.start_move_card(c, gap)
        my_drag_cards = None
        my_dragging = False
    # Release from clicking the remaining cards
    elif e.y >= CARD_Y and e.y <= CARD_Y + CARD_HEIGHT and e.x >= CARD_X and e.x <= CARD_X + CARD_WIDTH:
        click_remaining()
    # Release from clicking a card in visible stack
    elif e.y > CARD_Y + CARD_HEIGHT:
        click_card()


# --------------- Commands for the menu ---------------

def new_or_restart(new: bool) -> None:
    """
    Restart the current game or start a new game.
    
    Parameters:
    - new: whether the user is starting a new game.
    """
    global my_started, my_no_move, my_closet, my_drag_cards, my_dragging
    my_cards.reset(new)
    deal_cards()
    my_started = True
    my_no_move = False
    my_closet = None
    my_drag_cards = None
    my_dragging = False

def undo() -> None:
    """
    Undo previous step
    """
    global my_no_move
    if my_started and len(my_cards.steps) > 0:
        if my_no_move:     # Delete text for no more moves
            my_no_move = False
            CANVAS.delete("NoMove")
        step = my_cards.steps.pop()
        if step[0] == 7:    # Undo click on the remaining cards
            three = [step, my_cards.steps.pop(), my_cards.steps.pop()]
            for i in range(3):
                step = three[i]
                card = my_cards.stacks[step[1]][-1]
                card.hidden = True
                CANVAS.itemconfig(card.tag, image=BACKSIDE_IMAGE)
                my_cards.switch_stack(step[1], 7, 1, False)
                move_x = (CARD_X - card.x) // FRAME_RATE
                move_y = (CARD_Y - card.y) // FRAME_RATE
                CANVAS.move_card(card, CARD_X, CARD_Y, move_x, move_y)
                stretch_stack(step[1], len(my_cards.stacks[step[1]]) + 1)
        else:   # Undo regular steps
            if step[3]:  # Hide the card if it's hidden in previous step
                    hide = my_cards.stacks[step[0]][-1]
                    hide.hidden = True
                    CANVAS.itemconfig(hide.tag, image=BACKSIDE_IMAGE)
            temp = my_cards.stacks[step[1]][len(my_cards.stacks[step[1]]) - step[2]:]
            if step[1] > 7:     # If cards is moved a completed set
                my_cards.win_num -= 1
                my_cards.stacks[step[1]]
                for c in temp: c.hidden = False
            temp = my_cards.stacks[step[1]][len(my_cards.stacks[step[1]]) - step[2]:]
            my_cards.switch_stack(step[1], step[0], step[2], False)
            gap = (H_GAP * MAX_IN_STACK) // (len(my_cards.stacks[step[0]]) - step[2]) \
                if len(my_cards.stacks[step[0]]) - step[2] > MAX_IN_STACK else H_GAP
            for c in temp:
                CANVAS.start_move_card(c, gap)
            stretch_stack(step[1], len(my_cards.stacks[step[1]]) + step[2])
            shrink_stack(step[0], len(my_cards.stacks[step[0]]) - step[2])
            if step[1] > 7: undo()

def hint() -> None:
    """
    Find an available move and trigger the click event to make the move.
    If there's no move, notify the user.
    """
    global my_no_move
    if my_started and not my_no_move:
        found = False
        # Look for an empty spot for a 'King'(value 13)
        for t in ["club", "diamond", "heart", "spade"]:
            tag = t + "13"
            if not ALL_CARDS[tag].hidden and ALL_CARDS[tag].card_idx != 0:
                dest = 0
                while len(my_cards.stacks[dest]) != 0 and dest < 7: dest += 1
                if dest < 7:
                    card = ALL_CARDS[tag]
                    click_card(True, card, None, dest)
                    found = True
                    break
        # Look for move in stacks from left to right
        if not found:
            for i in range(7):
                if len(my_cards.stacks[i]) > 0:
                    target = my_cards.stacks[i][-1]
                    if target.value != 1:
                        card = ALL_CARDS[target.type + str(target.value - 1)]
                        if not card.hidden and card.stack_idx != target.stack_idx:
                            click_card(True, card, target)
                            found = True
                            break
        # Look for remaining cards
        if not found and len(my_cards.stacks[7]) > 0:
            click_remaining()
            found = True
        # Notify the user there's no more moves
        if not found:
            my_no_move = True
            CANVAS.create_text(10, 10, tag="NoMove", text="No more moves.\nTry to undo or restart.", 
                               fill="white", font=("Helvetica 20 bold"), anchor="nw")
    

def main() -> None:
    """
    Set up the game window and its components and start the game.
    """

    # Set up game window
    ROOT.iconphoto(False, BACKSIDE_IMAGE)
    ROOT.title("Scorpion Solitaire")
    ROOT.geometry(F"{WIN_WIDTH}x{WIN_HEIGHT}+{int(ROOT.winfo_screenwidth() / 2)}+40")
    ROOT.resizable(False, False)

    # Set up canvas
    CANVAS.pack(expand=True, fill=BOTH)
    CANVAS.config(background="#3B9212")
    CANVAS.bind("<Motion>", hover_card)
    CANVAS.create_image(CARD_X, CARD_Y, image=BACKSIDE_IMAGE, anchor="nw")

    # Set up menu
    MENU.add_command(label="New Game", command=lambda: new_or_restart(True))
    MENU.add_command(label="Restart", command=lambda: new_or_restart(False))
    MENU.add_command(label="Undo", command=undo)
    MENU.add_command(label="Hint", command=hint)
    ROOT["menu"] = MENU

    ctypes.windll.shcore.SetProcessDpiAwareness(1)
    ROOT.mainloop()


if __name__ == "__main__":
    main()