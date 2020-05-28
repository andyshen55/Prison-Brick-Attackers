# myTeam.py
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
import baselineTeam
import distanceCalculator
import random, time, util
from game import Directions
import game
from util import nearestPoint

#################
# Team creation #
#################

def createTeam(firstIndex, secondIndex, isRed,
               first='OffensiveAgent', second='DefensiveReflexAgent'):
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


class ReflexCaptureAgent(CaptureAgent):
  """
  A base class for reflex agents that chooses score-maximizing actions
  """
 
  def registerInitialState(self, gameState):
    self.start = gameState.getAgentPosition(self.index)
    CaptureAgent.registerInitialState(self, gameState)

  def chooseAction(self, gameState):
    """
    Picks among the actions with the highest Q(s,a).
    """
    actions = gameState.getLegalActions(self.index)

    # You can profile your evaluation time by uncommenting these lines
    # start = time.time()
    values = [self.evaluate(gameState, a) for a in actions]
    # print 'eval time for agent %d: %.4f' % (self.index, time.time() - start)

    maxValue = max(values)
    bestActions = [a for a, v in zip(actions, values) if v == maxValue]

    foodLeft = len(self.getFood(gameState).asList())

    if foodLeft <= 2:
      bestDist = 9999
      for action in actions:
        successor = self.getSuccessor(gameState, action)
        pos2 = successor.getAgentPosition(self.index)
        dist = self.getMazeDistance(self.start,pos2)
        if dist < bestDist:
          bestAction = action
          bestDist = dist
      return bestAction

    return random.choice(bestActions)

  def getSuccessor(self, gameState, action):
    """
    Finds the next successor which is a grid position (location tuple).
    """
    successor = gameState.generateSuccessor(self.index, action)
    pos = successor.getAgentState(self.index).getPosition()
    if pos != nearestPoint(pos):
      # Only half a grid position was covered
      return successor.generateSuccessor(self.index, action)
    else:
      return successor

  def evaluate(self, gameState, action):
    """
    Computes a linear combination of features and feature weights
    """
    features = self.getFeatures(gameState, action)
    weights = self.getWeights(gameState, action)
    return features * weights


class OffensiveAgent(ReflexCaptureAgent):
  def getFeatures(self, gameState, action):
    features = util.Counter()
    successor = self.getSuccessor(gameState, action)
    foodList = self.getFood(successor).asList()    
    features['successorScore'] = -len(foodList)#self.getScore(successor)

    # Compute distance to the nearest food

    if len(foodList) > 0: # This should always be True,  but better safe than sorry
      myPos = successor.getAgentState(self.index).getPosition()
      minDistance = min([self.getMazeDistance(myPos, food) for food in foodList])
      features['distanceToFood'] = minDistance
    return features


    # features = util.Counter()
    # successor = self.getSuccessor(gameState, action)
    # foodList = self.getFood(successor).asList()    
    # features['successorScore'] = self.getScore(successor)

    # agent = successor.getAgentState(self.index)
    # myPos = agent.getPosition()
    # capsules = self.getCapsules(gameState)
    # features['carrying'] = agent.numCarrying

    # opponents = [gameState.getAgentState(agentIndex) for agentIndex in self.getOpponents(gameState)]
    # defenders = [agent for agent in opponents if not agent.isPacman and agent.getPosition() != None]
    # adjacentGhosts = 0

    # # Compute distance to the nearest food
    # if len(foodList) > 0: # This should always be True,  but better safe than sorry
    #   minDistance = min([self.getMazeDistance(myPos, food) for food in foodList])
    #   features['distanceToFood'] = minDistance
    
    # # Compute distance to nearest defender, same check in case defender just died
    # if len(defenders):
    #   distances = [self.getMazeDistance(myPos, defender.getPosition()) for defender in defenders]
    #   nearestDefender = min(distances)
    #   features['nearestDefender'] = nearestDefender
    #   for defender in distances:
    #     if defender <= 2:
    #       adjacentGhosts += 1
    # features['adjacentGhosts'] = adjacentGhosts

    # # nearest capsule weight
    # if len(capsules):
    #   nearestCapsule = min([self.getMazeDistance(myPos, capsule) for capsule in capsules])
    #   features['nearestCapsule'] = nearestCapsule
    # else:
    #   features['nearestCapsule'] = -1
    

    # # get distance to own territory (safe)
    # redMidline = [(15,1), (15,2), (15,4), (15,5), (15,7), (15,8), (15,11), (15,12), (15,13), (15,14)]
    # blueMidline =  [(16,1), (16,2), (16,3), (16,4), (16,7), (16,8), (16,10), (16,11), (16,13), (16,14)]   
    # if self.red:
    #   distanceFromMidline = min([self.getMazeDistance(myPos, square) for square in redMidline])
    # else:
    #   distanceFromMidline = min([self.getMazeDistance(myPos, square) for square in blueMidline])
    # features['distanceFromMidline'] = distanceFromMidline
    
    # return features


  def getWeights(self, gameState, action):
    return {'successorScore': 100, 'distanceToFood': -1}

  def d2m(self, gameState):
    #returns distance to their middle border
    walls = gameState.getWalls()
    walls_width = len(walls[0]) #gets width of stage
    middle_x = walls // 2 #edge of red
    if( not gameState.isOnRedTeam(self.index)):
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

class DefensiveReflexAgent(ReflexCaptureAgent):
  """
  A reflex agent that keeps its side Pacman-free. Again,
  this is to give you an idea of what a defensive agent
  could be like.  It is not the best or only way to make
  such an agent.
  """

  def getFeatures(self, gameState, action):
    features = util.Counter()
    successor = self.getSuccessor(gameState, action)

    myState = successor.getAgentState(self.index)
    myPos = myState.getPosition()

    # Computes whether we're on defense (1) or offense (0)
    features['onDefense'] = 1
    if myState.isPacman: features['onDefense'] = 0

    # Computes distance to invaders we can see
    enemies = [successor.getAgentState(i) for i in self.getOpponents(successor)]
    invaders = [a for a in enemies if a.isPacman and a.getPosition() != None]
    features['numInvaders'] = len(invaders)
    if len(invaders) > 0:
      dists = [self.getMazeDistance(myPos, a.getPosition()) for a in invaders]
      features['invaderDistance'] = min(dists)

    if action == Directions.STOP: features['stop'] = 1
    rev = Directions.REVERSE[gameState.getAgentState(self.index).configuration.direction]
    if action == rev: features['reverse'] = 1

    return features

  def getWeights(self, gameState, action):
    return {'numInvaders': -1000, 'onDefense': 100, 'invaderDistance': -10, 'stop': -100, 'reverse': -2}
