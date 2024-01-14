from Card import *
from tkinter import Canvas, Tk, BOTH

FRAME_RATE = 5
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
    
    def create_cards(self, cards:list[Card], action=None) -> None:
        """
        Create a list of cards on the canvas
        
        Parameters:
        - cards: list of cards
        - action: action to take when the card is clicked
        """
        self.delete("all")
        for card in cards:
            self.create_image(card.x, card.y, image=card.image, tag=card.tag, anchor="nw")
            self.tag_bind(card.tag, "<Button-1>", action)
    
    def start_move_card(self, card: Card, h_gap:int=H_GAP) -> None:
        """
        Place a card to its corresponding position based on the given horizontal gap between cards.
        
        Parameters:
        - card: the card to move.
        - h_gap: the horizontal gap between the top of each card on a stack
        """
        self.lift(card.tag)
        dest_x = CARD_X + card.stack_idx * (CARD_WIDTH + V_GAP)
        dest_y = CARD_Y + CARD_HEIGHT + (card.card_idx + 1) * h_gap
        move_x = (dest_x - card.x) // 20
        move_y = (dest_y - card.y) // 20
        self.move_card(card, dest_x, dest_y, move_x, move_y)
    
    def collect_finished(self, cards: list[Card], num: int) -> None:
        pass
    
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
        if abs(move_x) > abs(dest_x - card.x): move_x = dest_x - card.x
        if abs(move_y) > abs(dest_y - card.y): move_y = dest_y - card.y
        # Move the card and update current position
        self.move(card.tag, move_x, move_y)
        card.x += move_x
        card.y += move_y
        # Continue to move card until the card is placed in its destination position
        if card.x != dest_x or card.y != dest_y:
            self.after(FRAME_RATE, lambda: self.move_card(card, dest_x, dest_y, move_x, move_y))