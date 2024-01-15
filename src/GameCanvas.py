from Card import *
from tkinter import Canvas, Tk

FRAME_RATE = 10
""" Image move every n millionseconds when moving cards to destination position """

class GameCanvas(Canvas):
    """
    Represent the canvas that displays playing cards in the game
    """
    
    def __init__(self, root: Tk) -> None:
        """
        Create a game canvas with given root
        
        Parameters:
        - root: root component
        """
        super().__init__(root)
    
    def create_cards(self, cards:list[Card], clicked=None, drag=None, release=None) -> None:
        """
        Create a list of cards on the canvas
        
        Parameters:
        - cards: list of cards
        - action: action to take when the card is clicked
        """
        self.delete("all")
        for card in cards:
            self.create_image(card.x, card.y, image=card.image, tag=card.tag, anchor="nw")
            self.tag_bind(card.tag, "<Button-1>", clicked)
            self.tag_bind(card.tag, "<B1-Motion>", drag)
            self.tag_bind(card.tag, "<ButtonRelease-1>", release)
    
    def start_move_card(self, card: Card, h_gap:int=H_GAP) -> None:
        """
        Place a card to its corresponding position based on the given horizontal gap between cards.
        
        Parameters:
        - card: the card to move.
        - h_gap: the horizontal gap between the top of each card on a stack
        """
        if card.move_id != None: self.after_cancel(card.move_id)
        self.lift(card.tag)
        dest_x = CARD_X + card.stack_idx * (CARD_WIDTH + V_GAP)
        dest_y = CARD_Y + CARD_HEIGHT + H_GAP + card.card_idx * h_gap
        move_x = (dest_x - card.x) // FRAME_RATE
        move_y = (dest_y - card.y) // FRAME_RATE
        self.move_card(card, dest_x, dest_y, move_x, move_y)
    
    def collect_finished(self, cards: list[Card], num: int) -> None:
        """
        Collect a completed set of cards by moving them to top-right area.
        
        Parameters:
        - cards: completed set of cards
        - num: the number of completed set used to calculate destination
        """
        dest_x = CARD_X + (2 + num) * (CARD_WIDTH + V_GAP)
        for card in cards:
            self.tag_unbind(card.tag, "<Button-1>")
            if card.move_id != None: self.after_cancel(card.move_id)
            card.hidden = True
            move_x = (dest_x - card.x) // FRAME_RATE
            move_y = (CARD_Y - card.y) // FRAME_RATE
            self.lift(card.tag)
            self.move_card(card, dest_x, CARD_Y, move_x, move_y)
    
    def move_card(self, card: Card, dest_x: int, dest_y: int, move_x: int, move_y: int) -> None:
        """
        Helper method to create animation of moving card.
        
        Parameters:
        - card: the card to move.
        - dest_x: destination x coordinate of the card.
        - dest_y: destination y coordinate of the card.
        - move_x: how much should the card shift from its current position to the right in one move.
        - move_y: how much should the card shift from its current position to the bottom in one move.
        """
        # Adjust the length of move for the last move of a card
        if move_x != 0 and card.x == dest_x: move_x = 0
        elif abs(move_x) > abs(dest_x - card.x): move_x = dest_x - card.x
        if move_y != 0 and card.y == dest_y: move_y = 0
        elif abs(move_y) > abs(dest_y - card.y): move_y = dest_y - card.y
        # Move the card and update current position
        self.move(card.tag, move_x, move_y)
        card.x += move_x
        card.y += move_y
        # Continue to move card until the card is placed in its destination position
        if card.x != dest_x or card.y != dest_y:
            card.move_id = self.after(FRAME_RATE, lambda: self.move_card(card, dest_x, dest_y, move_x, move_y))
        else:
            card.move_id = None