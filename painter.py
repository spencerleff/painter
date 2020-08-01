#!/usr/bin/env python3

import curses
import curses.panel
from curses.textpad import Textbox, rectangle
import sys
import os
from os import path
import locale

##### WINDOW FUNCTION #####
def window(stdscr, fileExists, dungeonFile):
  fileLengthTest = True
  curses.curs_set(0) 
  curses.cbreak()
  
  (totalScreenHeight, totalScreenWidth) = stdscr.getmaxyx()
  totalScreenHeight -= 3
  screenHeight = totalScreenHeight - 2
  screenWidth = totalScreenWidth - 4

  newFileWidth = int(float(screenWidth) / 2) + 1

  #if file doesn't exist, set the h/w to the size of the terminal
  if fileExists == False:
      f = open(dungeonFile, "w+")
      for y in range(screenHeight):
          if y != 0:
              f.write("\n")
          for x in range(newFileWidth):
              f.write("#")
      f.close()

  #final err check and set size of painter screen
  else:
    with open(dungeonFile, 'r') as f:
        numLines = 0
        numChars = 0
        for lines in f:
            numLines += 1
            if numLines == 1:
                line = str(lines)
                for i in line:
                    numChars += 1
        if (numLines > screenHeight) or (numChars > screenWidth):
            fileLengthTest = False
            curses.endwin() 
            return fileLengthTest

        else:
            totalScreenHeight = numLines + 2
            totalScreenWidth = (numChars) * 2
            screenHeight = totalScreenHeight - 2
            screenWidth = totalScreenWidth - 4

  ######################################################################################
  ##### SAVE FILE TO MATRIX #####
  ######################################################################################
  fileMatrix = []
  numRows = 0
  numCols = 0
  with open(dungeonFile, 'r') as f:
      for line in f:
          numRows += 1
          col = str(line)
          numCols = len(col)
          rowArray = []
          for i in col:
              rowArray.append(i)
          fileMatrix.append(rowArray)
  
  #remove the temp file if one was used
  if fileExists == False:
      os.remove(dungeonFile)

  #color pair
  curses.init_pair(1, curses.COLOR_RED, curses.COLOR_WHITE)
  colorCount = 2
  curses.init_pair(2, curses.COLOR_BLUE, curses.COLOR_BLACK)
  curses.init_pair(3, curses.COLOR_WHITE, curses.COLOR_BLUE)
  curses.init_pair(4, curses.COLOR_WHITE, curses.COLOR_BLUE)
  curses.init_pair(5, curses.COLOR_WHITE, curses.COLOR_BLUE)
  
  #text items
  textCount = 0
  currentCursor = []
  currentCursor.append(curses.ACS_CKBOARD)
  currentCursor.append('[]')
  currentCursor.append('/]')
  currentCursor.append('\]')

  ######################################################################################
  ##### Windows and window settings #####
  ######################################################################################
  myWindow=curses.newwin(totalScreenHeight, totalScreenWidth, 0, 0)
  myWindow.box(0,0)
  #add the file to the window
  fileY = 0
  fileX = 0
  for r in range(numRows):
      fileY += 1
      for c in range(numCols):
          fileX += 1
          char = fileMatrix[r][c]
          if char == '#':
              myWindow.addch(fileY,fileX,currentCursor[0],curses.color_pair(2))
              myWindow.addch(fileY,fileX + 1,currentCursor[0],curses.color_pair(2))
          if char == '.':
              myWindow.addstr(fileY,fileX,currentCursor[1],curses.color_pair(3))
          if char == '/':
              myWindow.addstr(fileY,fileX,currentCursor[2],curses.color_pair(4))
          if char == '\\': 
              myWindow.addstr(fileY,fileX,currentCursor[3],curses.color_pair(5))
          fileX += 1
      fileX = 0
  myWindow.addch(1,1,currentCursor[0],curses.color_pair(1))
  myWindow.addch(1,2,currentCursor[0],curses.color_pair(1))
  myPanel=curses.panel.new_panel(myWindow)

  #info window
  infoWindow=curses.newwin(3, totalScreenWidth, totalScreenHeight, 0)
  infoWindow.box(0,0)
  cursorY = 1
  cursorX = 1
  infoWindow.addstr(1,1,"(%2d,%3d)" % (cursorY - 1,cursorX - 1))
  infoWindow.addstr(1,10,"Current:")
  infoWindow.addch(1,18,currentCursor[textCount],curses.color_pair(colorCount))
  infoWindow.addch(1,19,currentCursor[textCount],curses.color_pair(colorCount))
  infoPanel=curses.panel.new_panel(infoWindow)

  #update the curses window
  curses.panel.update_panels()
  curses.doupdate()
 
  
  ###########################################################################################
  ##### KEY INPUT #####
  ###########################################################################################
  key=''
  savePanelActive = False
  currentBrush = ''
  currentBrushColor = ''
  replaceCursorTxt = ''
  replaceCursor = ''
  replaceColor = ''
  isChar = False
  xCoordinate = 0
  yCoordinate = 0
  while key != ord('Q'):
      key = stdscr.getch()
      
      #Prevents the cursor from overwriting the text
      replaceCursorTxt = str(fileMatrix[yCoordinate][xCoordinate])
      if replaceCursorTxt == '#':
          replaceCursor = currentCursor[0]
          replaceColor = curses.color_pair(2)
          isChar = True
      elif replaceCursorTxt == '.':
          replaceCursor = currentCursor[1]
          replaceColor = curses.color_pair(3)
          isChar = False
      elif replaceCursorTxt == '/':
          replaceCursor = currentCursor[2]
          replaceColor = curses.color_pair(4)
          isChar = False
      elif replaceCursorTxt == '\\':
          replaceCursor = currentCursor[3]
          replaceColor = curses.color_pair(4)
          isChar = False

      #CHANGE CURRENT CURSOR ON INFO WINDOW
      if key == ord(' ') and savePanelActive == False:
          colorCount += 1
          if colorCount == 6:
              colorCount = 2
          textCount += 1
          if textCount == len(currentCursor):
              textCount = 0
          if textCount == 0:
              infoWindow.addch(1,18,currentCursor[textCount],curses.color_pair(colorCount))
              infoWindow.addch(1,19,currentCursor[textCount],curses.color_pair(colorCount))
          else:
              infoWindow.addstr(1,18,currentCursor[textCount],curses.color_pair(colorCount))
          currentBrush = textCount
          currentBrushColor = colorCount
          infoWindow.refresh()
      
      #####################################################################################
      ##### Cursor Movement #####
      #####################################################################################
      #up
      if key == ord('k') and savePanelActive == False:
          if cursorY > 1:
              myWindow.addch(cursorY - 1,cursorX,currentCursor[0],curses.color_pair(1))
              myWindow.addch(cursorY - 1,cursorX + 1,currentCursor[0],curses.color_pair(1))
              if isChar == True:
                  myWindow.addch(cursorY,cursorX,replaceCursor,replaceColor)
                  myWindow.addch(cursorY,cursorX + 1,replaceCursor,replaceColor)
              else:
                  myWindow.addstr(cursorY,cursorX,replaceCursor,replaceColor)
              cursorY -= 1
              yCoordinate -= 1
              myWindow.refresh()
              infoWindow.addstr(1,1,"(%2d,%3d)" % (yCoordinate,xCoordinate))
              infoWindow.refresh()
      #down
      if key == ord('j') and savePanelActive == False:
          if cursorY < screenHeight:
              myWindow.addch(cursorY + 1,cursorX,currentCursor[0],curses.color_pair(1))
              myWindow.addch(cursorY + 1,cursorX + 1,currentCursor[0],curses.color_pair(1))
              if isChar == True:
                  myWindow.addch(cursorY,cursorX,replaceCursor,replaceColor)
                  myWindow.addch(cursorY,cursorX + 1,replaceCursor,replaceColor)
              else:
                  myWindow.addstr(cursorY,cursorX,replaceCursor,replaceColor)
              cursorY += 1
              yCoordinate += 1
              myWindow.refresh()
              infoWindow.addstr(1,1,"(%2d,%3d)" % (yCoordinate,xCoordinate))
              infoWindow.refresh()

      #left
      if key == ord('h') and savePanelActive == False:
          if cursorX > 1:
              myWindow.addch(cursorY,cursorX - 1,currentCursor[0],curses.color_pair(1))
              myWindow.addch(cursorY,cursorX - 2,currentCursor[0],curses.color_pair(1))
              if isChar == True:
                  myWindow.addch(cursorY,cursorX,replaceCursor,replaceColor)
                  myWindow.addch(cursorY,cursorX + 1,replaceCursor,replaceColor)
              else:
                  myWindow.addstr(cursorY,cursorX,replaceCursor,replaceColor)
              cursorX -= 2
              xCoordinate -= 1
              myWindow.refresh()
              infoWindow.addstr(1,1,"(%2d,%3d)" % (yCoordinate,xCoordinate))
              infoWindow.refresh()
      #right
      if key == ord('l') and savePanelActive == False:
          if cursorX < screenWidth:
              myWindow.addch(cursorY,cursorX + 2,currentCursor[0],curses.color_pair(1))
              myWindow.addch(cursorY,cursorX + 3,currentCursor[0],curses.color_pair(1))
              if isChar == True:
                  myWindow.addch(cursorY,cursorX,replaceCursor,replaceColor)
                  myWindow.addch(cursorY,cursorX + 1,replaceCursor,replaceColor)
              else:
                  myWindow.addstr(cursorY,cursorX,replaceCursor,replaceColor)
              cursorX += 2
              xCoordinate += 1
              myWindow.refresh()
              infoWindow.addstr(1,1,"(%2d,%3d)" % (yCoordinate,xCoordinate))
              infoWindow.refresh()
     
      ######################################################################################
      ##### BRUSH TOOL #####
      ######################################################################################
      #brush up
      if key == ord('K'):
          if savePanelActive == False:
              if cursorY > 1:
                  if textCount == 0:
                      myWindow.addch(cursorY,cursorX,currentCursor[textCount],curses.color_pair(colorCount))
                      myWindow.addch(cursorY,cursorX + 1,currentCursor[textCount],curses.color_pair(colorCount))
                  else:
                      myWindow.addstr(cursorY,cursorX,currentCursor[textCount],curses.color_pair(colorCount))
                  
                  #add new brush stroke to fileMatrix
                  if textCount == 0:
                      fileMatrix[yCoordinate][xCoordinate] = '#'
                  elif textCount == 1:
                      fileMatrix[yCoordinate][xCoordinate] = '.'
                  elif textCount == 2:
                      fileMatrix[yCoordinate][xCoordinate] = '/'
                  elif textCount == 3:
                      fileMatrix[yCoordinate][xCoordinate] = '\\'
                  
                  #move the cursor up
                  myWindow.addch(cursorY - 1,cursorX,currentCursor[0],curses.color_pair(1))
                  myWindow.addch(cursorY - 1,cursorX + 1,currentCursor[0],curses.color_pair(1))
                  cursorY -= 1
                  yCoordinate -= 1
                  myWindow.refresh()
                  infoWindow.addstr(1,1,"(%2d,%3d)" % (yCoordinate,xCoordinate))
                  infoWindow.refresh()

      #brush down
      if key == ord('J'):
          if savePanelActive == False:
              if cursorY < screenHeight:
                  if textCount == 0:
                      myWindow.addch(cursorY,cursorX,currentCursor[textCount],curses.color_pair(colorCount))
                      myWindow.addch(cursorY,cursorX + 1,currentCursor[textCount],curses.color_pair(colorCount))
                  else:
                      myWindow.addstr(cursorY,cursorX,currentCursor[textCount],curses.color_pair(colorCount))

                  #add new brush stroke to fileMatrix
                  if textCount == 0:
                      fileMatrix[yCoordinate][xCoordinate] = '#'
                  elif textCount == 1:
                      fileMatrix[yCoordinate][xCoordinate] = '.'
                  elif textCount == 2:
                      fileMatrix[yCoordinate][xCoordinate] = '/'
                  elif textCount == 3:
                      fileMatrix[yCoordinate][xCoordinate] = '\\'

                  #move the cursor down
                  myWindow.addch(cursorY + 1,cursorX,currentCursor[0],curses.color_pair(1))
                  myWindow.addch(cursorY + 1,cursorX + 1,currentCursor[0],curses.color_pair(1))
                  cursorY += 1
                  yCoordinate += 1
                  myWindow.refresh()
                  infoWindow.addstr(1,1,"(%2d,%3d)" % (yCoordinate,xCoordinate))
                  infoWindow.refresh()

      #brush left
      if key == ord('H'):
          if savePanelActive == False:
              if cursorX > 1:
                  if textCount == 0:
                      myWindow.addch(cursorY,cursorX,currentCursor[textCount],curses.color_pair(colorCount))
                      myWindow.addch(cursorY,cursorX + 1,currentCursor[textCount],curses.color_pair(colorCount))
                  else:
                      myWindow.addstr(cursorY,cursorX,currentCursor[textCount],curses.color_pair(colorCount))

                  #add new brush stroke to fileMatrix
                  if textCount == 0:
                      fileMatrix[yCoordinate][xCoordinate] = '#'
                  elif textCount == 1:
                      fileMatrix[yCoordinate][xCoordinate] = '.'
                  elif textCount == 2:
                      fileMatrix[yCoordinate][xCoordinate] = '/'
                  elif textCount == 3:
                      fileMatrix[yCoordinate][xCoordinate] = '\\'
                  
                  #move the cursor left
                  myWindow.addch(cursorY,cursorX - 1,currentCursor[0],curses.color_pair(1))
                  myWindow.addch(cursorY,cursorX - 2,currentCursor[0],curses.color_pair(1))
                  cursorX -= 2
                  xCoordinate -= 1
                  myWindow.refresh()
                  infoWindow.addstr(1,1,"(%2d,%3d)" % (yCoordinate,xCoordinate))
                  infoWindow.refresh()
                  
      #brush right
      if key == ord('L'):
          if savePanelActive == False:
              if cursorX < screenWidth:
                  if textCount == 0:
                      myWindow.addch(cursorY,cursorX,currentCursor[textCount],curses.color_pair(colorCount))
                      myWindow.addch(cursorY,cursorX + 1,currentCursor[textCount],curses.color_pair(colorCount))
                  else:
                      myWindow.addstr(cursorY,cursorX,currentCursor[textCount],curses.color_pair(colorCount))
              
                  #add new brush stroke to fileMatrix
                  if textCount == 0:
                      fileMatrix[yCoordinate][xCoordinate] = '#'
                  elif textCount == 1:
                      fileMatrix[yCoordinate][xCoordinate] = '.'
                  elif textCount == 2:
                      fileMatrix[yCoordinate][xCoordinate] = '/'
                  elif textCount == 3:
                      fileMatrix[yCoordinate][xCoordinate] = '\\'

                  #move the cursor right
                  myWindow.addch(cursorY,cursorX + 2,currentCursor[0],curses.color_pair(1))
                  myWindow.addch(cursorY,cursorX + 3,currentCursor[0],curses.color_pair(1))
                  cursorX += 2
                  xCoordinate += 1
                  myWindow.refresh()
                  infoWindow.addstr(1,1,"(%2d,%3d)" % (yCoordinate,xCoordinate))
                  infoWindow.refresh()
      
      
      ###############################################################
      ##### SAVE WINDOW #####
      ###############################################################
      if key == ord('w') or key == ord('s'):
          if savePanelActive == False:
              savePanelActive = True

              saveWindowWidth = len(dungeonFile) + 8
              (yMax,xMax)=myWindow.getmaxyx()
              if xMax < saveWindowWidth:
                  saveWindowWidth = xmax - 2

              saveWindow = curses.newwin(3,saveWindowWidth,yMax//2-2, xMax//2-(saveWindowWidth//2+1))
              subWindow = curses.newwin(1,saveWindowWidth - 2,yMax//2-1,xMax//2-(saveWindowWidth//2))
              saveWindow.immedok(True)
              subWindow.immedok(True)
              saveWindow.box()
              
              saveWindow.addstr(0,saveWindowWidth//3,"Save")
              subWindow.addstr(dungeonFile)
              winInput = Textbox(subWindow)
              subWindow.move(0,len(dungeonFile))
              curses.curs_set(1)
              dungeonFile = winInput.edit().strip()
              curses.curs_set(0)

              saveWindow=None
              subWindow=None
              winInput=None
              
              #Redraw the window so that the empty space where the saveWindow was will be filled
              outputY = 0
              outputX = 0
              for r in range(numRows):
                  outputY += 1
                  for c in range(numCols):
                      outputX += 1
                      char = fileMatrix[r][c]
                      if char == '#':
                          myWindow.addch(outputY,outputX,currentCursor[0],curses.color_pair(2))
                          myWindow.addch(outputY,outputX + 1,currentCursor[0],curses.color_pair(2))
                      if char == '.':
                          myWindow.addstr(outputY,outputX,currentCursor[1],curses.color_pair(3))
                      if char == '/':
                          myWindow.addstr(outputY,outputX,currentCursor[2],curses.color_pair(4))
                      if char == '\\': 
                          myWindow.addstr(outputY,outputX,currentCursor[3],curses.color_pair(5))
                      outputX += 1
                  outputX = 0
              
              #Redraw the cursor
              myWindow.addch(cursorY,cursorX,currentCursor[0],curses.color_pair(1))
              myWindow.addch(cursorY,cursorX + 1,currentCursor[0],curses.color_pair(1))
              
              savePanelActive = False
              myWindow.refresh()
              stdscr.refresh()

              #write the matrix to the file
              if fileExists == False:
                  with open(dungeonFile, 'w+') as fp:
                      for y in range(numRows):
                          for x in range(numCols):
                              fp.write(str(fileMatrix[y][x]))
                          fp.write("\n")

              elif fileExists == True:
                  with open(dungeonFile, 'w+') as fp:
                      for y in range(numRows):
                          for x in range(numCols):
                              fp.write(str(fileMatrix[y][x]))


      if key == '^?':
          delch()
          delch()

      #refresh the standard screen after each key press
      stdscr.refresh()

##### END WINDOW FUNCTION #####


################################################################################################
##### ERROR CHECKS #####
################################################################################################
if len(sys.argv) < 2 or len(sys.argv) > 2:
    print("Usage: ./painter.py dungeonfile.txt")
    sys.exit(1)

#file doesnt exist
dungeonFile = sys.argv[1]
if not path.exists(dungeonFile):
    fileExists = False
    with open(dungeonFile, 'x') as f:
        f.close()

#else validate the file
else:
    fileExists = True
    allowedChars = '#.\/'
    with open(dungeonFile, 'r') as fp:
        for firstLine in fp:
            startingWidth = len(firstLine)
            break
        fp.close()
    with open(dungeonFile, 'r') as f:
        lineCounter = 0
        for lines in f:
            #Test if the lines are all the same length
            lineCounter += 1
            colCounter = 0
            for i in lines:
                colCounter += 1
            #print("colCounter: " + str(colCounter))
            #print("startingWidth: " + str(startingWidth))
            if (colCounter) != int(startingWidth):
                print("File read-in error: The lines in the file are not the same length.")
                sys.exit(1)
            lineCounter += 1
            #Test if the file has only allowed characters
            testLine = str(lines)
            for i in range(len(testLine) - 1):
                if testLine[i] not in allowedChars:
                    print("File read-in error: Invalid character found (" + str(lines[i]) + ")")
                    sys.exit(1)
        f.close()

#run the window function
fileLengthTest = curses.wrapper(window, fileExists, dungeonFile)

#third file read-in error (can't be rendered in terminal window)
if fileLengthTest == False:
    print("File read-in error: The file is too large to be fully rendered in the terminal window")
    sys.exit(1)

##### END OF PROGRAM #####
