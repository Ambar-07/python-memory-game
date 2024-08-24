import random
import pygame
import sys
from pygame.locals import *

class MemoryGame:
    def _init_(self):
        self.FPS = 30
        self.WINDOWWIDTH = 640
        self.WINDOWHEIGHT = 480
        self.REVEALSPEED = 8
        self.BOXSIZE = 40
        self.GAPSIZE = 10
        self.BOARDWIDTH = 10
        self.BOARDHEIGHT = 7
        self.XMARGIN = int((self.WINDOWWIDTH - (self.BOARDWIDTH * (self.BOXSIZE + self.GAPSIZE))) / 2)
        self.YMARGIN = int((self.WINDOWHEIGHT - (self.BOARDHEIGHT * (self.BOXSIZE + self.GAPSIZE))) / 2)

        self.GRAY = (100, 100, 100)
        self.NAVYBLUE = (60, 60, 100)
        self.WHITE = (255, 255, 255)
        self.RED = (255, 0, 0)
        self.GREEN = (0, 255, 0)
        self.BLUE = (0, 0, 255)
        self.YELLOW = (255, 255, 0)
        self.ORANGE = (255, 128, 0)
        self.PURPLE = (255, 0, 255)
        self.CYAN = (0, 255, 255)

        self.BGCOLOR = self.NAVYBLUE
        self.LIGHTBGCOLOR = self.GRAY
        self.BOXCOLOR = self.WHITE
        self.HIGHLIGHTCOLOR = self.BLUE

        self.SQUARE = 'square'
        self.DONUT = 'donut'
        self.DIAMOND = 'diamond'
        self.LINES = 'lines'
        self.OVAL = 'oval'

        self.ALLCOLORS = (self.RED, self.GREEN, self.BLUE, self.YELLOW, self.ORANGE, self.PURPLE, self.CYAN)
        self.ALLSHAPES = (self.DONUT, self.SQUARE, self.DIAMOND, self.LINES, self.OVAL)

        self.mousex = 0
        self.mousey = 0

        pygame.init()
        self.FPSCLOCK = pygame.time.Clock()
        self.DISPLAYSURF = pygame.display.set_mode((self.WINDOWWIDTH, self.WINDOWHEIGHT))
        pygame.display.set_caption('Memory Game')
        self.play()

    def play(self):
        self.mainBoard = self.getRandomizedBoard()
        self.revealedBoxes = self.generateRevealedBoxesData(False)

        self.firstSelection = None

        self.DISPLAYSURF.fill(self.BGCOLOR)
        self.startGameAnimation(self.mainBoard)

        while True:
            self.mouseClicked = False

            self.DISPLAYSURF.fill(self.BGCOLOR)
            self.drawBoard(self.mainBoard, self.revealedBoxes)

            for event in pygame.event.get():
                if event.type == QUIT or (event.type == KEYUP and event.key == K_ESCAPE):
                    pygame.quit()
                    sys.exit()
                elif event.type == MOUSEMOTION:
                    self.mousex, self.mousey = event.pos
                elif event.type == MOUSEBUTTONUP:
                    self.mousex, self.mousey = event.pos
                    self.mouseClicked = True

            self.boxx, self.boxy = self.getBoxAtPixel(self.mousex, self.mousey)
            if self.boxx is not None and self.boxy is not None:
                if not self.revealedBoxes[self.boxx][self.boxy]:
                    self.drawHighlightBox(self.boxx, self.boxy)
                if not self.revealedBoxes[self.boxx][self.boxy] and self.mouseClicked:
                    self.revealBoxesAnimation(self.mainBoard, [(self.boxx, self.boxy)])
                    self.revealedBoxes[self.boxx][self.boxy] = True
                    if self.firstSelection is None:
                        self.firstSelection = (self.boxx, self.boxy)
                    else:
                        icon1shape, icon1color = self.getShapeAndColor(self.mainBoard, self.firstSelection[0], self.firstSelection[1])
                        icon2shape, icon2color = self.getShapeAndColor(self.mainBoard, self.boxx, self.boxy)

                        if icon1shape != icon2shape or icon1color != icon2color:
                            pygame.time.wait(1000)
                            self.coverBoxesAnimation(self.mainBoard, [self.firstSelection, (self.boxx, self.boxy)])
                            self.revealedBoxes[self.firstSelection[0]][self.firstSelection[1]] = False
                            self.revealedBoxes[self.boxx][self.boxy] = False
                        elif self.hasWon(self.revealedBoxes):
                            self.gameWonAnimation(self.mainBoard)
                            pygame.time.wait(2000)

                            self.mainBoard = self.getRandomizedBoard()
                            self.revealedBoxes = self.generateRevealedBoxesData(False)

                            self.drawBoard(self.mainBoard, self.revealedBoxes)
                            pygame.display.update()
                            pygame.time.wait(1000)

                            self.startGameAnimation(self.mainBoard)
                        self.firstSelection = None

            pygame.display.update()
            self.FPSCLOCK.tick(self.FPS)

    def generateRevealedBoxesData(self, val):
        revealedBoxes = []
        for i in range(self.BOARDWIDTH):
            revealedBoxes.append([val] * self.BOARDHEIGHT)
        return revealedBoxes

    def getRandomizedBoard(self):
        # Get a list of every possible shape in every possible color.
        icons = []
        for color in self.ALLCOLORS:
            for shape in self.ALLSHAPES:
                icons.append((shape, color))

        random.shuffle(icons)
        numIconsUsed = int(self.BOARDWIDTH * self.BOARDHEIGHT / 2)
        icons = icons[:numIconsUsed] * 2
        random.shuffle(icons)

        # Create the board data structure, with randomly placed icons.
        board = []
        for x in range(self.BOARDWIDTH):
            column = []
            for y in range(self.BOARDHEIGHT):
                column.append(icons[0])
                del icons[0]
            board.append(column)
        return board

    def splitIntoGroupsOf(self, groupSize, theList):
        # splits a list into a list of lists, where the inner lists have at
        # most groupSize number of items.
        result = []
        for i in range(0, len(theList), groupSize):
            result.append(theList[i:i + groupSize])
        return result

    def leftTopCoordsOfBox(self, boxx, boxy):
        # Convert board coordinates to pixel coordinates
        left = boxx * (self.BOXSIZE + self.GAPSIZE) + self.XMARGIN
        top = boxy * (self.BOXSIZE + self.GAPSIZE) + self.YMARGIN
        return (left, top)

    def getBoxAtPixel(self, x, y):
        for boxx in range(self.BOARDWIDTH):
            for boxy in range(self.BOARDHEIGHT):
                left, top = self.leftTopCoordsOfBox(boxx, boxy)
                boxRect = pygame.Rect(left, top, self.BOXSIZE, self.BOXSIZE)
                if boxRect.collidepoint(x, y):
                    return (boxx, boxy)
        return (None, None)

    def drawIcon(self, shape, color, boxx, boxy):
        quarter = int(self.BOXSIZE * 0.25)
        half = int(self.BOXSIZE * 0.5)

        left, top = self.leftTopCoordsOfBox(boxx, boxy)
        # Draw the shapes
        if shape == self.DONUT:
            pygame.draw.circle(self.DISPLAYSURF, color, (left + half, top + half), half - 5)
            pygame.draw.circle(self.DISPLAYSURF, self.BGCOLOR, (left + half, top + half), quarter - 5)
        elif shape == self.SQUARE:
            pygame.draw.rect(self.DISPLAYSURF, color, (left + quarter, top + quarter, self.BOXSIZE - half, self.BOXSIZE - half))
        elif shape == self.DIAMOND:
            pygame.draw.polygon(self.DISPLAYSURF, color, ((left + half, top), (left + self.BOXSIZE - 1, top + half),
                                                         (left + half, top + self.BOXSIZE - 1), (left, top + half)))
        elif shape == self.LINES:
            for i in range(0, self.BOXSIZE, 4):
                pygame.draw.line(self.DISPLAYSURF, color, (left, top + i), (left + i, top))
                pygame.draw.line(self.DISPLAYSURF, color, (left + i, top + self.BOXSIZE - 1), (left + self.BOXSIZE - 1, top + i))
        elif shape == self.OVAL:
            pygame.draw.ellipse(self.DISPLAYSURF, color, (left, top + quarter, self.BOXSIZE, half))

    def getShapeAndColor(self, board, boxx, boxy):
        return board[boxx][boxy][0], board[boxx][boxy][1]

    def drawBoxCovers(self, board, boxes, coverage):
        for box in boxes:
            left, top = self.leftTopCoordsOfBox(box[0], box[1])
            pygame.draw.rect(self.DISPLAYSURF, self.BGCOLOR, (left, top, self.BOXSIZE, self.BOXSIZE))
            shape, color = self.getShapeAndColor(board, box[0], box[1])
            self.drawIcon(shape, color, box[0], box[1])
            if coverage > 0:
                pygame.draw.rect(self.DISPLAYSURF, self.BOXCOLOR, (left, top, coverage, self.BOXSIZE))
        pygame.display.update()
        self.FPSCLOCK.tick(self.FPS)

    def revealBoxesAnimation(self, board, boxesToReveal):
        for coverage in range(self.BOXSIZE, (-self.REVEALSPEED) - 1, -self.REVEALSPEED):
            self.drawBoxCovers(board, boxesToReveal, coverage)

    def coverBoxesAnimation(self, board, boxesToCover):
        for coverage in range(0, self.BOXSIZE + self.REVEALSPEED, self.REVEALSPEED):
            self.drawBoxCovers(board, boxesToCover, coverage)

    def drawBoard(self, board, revealed):
        for boxx in range(self.BOARDWIDTH):
            for boxy in range(self.BOARDHEIGHT):
                left, top = self.leftTopCoordsOfBox(boxx, boxy)
                if not revealed[boxx][boxy]:
                    pygame.draw.rect(self.DISPLAYSURF, self.BOXCOLOR, (left, top, self.BOXSIZE, self.BOXSIZE))
                else:
                    shape, color = self.getShapeAndColor(board, boxx, boxy)
                    self.drawIcon(shape, color, boxx, boxy)

    def drawHighlightBox(self, boxx, boxy):
        left, top = self.leftTopCoordsOfBox(boxx, boxy)
        pygame.draw.rect(self.DISPLAYSURF, self.HIGHLIGHTCOLOR, (left - 5, top - 5, self.BOXSIZE + 10, self.BOXSIZE + 10), 4)

    def startGameAnimation(self, board):
        coveredBoxes = self.generateRevealedBoxesData(False)
        boxes = []
        for x in range(self.BOARDWIDTH):
            for y in range(self.BOARDHEIGHT):
                boxes.append((x, y))
        random.shuffle(boxes)
        boxGroups = self.splitIntoGroupsOf(8, boxes)

        self.drawBoard(board, coveredBoxes)
        for boxGroup in boxGroups:
            self.revealBoxesAnimation(board, boxGroup)
            self.coverBoxesAnimation(board, boxGroup)

    def gameWonAnimation(self, board):
        coveredBoxes = self.generateRevealedBoxesData(True)
        color1 = self.LIGHTBGCOLOR
        color2 = self.BGCOLOR

        for i in range(13):
            color1, color2 = color2, color1
            self.DISPLAYSURF.fill(color1)
            self.drawBoard(board, coveredBoxes)
            pygame.display.update()
            pygame.time.wait(300)

    def hasWon(self, revealedBoxes):
        for i in revealedBoxes:
            if False in i:
                return False
        return True


if _name_ == '_main_':
    game = MemoryGame()