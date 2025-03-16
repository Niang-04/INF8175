from collections import defaultdict
import random
from player_divercite import PlayerDivercite
from seahorse.game.action import Action
from seahorse.game.game_state import GameState
from game_state_divercite import GameStateDivercite
from seahorse.utils.custom_exceptions import MethodNotImplementedError

import math

class MCTSNode():
    def __init__(self, state: GameStateDivercite, parent=None, action=None, playerId=None):
        self.state = state
        self.parent = parent
        self.action = action
        self.children = []
        self.nVisits = 0
        self.nWins = 0
        self.untriedActions = list(state.generate_possible_light_actions())
        self.playerId = state.next_player.get_id() if state else playerId

    def addChild(self, state, action):
        """
        Adds a child node to the current node
        """
        child = MCTSNode(state=state, parent=self, action=action)
        if action in self.untriedActions:
            self.untriedActions.remove(action)
        self.children.append(child)
        return child
    
    def isFullyExpanded(self):
        """
        Checks if all the different possible actions from a given node have been tried at least once
        """
        return len(self.untriedActions) == 0
    
    def isTerminalAction(self):
        """
        Verifies if the current node represents a terminal game state
        """
        return self.state.is_done()
    
    def expand(self):
        """
        Expands the current node by selecting an untried action and adding it as a child to the current node
        """
        if not self.untriedActions or self.isTerminalAction():
            return self

        action = self.untriedActions.pop()
        nextState = self.state.apply_action(action)
        return self.addChild(state=nextState, parent=self, action=action)


    def selectChild(self, explorationWeight = 1.41421356237):
        """
        Selects a child node using the UCB1 formula and exploration principles
        """
        bestChild = None
        highestUcbValue = float('-inf')

        for child in self.children:
            if child.nVisits == 0:
                return child
            
            exploitationTerm = child.nWins / child.nVisits
            explorationTerm = explorationWeight * math.sqrt(math.log(self.nVisits) / child.nVisits)
            ucbValue = exploitationTerm + explorationTerm

            if ucbValue > highestUcbValue:
                highestUcbValue = ucbValue
                bestChild = child
        
        return bestChild

    
    def backpropagate(self, result, playerId):
        """
        Will add the result recursively to all the parent nodes, of a given node, up to the root of the tree
        """
        self.nVisits += 1
        self.nWins += result if self.playerId == playerId else 1 - result
        if self.parent:
            self.parent.backpropagate(playerId)
    
    def simulate(self, ownerId, simulationDepthLimit=20):
        """
        Knowledge based self-play simulation from the current node to the determine the outcome after a given number of movements.
        It uses the scoring rules of Diversite as a guide in the simulation
        """
        tmpState = self.state
        currDepth = 0

        while not tmpState.is_done() and currDepth < simulationDepthLimit:
            possibleActions = list(tmpState.generate_possible_light_actions())
            if not possibleActions:
                break

            action = self.knowledgeBasedAction(tmpState, possibleActions)
            tmpState.apply_action(action)
            depth += 1

        if not tmpState.is_done() and depth >= simulationDepthLimit:
            return self.evaluateNonTerminalPosition(tmpState, ownerId)

        return self.scoreTerminalState(tmpState, ownerId)
    



class MyPlayer(PlayerDivercite):
    """
    Player class for Divercite game that makes random moves.

    Attributes:
        piece_type (str): piece type of the player
    """

    def __init__(self, piece_type: str, name: str = "MyPlayer"):
        """
        Initialize the PlayerDivercite instance.

        Args:
            piece_type (str): Type of the player's game piece
            name (str, optional): Name of the player (default is "bob")
            time_limit (float, optional): the time limit in (s)
        """
        super().__init__(piece_type, name)
        # Add any information you want to store about the player here
        # self.json_additional_info = {}

    def compute_action(self, current_state: GameState, remaining_time: int = 1e9, **kwargs) -> Action:
        """
        Use the minimax algorithm to choose the best action based on the heuristic evaluation of game states.

        Args:
            current_state (GameState): The current game state.

        Returns:
            Action: The best action as determined by minimax.
        """

        #TODO
        # raise MethodNotImplementedError()
