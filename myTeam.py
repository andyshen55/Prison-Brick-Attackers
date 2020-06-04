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
from baselineTeam import DefensiveReflexAgent, ReflexCaptureAgent
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

class OffensiveAgent(ReflexCaptureAgent):
  def registerInitialState(self, gameState):
    self.start = gameState.getAgentPosition(self.index)
    CaptureAgent.registerInitialState(self, gameState)
    #middlePoints
    self.middleLine = []
    walls = gameState.getWalls()
    middleX = walls.width // 2
    #print(middleX)
    if( not self.red):
      middleX+=1
    y = 0
    while(y < walls.height):
      #print(y)
      if(not gameState.hasWall(middleX, y)):
        tpl = (middleX, y)
        self.middleLine.append(tpl)
      y += 1

  def getFeatures(self, gameState, action):
    # score differential as feature
    features = util.Counter()
    successor = self.getSuccessor(gameState, action)
    features['score'] = self.getScore(successor) - self.getScore(gameState)

    agent = successor.getAgentState(self.index)
    myPos = agent.getPosition()
    carrying = agent.numCarrying
    features['carrying'] = carrying

    foodList = self.getFood(successor).asList()
    capsules = self.getCapsules(gameState)
    opponents = [gameState.getAgentState(agentIndex) for agentIndex in self.getOpponents(gameState)]
    defenders = [agent for agent in opponents if not agent.isPacman and agent.getPosition() != None]

    # Compute distance to the nearest food
    if len(foodList): # This should always be True,  but better safe than sorry
      minDistance = min([self.getMazeDistance(myPos, food) for food in foodList])
      features['closestFood'] = minDistance
    features['foodRemaining'] = len(foodList)

    # Compute distance to nearest defender, same check in case defender just died
    if len(defenders):
      numAdjacent = 0
      distances = [self.getMazeDistance(myPos, defender.getPosition()) for defender in defenders]
      for defender in distances:
        if defender <= 2:
          numAdjacent += 1
      features['adjacentDefenders'] = numAdjacent

    # nearest capsule weight
    if len(capsules):
      nearestCapsule = min([self.getMazeDistance(myPos, capsule) for capsule in capsules])
      features['nearestCapsule'] = nearestCapsule
    else:
      features['nearestCapsule'] = -1

    # get distance to own territory (safe)
    midLine = self.middleLine
    distanceFromMidline = min([self.getMazeDistance(myPos, square) for square in self.middleLine])

    features['distanceFromMidline'] = distanceFromMidline
    features['stop'] = (action == 'Stop')

    return features


  def getWeights(self, gameState, action):
    # score differential as feature
    successor = self.getSuccessor(gameState, action)
    agent = successor.getAgentState(self.index)
    carrying = agent.numCarrying

    midWeight = 0
    if carrying:
      midWeight = - (carrying ** 2)

    return {'score': 1000, 'closestFood': -2, 'carrying': 100, 'adjacentDefenders':-150, 'distanceFromMidline': midWeight, 'stop': -1000}


  def evaluate(self, gameState, action):
    features = self.getFeatures(gameState, action)
    weights = self.getWeights(gameState, action)
    score = features * weights

    # if features['distanceFromMidline'] < 5:
    #   print(features)
    #   print(weights)
    #   print(action, score)
    #   input()

    return features * weights


  def chooseAction(self, gameState):
    """
    Picks among the actions with the highest Q(s,a).
    """
    actions = gameState.getLegalActions(self.index)
    # print(actions)
    # input()
    values = [self.evaluate(gameState, a) for a in actions]

    # start = time.time()
    # print 'eval time for agent %d: %.4f' % (self.index, time.time() - start)

    maxValue = max(values)
    bestActions = [a for a, v in zip(actions, values) if v == maxValue]

    # print('Chosen action:', bestActions)
    # print(self.getFeatures(gameState, bestActions[0]))
    # input()
    # print('Score:', maxValue)
    # input()

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
