from Card import *
from random import randint

class CardSet:
    """
    Represent a set of cards used in the game
    """
    
    def __init__(self, cards: dict[str, Card]) -> None:
        """
        Create a set of cards.
        
        Parameters:
        - cards: predefined cards with images
        """
        self.cards = cards
        """ All cards with tags """
        self.stacks: list[list[Card]] = []
        """ Card stacks used to organize cards during the game
        Stack 0-6: dealed cards
        Stack 7: remaining cards after dealing
        Stack 8-11: completed set of cards
        """
        self.old_stacks: list[list[Card]] = []
        """ A copy of the stacks at the beginning of the game """
        self.win_num: int = 0
        """ Number of completed set of cards """
        self.steps: list[tuple] = []
        """ List of steps taken by the user in format (src, dest, length), used for undo """
        
    def switch_stack(self, src: int, dest: int, length: int, add_step: bool=True) -> None:
        """
        Assign a sub-stack from source stack to destinatin stack.
        
        Parameters:
        - src: the source stack
        - dest: the destination stack
        - length: the length of sub-stack
        """
        c_idx = len(self.stacks[dest])
        temp = self.stacks[src][len(self.stacks[src]) - length:]
        self.stacks[dest].extend(temp)
        for i in range(length):
            self.stacks[src].pop()
            temp[i].stack_idx = dest
            temp[i].card_idx = c_idx
            c_idx += 1
        if add_step: self.steps.append((src, dest, length))

    def shuffle_cards(self) -> None:
        """
        Shuffle cards into 7 stacks of cards while make sure there's at least one way to win the game.
        """ 
        # Assign 4 types of cards into 4 stacks by types
        for i in range(4):
            s = list(self.cards.values())[i * 13 : (i + 1) * 13]
            for c in s: c.stack_idx = i
            self.stacks.append(s)
        self.stacks.extend([[], [], [], [], [], [], [], []])
        
        # Shuffle cards into 7 stacks by removing some cards from the end of a stack add them to another stack,
        # but leave at least one card on each stack
        for _ in range(2):
            for i in range(6):
                for j in range(i + 1, 7):
                    # Move some cards from first stack to second stack
                    max = len(self.stacks[i]) - 1 if len(self.stacks[i]) > 0 else 0
                    self.switch_stack(i, j, randint(0, max), False)
                    # Move some cards from second stack to first stack
                    max = len(self.stacks[j]) - 1 if len(self.stacks[j]) > 0 else 0
                    self.switch_stack(j, i, randint(0, max), False)
        
        # Deal three cards to the 8th stack
        for i in range(3):
            self.switch_stack(i, 7, 1, False)
            
        # Shuffle again
        for _ in range(4):
            for i in range(6):
                for j in range(i + 1, 7):
                    # Move some cards from first stack to second stack
                    self.switch_stack(i, j, randint(0, len(self.stacks[i])), False)
                    # Move some cards from second stack to first stack
                    self.switch_stack(j, i, randint(0, len(self.stacks[j])), False)
        
        # Make sure each stack have 7 cards at the end.
        for i in range(7):
            if len(self.stacks[i]) > 7:
                self.switch_stack(i, i + 1, len(self.stacks[i]) - 7, False)
            elif len(self.stacks[i]) < 7:
                j = i + 1
                while len(self.stacks[j]) < 7 - len(self.stacks[i]): j += 1
                self.switch_stack(j, i, 7 - len(self.stacks[i]), False)
    
    def check_stack(self, stack_idx: int) -> bool:
        """
        Check whether the stack has a completed set of cards (all same type order from value 13 to 1).
        If so, collect the completed set.
        
        Parameters:
        - stack_idx: index of the stack to be checked
        
        Return:
        Whether there's a completed set
        """
        completed = len(self.stacks[stack_idx]) > 12
        if completed:
            # Check for completeness
            s = self.stacks[stack_idx][len(self.stacks[stack_idx]) - 13:]
            t = s[0].type
            v = 13
            for c in s:
                if c.type != t or c.value != v:
                    completed = False
                    break
                v -= 1
            # Collect set
            if completed:
                self.win_num += 1
                self.switch_stack(stack_idx, self.win_num + 7, 13)
        return completed
    
    def reset(self, new: bool) -> None:
        """
        Reset the card set to the beginning of the game.
        
        Parameters:
        - new: whether the user is starting a new game.
        """
        self.stacks.clear()
        self.steps.clear()
        self.win_num = 0
        for c in self.cards.values():
            c.x = CARD_X
            c.y = CARD_Y
            c.hidden = False
        if new:     # Starting a new game
            self.old_stacks.clear()
            for c in self.cards.values():
                c.stack_idx = -1
                c.stack_idx = c.value - 1
        else:       # Restarting the current game
            for i in range(7):
                for j in range(len(self.old_stacks[i])):
                    c = self.old_stacks[i][j]
                    c.stack_idx = i
                    c.card_idx = j
            for i in range(3):
                c = self.old_stacks[7][i]
                c.stack_idx = 7
                c.card_idx = i