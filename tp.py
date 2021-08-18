import math, string, random
#CITATION: all graphics from cmu_112_graphics https://www.cs.cmu.edu/~112/notes/notes-graphics.html
from cmu_112_graphics import *

#Instructions Margin
rightMargin = 500

#Classes
class Player(object):
    def __init__(self, app, maze):
        self.app = app
        self.x, self.y, self.x1, self.y1, c, d = getCellBounds(app, 0, 0)
        self.row, self.col = getCell(self.app, self.x, self.y)
        self.color = "blue"
        self.maze = maze
        self.mazeCoord = self.maze[self.row][self.col]
        self.lives = 3
        
    def move(self, dx, dy):
        self.x += dx
        self.y += dy
        self.x1 += dx
        self.y1 += dy
        n, e, s, w = self.mazeCoord.getWallStatus()
        if dx > 0 and e:
            self.x -= dx 
            self.x1 -= dx
        elif dx < 0 and w:
            self.x -= dx
            self.x1 -= dx
        elif dy > 0 and s:
            self.y -= dy
            self.y1 -= dy
        elif dy < 0 and n:
            self.y -= dy
            self.y1 -= dy
        self.row, self.col = getCell(self.app, self.x+3, self.y+3)
        self.mazeCoord = self.maze[self.row][self.col]
        eRow, eCol = self.app.enemy.getLocation()
        fRow, fCol = self.app.food.getLocation()
        if self.mazeCoord == self.app.exit and self.app.mode == "normalMode":
            self.app.gameOver = True
        elif self.mazeCoord == self.app.aiExit and self.app.mode == "aiMode":
            self.app.gameOver = True
        if self.row == fRow and self.col == fCol:
            self.app.livesLeft += self.app.food.lifeValue
            self.app.food.moveFood()
        if self.mazeCoord == self.maze[eRow][eCol]:
            self.app.livesLeft -= 1
            if self.app.livesLeft <= 0:
                self.app.gameOver = True
                return
    
    def getCurrentPosition(self):
        return self.row, self.col

    def draw(self, canvas):
        canvas.create_oval(self.x + 3, self.y + 3, self.x1 - 3, self.y1 - 3, fill=self.color)
    
class Cell(object):
    def __init__(self, app, row, col):
        self.app = app
        self.row = row
        self.col = col
        self.w = True
        self.e = True
        self.n = True
        self.s = True

    def changeWallStatus(self, other, dir):
        if dir == "e":
            self.e = False
            other.w = False
        elif dir == "w":
            self.w = False
            other.e = False
        elif dir == "n":
            self.n = False
            other.s = False
        elif dir == "s":
            self.s = False
            other.n = False

    def getWallStatus(self):
        return self.n, self.e, self.s, self.w

    def getLocation(self):
        return (self.row, self.col)

    def __repr__(self):
        return f"({self.row}, {self.col})"

class Enemy(object):
    def __init__(self, app, maze):
        self.app = app
        self.x, self.y, a, b, c, d = getCellBounds(app, self.app.rows - 3, self.app.cols - 10)
        self.r = c / 2 - 3
        self.x += c / 2
        self.y += d / 2
        self.row, self.col = getCell(self.app, self.x, self.y)
        self.color = "yellow"
        self.maze = maze
        self.mazeCoord = self.maze[self.row][self.col]
        self.path = []

    def updatePosition(self):
        pRow, pCol = self.app.player.getCurrentPosition()
        if self.maze[self.row][self.col] == self.maze[pRow][pCol]:
            self.app.livesLeft -= 1
            if self.app.livesLeft <= 0:
                self.app.gameOver = True
                return
            randRow = random.randint(0, self.app.rows  - 1)
            randCol = random.randint(0, self.app.cols - 1)
            self.x, self.y, a, b, c, d = getCellBounds(self.app, randRow, randCol)
            self.x += c / 2
            self.y += d / 2
            self.row, self.col = getCell(self.app, self.x, self.y)
            self.findPath()

        if self.app.enemyPath != []:
            loc = self.app.enemyPath.pop()
            drow, dcol = loc.getLocation()
            self.x, self.y, a, b, c, d = getCellBounds(self.app, drow, dcol)
            self.x += c / 2
            self.y += d / 2
            self.row, self.col = getCell(self.app, self.x, self.y)

    def findPath(self):
        self.app.enemyPath = []
        startCell = self.maze[self.row][self.col]
        eRow, eCol = self.app.player.getCurrentPosition()
        endCell = self.maze[eRow][eCol]
        autoSolver(self.app, startCell, endCell, self.app.enemyPath)
    
    def getLocation(self):
        return self.row, self.col

    def draw(self, canvas):
        canvas.create_oval(self.x - self.r, self.y - self.r, self.x + self.r, self.y + self.r, fill=self.color)

class AIRacer(Enemy):
    def __init__(self, app, maze):
        self.app = app
        self.x, self.y, a, b, c, d = getCellBounds(app, 0, self.app.cols - 1)
        self.r = c / 2 - 3
        self.x += c / 2
        self.y += d / 2
        self.row, self.col = getCell(self.app, self.x, self.y)
        self.color = "yellow"
        self.maze = maze
        self.mazeCoord = self.maze[self.row][self.col]
        self.path = []

    def updatePosition(self):
        if self.maze[self.row][self.col] == self.app.aiExit:
            self.app.gameOver = True
            return
        if self.app.aiPath != []:
            loc = self.app.aiPath.pop()
            drow, dcol = loc.getLocation()
            self.x, self.y, a, b, c, d = getCellBounds(self.app, drow, dcol)
            self.x += c / 2
            self.y += d / 2
            self.row, self.col = getCell(self.app, self.x, self.y)

    def findPath(self):
        self.app.aiPath = []
        startCell = self.maze[self.row][self.col]
        endCell = self.app.aiExit
        autoSolver(self.app, startCell, endCell, self.app.aiPath)

class Button(object):
    def __init__(self, x0, y0, x1, y1, text):
        self.x0 = x0
        self.y0 = y0
        self.x1 = x1
        self.y1 = y1
        self.text = text
    
    def getCoordinates(self):
        return self.x0, self.y0, self.x1, self.y1

    def draw(self, canvas):
        canvas.create_rectangle(self.x0, self.y0, self.x1, self.y1, fill="pink")
        canvas.create_text(self.x0 + (self.x1 - self.x0) / 2, self.y0 + (self.y1 - self.y0) / 2, text=self.text, font="Helveltica 15 bold")

    def isClicked(self, x, y):
        if self.x0 <= x <= self.x1 and self.y0 <= y <= self.y1:
            return True
        return False

class Menu(object):
    def __init__(self, app):
        self.app = app
        self.normalButton = Button(self.app.width / 3 - 50, self.app.height / 3, self.app.width / 2  + 300, self.app.height / 3 + 50, "Normal Mode")
        self.aiButton = Button(self.app.width / 3 - 50, self.app.height / 3 + 100, self.app.width / 2  + 300, self.app.height / 3 + 150, "AI Race Mode")
        self.easyLevelButton = Button(self.app.width / 3 - 50, self.app.height / 3, self.app.width / 2  + 300, self.app.height / 3 + 50, "Easy (10x10)")
        self.normalLevelButton = Button(self.app.width / 3 - 50, self.app.height / 3 + 100, self.app.width / 2  + 300, self.app.height / 3 + 150, "Normal (20x20)")
        self.hardLevelButton = Button(self.app.width / 3 - 50, self.app.height / 3 + 200, self.app.width / 2  + 300, self.app.height / 3 + 250, "Hard (40x40)")
        self.backButton = Button(self.app.width / 3 - 50, self.app.height / 3 + 300, self.app.width / 2  + 300, self.app.height / 3 + 350, "Back to Main Menu")
        self.normalExitButton = Button(self.app.width * 3 / 4, self.app.height * 2 / 3, self.app.width * 3 / 4  + 300, self.app.height * 2 / 3 + 50, "Back to Level Selection")
        self.aiExitButton = Button(self.app.width * 3 / 4, self.app.height * 2 / 3, self.app.width * 3 / 4  + 300, self.app.height * 2 / 3 + 50, "Back to Main menu")

    def drawMainMenu(self, canvas):
        self.normalButton.draw(canvas)
        self.aiButton.draw(canvas)

    def drawLevelSelect(self, canvas):
        self.easyLevelButton.draw(canvas)
        self.normalLevelButton.draw(canvas)
        self.hardLevelButton.draw(canvas)
        self.backButton.draw(canvas)

    def drawExit(self, canvas):
        canvas.create_text(self.app.width * 3 / 4 - 100, self.app.height * 1/7, text="Instructions:", font="Helveltica 20 bold", anchor="w")
        canvas.create_text(self.app.width * 3 / 4 - 100, self.app.height * 1/7 + 50, text="Reach the exit before it changes, avoid enemies!\nEat food (orange) to gain back lives", font="Helveltica 15 bold", anchor="w")
        canvas.create_text(self.app.width * 3 / 4 - 100, self.app.height * 1/7 + 100, text="Use W, A, S, D to move", font="Helveltica 15 bold", anchor="w")
        canvas.create_text(self.app.width * 3 / 4 - 100, self.app.height * 1/7 + 150, text="Press 'h' for a hint. Press 'z' for the solution path.\nNote: Using solutions ends the game", font="Helveltica 15 bold", anchor="w")
        canvas.create_text(self.app.width * 3 / 4 - 100, self.app.height * 1/7 + 210, text="Press 'p' to pause/unpause. Press 'r' to reset,\nor play again!", font="Helveltica 15 bold", anchor="w")
        self.normalExitButton.draw(canvas)

    def drawAiExit(self, canvas):
        canvas.create_text(self.app.width * 3 / 4 - 100, self.app.height * 1/7, text="Instructions:", font="Helveltica 20 bold", anchor="w")
        canvas.create_text(self.app.width * 3 / 4 - 100, self.app.height * 1/7 + 50, text="Reach the exit the before the AI does!", font="Helveltica 15 bold", anchor="w")
        canvas.create_text(self.app.width * 3 / 4 - 100, self.app.height * 1/7 + 100, text="Use W, A, S, D to move", font="Helveltica 15 bold", anchor="w")
        canvas.create_text(self.app.width * 3 / 4 - 100, self.app.height * 1/7 + 150, text="Hints and solutions are disabled.", font="Helveltica 15 bold", anchor="w")
        canvas.create_text(self.app.width * 3 / 4 - 100, self.app.height * 1/7 + 210, text="Press 'p' to pause/unpause. Press 'r' to reset,\nor play again!", font="Helveltica 15 bold", anchor="w")
        self.aiExitButton.draw(canvas)
    
class Food(object):
    def __init__(self, app):
        self.app = app
        self.randRow = random.randint(0, self.app.rows - 1)
        self.randCol = random.randint(0, self.app.cols - 1)
        self.x, self.y, self.x1, self.y1, cw, ch = getCellBounds(self.app, self.randRow, self.randCol)
        self.lifeValue = random.randint(1, 3)
        self.timeCount = 0

    def moveFood(self):
        self.randRow = random.randint(0, self.app.rows - 1)
        self.randCol = random.randint(0, self.app.cols - 1)
        self.x, self.y, self.x1, self.y1, cw, ch = getCellBounds(self.app, self.randRow, self.randCol)
        self.lifeValue = random.randint(1, 2)
        self.timeCount = random.randint(3, 8)

    def getLocation(self):
        return self.randRow, self.randCol

    def draw(self, canvas):
        canvas.create_oval(self.x + 6, self.y + 6, self.x1 - 6, self.y1 - 6, fill="orange")
        canvas.create_text(self.x + (self.x1 - self.x) / 2, self.y + (self.y1 - self.y) / 2, text=self.lifeValue, font="Helveltica 10 bold")

#CITATION: Menu switching learned from https://www.cs.cmu.edu/~112/notes/notes-animations-part4.html
#Menu Screen
def menuMode_redrawAll(app, canvas):
    canvas.create_text(app.width / 2, app.height / 5, text="A-MAZE-ing", font="Helveltica 30 bold")
    app.menu.drawMainMenu(canvas)

def menuMode_mousePressed(app, event):
    if app.menu.normalButton.isClicked(event.x, event.y):
        app.mode = "selectMode"
    elif app.menu.aiButton.isClicked(event.x, event.y):
        app.mode = "aiMode"

def menuMode_keyPressed(app, event):
    if event.key == "1":
        app.mode = "selectMode"
    elif event.key == "2":
        app.mode = "aiMode"

#Level Selection Screen
def selectMode_redrawAll(app, canvas):
    canvas.create_text(app.width / 2, app.height / 5, text="Level selection", font="Helveltica 30 bold")
    app.menu.drawLevelSelect(canvas)

def selectMode_mousePressed(app, event):
    if app.menu.easyLevelButton.isClicked(event.x, event.y):
        resetApp(app, "easy", "normalMode")
        
    elif app.menu.normalLevelButton.isClicked(event.x, event.y):
        resetApp(app, "normal", "normalMode")
    elif app.menu.hardLevelButton.isClicked(event.x, event.y):
        resetApp(app, "hard", "normalMode")
    elif app.menu.backButton.isClicked(event.x, event.y):
        resetApp(app, "", "menuMode")
    

def selectMode_keyPressed(app, event):
    if event.key == "4":
        resetApp(app, "impossible", "normalMode")
        
#AI Mode
def aiMode_mousePressed(app, event):
    if app.menu.aiExitButton.isClicked(event.x, event.y):
        resetApp(app, "", "menuMode")

def aiMode_keyPressed(app, event):
    gridWidth  = app.width - 2 * app.margin - rightMargin
    gridHeight = app.height - 2 * app.margin
    cellWidth = gridWidth / app.cols
    cellHeight = gridHeight / app.rows
    if event.key == 'r':
        resetApp(app, "", app.mode) 
    elif app.gameOver:
        return
    elif app.visibleSolution:
        return
    elif event.key == 'p':
        app.paused = not app.paused
    elif event.key == "s":
        app.player.move(0, cellHeight)
        app.playerMoved = True
    elif event.key == "w":
        app.player.move(0, -cellHeight)
        app.playerMoved = True
    elif event.key == "a":
        app.player.move(-cellWidth, 0)
        app.playerMoved = True
    elif event.key == "d":
        app.player.move(cellWidth, 0)
        app.playerMoved = True

def aiMode_timerFired(app):
    if app.gameOver:
        return
    elif not app.paused and app.playerMoved:
        doStep(app)

def aiMode_redrawAll(app, canvas):
    drawAIGrid(app, canvas)
    app.player.draw(canvas)
    app.aiRacer.draw(canvas)
    app.menu.drawAiExit(canvas)

#App functions and Normal Mode
def appStarted(app):
    app.rows = 20
    app.cols = 20
    app.margin = 25
    app.menu = Menu(app)
    resetApp(app, "", "menuMode")

def resetApp(app, level, mode):
    app.mode = mode
    app.level = level
    app.countdown = 0
    app.food = Food(app)
    #Test maze size
    if app.level == "easy":
        app.rows = 10
        app.cols = 10
        app.countdown = 14

    elif app.level == "normal":
        app.rows = 20
        app.cols = 20
        app.countdown = 24

    elif app.level == "hard":
        app.rows = 40
        app.cols = 40
        app.countdown = 34

    elif app.level == "impossible":
        app.rows = 70
        app.cols = 70
        app.countdown = 60
        app.food = None
    if app.food != None:
        app.food.moveFood()
    app.timer = 0
    app.paused = False
    app.gameOver = False
    app.visibleSolution = False
    app.showHint = False
    app.hintCount = 3
    app.livesLeft = 3
    app.mazeInfo = []
    for r in range(app.rows + 1): 
        temp = []
        for c in range(app.cols + 1):
            temp.append(Cell(app, r, c))
        app.mazeInfo.append(temp)
    app.player = Player(app, app.mazeInfo)
    generateMaze(app)
    app.aiExit = app.mazeInfo[app.rows - 1][app.cols // 2]
    app.exit = app.mazeInfo[app.rows - 1][app.cols - 1]
    app.solutionPath = []
    app.enemyPath = []
    app.enemyTwoPath = []
    app.aiPath = []
    app.hintPath = []
    app.enemy = Enemy(app, app.mazeInfo)
    app.enemy.findPath()
    app.aiRacer = AIRacer(app, app.mazeInfo)
    app.aiRacer.findPath()
    app.playerMoved = False 

def normalMode_keyPressed(app, event):
    gridWidth  = app.width - 2 * app.margin - rightMargin
    gridHeight = app.height - 2 * app.margin
    cellWidth = gridWidth / app.cols
    cellHeight = gridHeight / app.rows
    if event.key == 'r':
        resetApp(app, app.level, app.mode)
        if app.level == "easy":
            app.countdown = 14
        elif app.level == "normal":
            app.countdown = 24
        elif app.level == "hard":
            app.countdown = 44
    elif app.gameOver:
        return
    elif app.visibleSolution:
        return
    elif event.key == 'p':
        app.paused = not app.paused
    elif event.key == 'z':
        app.visibleSolution = not app.visibleSolution
        if not app.visibleSolution:
            app.solutionPath = []
            return
        pRow, pCol = app.player.getCurrentPosition()
        cell = app.mazeInfo[pRow][pCol]
        autoSolver(app, cell, app.exit, app.solutionPath)
    elif event.key == 'h':
        if app.hintCount <= 0:
            return
        app.showHint = True
        if app.showHint:
            app.hintCount -= 1
            pRow, pCol = app.player.getCurrentPosition()
            cell = app.mazeInfo[pRow][pCol]
            autoSolver(app, cell, app.exit, app.solutionPath)
    elif event.key == "s":
        app.player.move(0, cellHeight)
    elif event.key == "w":
        app.player.move(0, -cellHeight)
    elif event.key == "a":
        app.player.move(-cellWidth, 0)
    elif event.key == "d":
        app.player.move(cellWidth, 0)

#Gets a new exit
def findNewExit(app):
    row = 0
    col = 0
    pRow, pCol = app.player.getCurrentPosition()
    directions = ["n", "e", "w", "s"]
    side = random.choice(directions)
    if side == "n":
        row = 0
        col = random.randint(0, app.cols - 1)
    elif side == "e":
        row = random.randint(0, app.rows - 1)
        col = app.cols - 1
    elif side == "w":
        row = random.randint(0, app.rows - 1)
        col = 0
    elif side == "s":
        row = app.rows - 1
        col = random.randint(0, app.cols - 1)
    if app.mazeInfo[row][col] == app.mazeInfo[pRow][pCol]:
        return findNewExit(app)
    else:
        return app.mazeInfo[row][col]

#Checks if neighbors are connected (i.e no wall between them)
def isConnectedNeighbor(fromCell, toCell):
    fromRow, fromCol = fromCell.getLocation()
    toRow, toCol = toCell.getLocation()
    if fromRow == toRow:
        if fromCol > toCol:
            return not fromCell.w
        else:
            return not fromCell.e
    elif fromCol == toCol:
        if fromRow > toRow:
            return not fromCell.n
        else:
            return not fromCell.s
    return False

#CITATION: autoSolver is created using recursive backtracking, researched from https://www.geeksforgeeks.org/backtracking-introduction/
def autoSolver(app, cell, endCell, path):
    visited = set()
    findPath(app, cell, endCell, path, visited)

#finds the solution path
def findPath(app, cell, endCell, path, visited):
    if cell == endCell:
        path.append(cell)
        return True
    n, s, w, e = getNeighbors(app, cell)
    neighborList = [n, s, w, e]
    visited.add(cell)
    for i in range(len(neighborList)):
        if neighborList[i] != None:
            if neighborList[i] in visited:
                continue
            if isConnectedNeighbor(cell, neighborList[i]):
                foundExit = findPath(app, neighborList[i], endCell, path, visited)
                if foundExit:
                    path.append(cell)
                    return True
    return False

#adds neighbors into the neighbor list
def addNeighbors(app, cell, inList, visited, neighborList):
    northCell, southCell, westCell, eastCell = getNeighbors(app, cell)
    if northCell != None and northCell not in inList and northCell not in visited:
        neighborList.append(northCell)
        inList.add(northCell)
    if southCell != None and southCell not in inList and southCell not in visited:
        neighborList.append(southCell)
        inList.add(southCell)
    if westCell != None and westCell not in inList and westCell not in visited:
        neighborList.append(westCell)
        inList.add(westCell)
    if eastCell != None and eastCell not in inList and eastCell not in visited:
        neighborList.append(eastCell)
        inList.add(eastCell)

#gets all available neighbors to a cell
def getNeighbors(app, cell):
    row = cell.row
    col = cell.col
    northCell = None
    southCell = None
    westCell = None
    eastCell = None
    if row - 1 >= 0:
        northCell = app.mazeInfo[row - 1][col]
    if row + 1 < app.rows:
        southCell = app.mazeInfo[row + 1][col]
    if col - 1 >= 0:
        westCell = app.mazeInfo[row][col - 1]
    if col + 1 < app.cols:
        eastCell = app.mazeInfo[row][col + 1]
    return northCell, southCell, westCell, eastCell

#Takes down wall between cells
def knockWall(app, cell, visited):
    dirList = []
    n, s, w, e = getNeighbors(app, cell)
    if n != None and n in visited:
        dirList.append(n)
    if s != None and s in visited:
        dirList.append(s)
    if e != None and e in visited:
        dirList.append(e)
    if w != None and w in visited:
        dirList.append(w)
    if dirList != []:
        dirKnock = random.choice(dirList)
        if dirKnock == n:
            cell.changeWallStatus(dirKnock, "n")
        elif dirKnock == s:
            cell.changeWallStatus(dirKnock, "s")
        elif dirKnock == w:
            cell.changeWallStatus(dirKnock, "w")
        elif dirKnock == e:
            cell.changeWallStatus(dirKnock, "e")

#CITATION: generateMaze is based on randomized Prim's algorithm, mainly researched from https://en.wikipedia.org/wiki/Maze_generation_algorithm
def generateMaze(app):
    visited = set()
    inList = set()
    neighbors = []
    startRow = random.randint(0, app.rows - 1)
    startCol = random.randint(0, app.cols - 1)
    neighbors.append(app.mazeInfo[startRow][startCol])
    inList.add(app.mazeInfo[startRow][startCol])
    while neighbors != []:
        cell = random.choice(neighbors)
        neighbors.remove(cell)
        inList.remove(cell)
        knockWall(app, cell, visited)
        visited.add(cell)
        addNeighbors(app, cell, inList, visited, neighbors)

def normalMode_mousePressed(app, event):
    if app.menu.normalExitButton.isClicked(event.x, event.y):
        resetApp(app, "normal", "selectMode")

def normalMode_timerFired(app):
    if app.gameOver:
        return
    elif app.visibleSolution:
        return
    elif not app.paused:
        doStep(app)

def doStep(app):
    assert(app.countdown >= 0)
    app.timer += app.timerDelay
    if app.mode == "normalMode":
        if app.timer % 1000 == 0:
            app.countdown -= 1
            if app.food != None:
                app.food.timeCount -= 1
                if app.food.timeCount == 0:
                    app.food.moveFood()
        if app.timer % 2500 == 0:
            app.enemy.findPath()

        if app.level == "easy":
            if app.timer % 15000 == 0:
                app.exit = findNewExit(app)
                app.countdown = 14
            if app.timer % 500 == 0:
                app.enemy.updatePosition()

        elif app.level == "normal":
            if app.timer % 25000 == 0:
                app.exit = findNewExit(app)
                app.countdown = 24
            if app.timer % 300 == 0:
                app.enemy.updatePosition()

        elif app.level == "hard":
            if app.timer % 35000 == 0:
                app.exit = findNewExit(app)
                app.countdown = 34
            if app.timer % 100 == 0:
                app.enemy.updatePosition()
                
        elif app.level == "impossible":
            if app.timer % 60000 == 0:
                app.exit = findNewExit(app)
                app.countdown = 59
            app.enemy.updatePosition()

        if app.timer % 2000 == 0 and app.showHint:
            app.showHint = False
            app.solutionPath = []

    elif app.mode == "aiMode":
        if app.timer % 200 == 0:
            app.aiRacer.updatePosition()
        app.showHint = False
       

#CITATION: code from https://www.cs.cmu.edu/~112/notes/notes-animations-part2.html
def getCell(app, x, y):
    gridWidth  = app.width - 2 * app.margin - rightMargin
    gridHeight = app.height - 2 * app.margin
    cellWidth = gridWidth / app.cols
    cellHeight = gridHeight / app.rows
    row = int((y - app.margin) / cellHeight)
    col = int((x - app.margin) / cellWidth)
    return row, col

#CITATION: template from https://www.cs.cmu.edu/~112/notes/notes-animations-part2.html (modified)
def getCellBounds(app, row, col):
    gridWidth  = app.width - 2 * app.margin - rightMargin
    gridHeight = app.height - 2 * app.margin
    cellWidth = gridWidth / app.cols
    cellHeight = gridHeight / app.rows
    x0 = app.margin + col * cellWidth
    y0 = app.margin + row * cellHeight
    x1 = x0 + cellWidth
    y1 = y0 + cellHeight
    return x0, y0, x1, y1, cellWidth, cellHeight

#Normal draw function
def drawNormalGrid(app, canvas):
    for r in range(len(app.mazeInfo) - 1):
        for c in range(len(app.mazeInfo[r]) - 1):
            x0, y0, x1, y1, cellW, cellH = getCellBounds(app, r, c)
            n, e, s, w = app.mazeInfo[r][c].getWallStatus()
            if n:
                canvas.create_line(x0, y0, x1, y0)
            if e:
                canvas.create_line(x1, y0, x1, y1)
            if s:
                canvas.create_line(x0, y1, x1, y1)
            if w:
                canvas.create_line(x0, y0, x0, y1)
    if app.showHint:
        for i in range(4):
            hintPath = copy.copy(app.solutionPath)
            hintPath = hintPath[::-1]
            r, c = hintPath[i].getLocation()
            x0, y0, x1, y1, cw, ch = getCellBounds(app, r, c)
            canvas.create_oval(x0 + 3, y0 + 3, x1 - 3, y1 - 3, fill="red", outline="")
    else:
        for i in range(len(app.solutionPath)):
            r, c = app.solutionPath[i].getLocation()
            x0, y0, x1, y1, cw, ch = getCellBounds(app, r, c)
            canvas.create_oval(x0 + 3, y0 + 3, x1 - 3, y1 - 3, fill="red", outline="")
    ex, ey = app.exit.getLocation()
    x0, y0, x1, y1, cw, ch = getCellBounds(app, ex, ey)
    canvas.create_rectangle(x0 + 2, y0 + 2, x1 - 2, y1 - 2, fill="green", outline="")
    canvas.create_text(app.width - rightMargin - app.margin, app.margin - 10, text=f"Time until exit change: {app.countdown}s", anchor="e", font="Helveltica 12 bold")
    canvas.create_text(app.margin - 20, app.height - 10, text=f"Hints left: {app.hintCount}", anchor="w", font="Helveltica 12 bold")
    canvas.create_text(app.width - rightMargin - app.margin, app.height - 10, text=f"Lives left: {app.livesLeft}", anchor="e", font="Helveltica 12 bold")
    if app.gameOver:
        canvas.create_text((app.width - rightMargin) / 2, app.margin - 20, text="Game Over!", anchor="n", font="Helveltica 12 bold")
    if app.visibleSolution:
        canvas.create_text((app.width - rightMargin) / 2, app.margin - 20, text="Solution used, game over", anchor="n", font="Helveltica 12 bold")

#AI draw function
def drawAIGrid(app, canvas):
    for r in range(len(app.mazeInfo) - 1):
        for c in range(len(app.mazeInfo[r]) - 1):
            x0, y0, x1, y1, cellW, cellH = getCellBounds(app, r, c)
            n, e, s, w = app.mazeInfo[r][c].getWallStatus()
            if n:
                canvas.create_line(x0, y0, x1, y0)
            if e:
                canvas.create_line(x1, y0, x1, y1)
            if s:
                canvas.create_line(x0, y1, x1, y1)
            if w:
                canvas.create_line(x0, y0, x0, y1)
    if app.showHint:
        for i in range(4):
            hintPath = copy.copy(app.solutionPath)
            hintPath = hintPath[::-1]
            r, c = hintPath[i].getLocation()
            x0, y0, x1, y1, cw, ch = getCellBounds(app, r, c)
            canvas.create_oval(x0 + 3, y0 + 3, x1 - 3, y1 - 3, fill="red", outline="")
    else:
        for i in range(len(app.solutionPath)):
            r, c = app.solutionPath[i].getLocation()
            x0, y0, x1, y1, cw, ch = getCellBounds(app, r, c)
            canvas.create_oval(x0 + 3, y0 + 3, x1 - 3, y1 - 3, fill="red", outline="")
    ex, ey = app.aiExit.getLocation()
    x0, y0, x1, y1, cw, ch = getCellBounds(app, ex, ey)
    canvas.create_rectangle(x0 + 2, y0 + 2, x1 - 2, y1 - 2, fill="green", outline="")
    if app.gameOver:
        canvas.create_text((app.width - rightMargin) / 2, app.margin - 20, text="Game Over!", anchor="n", font="Helveltica 12 bold")
    if app.visibleSolution:
        canvas.create_text(app.width / 2, app.margin - 20, text="Solution used, game over", anchor="n", font="Helveltica 12 bold")

def normalMode_redrawAll(app, canvas):
    drawNormalGrid(app, canvas)
    app.player.draw(canvas)
    app.enemy.draw(canvas)
    app.menu.drawExit(canvas)
    if app.food != None:
        app.food.draw(canvas)

runApp(width=(1000 + rightMargin), height=1000)