cd # myTeam.py
# ---------
# Licensing Information:  You are free to use or extend these projects for
# educational purposes provided that (1) you do not distribute or publish
# solutions, (2) you retain this notice, and (3) you provide clear
# attribution to UC Berkeley, including a link to http://ai.berkeley.edu.
#
# Attribution Information: The Pacman AI projects were developed at UC Berkeley.
# The core projects and autograders were primarily created by John DeNero
# (denero@cs.berkeley.edu) and Dan Klein (klein@cs.berkeley.edu).
# Student side autograding was added by Brad Miller, Nick Hay, and
# Pieter Abbeel (pabbeel@cs.berkeley.edu).


from captureAgents import CaptureAgent
import random, time, util
from game import Directions
import game

#################
# Team creation #
#################

def createTeam(firstIndex, secondIndex, isRed,
               first = 'DummyAgent', second = 'DummyAgent'):
  """
  This function should return a list of two agents that will form the
  team, initialized using firstIndex and secondIndex as their agent
  index numbers.  isRed is True if the red team is being created, and
  will be False if the blue team is being created.

  As a potentially helpful development aid, this function can take
  additional string-valued keyword arguments ("first" and "second" are
  such arguments in the case of this function), which will come from
  the --redOpts and --blueOpts command-line arguments to capture.py.
  For the nightly contest, however, your team will be created without
  any extra arguments, so you should make sure that the default
  behavior is what you want for the nightly contest.
  """

  # The following line is an example only; feel free to change it.
  return [eval(first)(firstIndex), eval(second)(secondIndex)]

##########
# Agents #
##########

class DummyAgent(CaptureAgent):
  """
  A Dummy agent to serve as an example of the necessary agent structure.
  You should look at baselineTeam.py for more details about how to
  create an agent as this is the bare minimum.
  """

  def registerInitialState(self, gameState):
    """
    This method handles the initial setup of the
    agent to populate useful fields (such as what team
    we're on).

    A distanceCalculator instance caches the maze distances
    between each pair of positions, so your agents can use:
    self.distancer.getDistance(p1, p2)

    IMPORTANT: This method may run for at most 15 seconds.
    """
    #self.start = gameState.getAgentPosition(self.index)
    '''
    Make sure you do not delete the following line. If you would like to
    use Manhattan distances instead of maze distances in order to save
    on initialization time, please take a look at
    CaptureAgent.registerInitialState in captureAgents.py.
    '''
    CaptureAgent.registerInitialState(self, gameState)

    '''
    Your initialization code goes here, if you need any.
    '''


  def chooseAction(self, gameState):
    """
    Picks among actions randomly.
    """
    actions = gameState.getLegalActions(self.index)
    values = [self.evaluate(gameState, a) for a in actions]
    maxValue = max(values)
    bestActions = [a for a, v in zip(actions, values) if v == maxValue]
    '''
    You should change this in your own agent.
    '''

    return random.choice(bestActions)


  def evaluate(self, gameState, action):
    """
    Computes a linear combination of features and feature weights
    """
    features = self.getFeatures(gameState, action)
    weights = self.getWeights(gameState, action)
    return features * weights


  def getFeatures(self, gameState, action):
    """
    Returns a counter of features for the state
    """
    features = util.Counter()
    successor = self.generateSuccessor(gameState, action)
    features['successorScore'] = self.getScore(successor)
    """
    Possible features:
    score
    ditance to middle
    iswin/isloss
    time remaining (inverse?)
    pellets remaining
    pp remaining
    distance from pellets and pp
    distance from enemies
    scared ghosts?
    isTrap
    number of enemies on our territory
    pellets held
    when should we go back?
    """
    return features

  def getWeights(self, gameState, action):
    """
    Normally, weights do not depend on the gamestate.  They can be either
    a counter or a dictionary.
    """
    return {'successorScore': 1.0}

  def d2m(self, gameState):
    #returns distance to their middle border
    walls = gameState.getWalls()
    walls_width = len(walls[0]) #gets width of stage
    middle_x = walls // 2 #edge of red
    if(!gameState.isOnRedTeam(self.index)):
        middle_x += 1 #blue border
    pos = gameState.getAgentPosition(self.index)#gets pos of current agent
    return self.getMazeDistance(pos, (middle_x, pos[1]))


  def isTrap(self, gameState, x, y):
    #returns true if surreounded by walls with only
    #one exit, assumes given non edge coords
    walls = 0
    if(gameState.hasWall(x+1, y)):
        walls +=1
    if(gameState.hasWall(x-1, y)):
        walls +=1
    if(gameState.hasWall(x, y+1)):
        walls +=1
    if(gameState.hasWall(x, y-1)):
        walls +=1
    #im sure theres a neater way to do this but its not coming to me
    if(walls >=3):
        return True
    #might have to switch to 1 and 0 if we cant mult by weight
    return False
