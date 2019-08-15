import kivy
import kivy.uix.button as kb
from math import cos, sin
from kivy.app import App
from kivy.uix.widget import Widget
from kivy.core.window import Window

class Muscle(Widget):
    pass

class MotorUnit(Widget):
    pass

class Fibre(Widget):
    pass

class Needle(Widget):
    pass

class ZoomBox(Widget):
    pass

class Simulator(Widget):
    # constructor for the Simulator class
    def __init__(self, **kwargs):
        super(Simulator, self).__init__(**kwargs)
        self.xScale = 50
        self.yScale = 50
        self.sizeScale = 50
        self.lastShown = "single"
        self.childDictionary = {}
        self.zoomScale = []
        self.zoomCoord = []
        self.allowZoom = True
        self.zoomBox = ZoomBox()

        # buttons for zoom functionality
        self.zoomButton = kb.Button(text = "-")
        self.zoomButton.bind(on_press = self.zoomOut)
        self.homeButton = kb.Button(text = "Home")
        self.homeButton.bind(on_press = self.returnHome)
    '''
    def on_touch_down(self, touch):
        print("(" + str( (touch.pos[0]*self.xScale) + Window.width/2 ) + ", " + str( (touch.pos[1]*self.yScale) + Window.height/2 ))
    '''    

    def on_touch_down(self, touch):
        self.zoomCoord1 = touch.pos

        #create a zoom indicator
        self.zoomBox.pos = touch.pos
        self.zoomBox.size = (1,1)
        if not self.zoomBox.parent:
            self.add_widget(self.zoomBox)

        return super(Simulator, self).on_touch_down(touch)

    # draw the zoombox
    def on_touch_move(self, touch):
        x1 = self.zoomCoord1[0]
        y1 = self.zoomCoord1[1]
        x2 = touch.pos[0]
        y2 = touch.pos[1]

        self.zoomBox.size = (abs(x1 - x2), abs(y1 - y2))
        
        # quadrant I automatic

        # quadrant II
        if (x1 > x2) and (y1 < y2):
            self.zoomBox.pos = (x2,y1)

        # quadrant III
        elif (x1 > x2) and (y1 > y2):
            self.zoomBox.pos = touch.pos

        # quadrant IV
        elif (x1 < x2) and (y1 > y2):
            self.zoomBox.pos = (x1,y2)

    def on_touch_up(self, touch):
        self.remove_widget(self.zoomBox)
        if self.allowZoom == False:
            return

        self.zoomCoord2 = touch.pos

        # get x and y coordinates
        x1 = self.zoomCoord1[0]
        y1 = self.zoomCoord1[1]
        x2 = self.zoomCoord2[0]
        y2 = self.zoomCoord2[1]

        # change coordinates so that it is as if user dragged from top left to bottom right
        # user selected from top right to bottom left
        if (x1 > x2) and (y1 > y2):
            # swap x values
            temp = x1
            x1 = x2
            x2 = temp

        # user selected from bottom left to top right
        elif (x1 < x2) and (y1 < y2):
            # swap y values
            temp = y1
            y1 = y2
            y2 = temp

        # user selected from bottom right to top left
        elif (x1 > x2) and (y1 < y2):
            # swap coordinates
            temp = x1
            x1 = x2
            x2 = temp

            temp = y1
            y1 = y2
            y2 = temp

        # get the length and width of the selected area
        xLen = abs(x1 - x2)
        yLen = abs(y1 - y2)

        # if the selected area is too small consider it as if the user did not intend to zoom in
        if (xLen <= 15) and (yLen <= 15):
            scaleFactor = 1
            return
        # if selected area is wider than it is tall, fit all of the width onto screen with extra height
        elif (xLen > yLen):
            scaleFactor = 800 / xLen
            xZoom = x1 * scaleFactor
            yZoom = (y1 * scaleFactor) - ((Window.height / 3) * 2)
        # if selected area is taller than it is wide, fit all of the height onto the screen with extra width
        elif (yLen > xLen):
            scaleFactor = 600 / yLen
            xZoom = (x2 * scaleFactor) - ((Window.width / 3) * 2)
            yZoom = y2 * scaleFactor  

        # push onto stack so user can zoom out step-by-step
        self.zoomScale.append(scaleFactor)
        self.zoomCoord.append((xZoom, yZoom))

        for child in self.children:
            # increase the size of all widgets on the canvas
            child.size = tuple(scaleFactor * i for i in child.size)
            child.pos = tuple(scaleFactor * i for i in child.pos)

            # translate everything so that the selected zoom area is visible on the screen
            child.pos = (child.pos[0] - xZoom, child.pos[1] - yZoom)

            # increase the size of the child's children if it has any
            if child.children:
                for grandchild in child.children:
                    grandchild.size = tuple(scaleFactor * i for i in grandchild.size)
                    grandchild.pos = tuple(scaleFactor * i for i in grandchild.pos)
                    grandchild.pos = (grandchild.pos[0] - xZoom, grandchild.pos[1] - yZoom)

        # create a button to allow user to zoom out
        self.zoomButton.size = (25,25)
        self.zoomButton.pos = (710,20)

        # create a button to allow user to get back to default view
        self.homeButton.size = (50,25)
        self.homeButton.pos = (740,20)

        # add the zoom buttons to the canvas if they're not there
        if not self.zoomButton.parent:
            self.add_widget(self.zoomButton)
        if not self.homeButton.parent:
            self.add_widget(self.homeButton)

        return super(Simulator, self).on_touch_up(touch)

    def returnHome(self, instance):
        while (self.zoomScale):
            self.zoomOut(instance)

    def zoomOut(self, instance):
        # get the values needed for zooming out
        scaleFactor = self.zoomScale.pop()
        coordinates = self.zoomCoord.pop()

        if not self.zoomScale:
            self.remove_widget(self.zoomButton)
            self.remove_widget(self.homeButton)

        xZoom = coordinates[0]
        yZoom = coordinates[1]

        for child in self.children:
            # decrease the size of all widgets on the canvas
            child.size = tuple(i / scaleFactor for i in child.size)

            # translate everything so that the selected zoom area is visible on the screen
            child.pos = (child.pos[0] + xZoom, child.pos[1] + yZoom)

            child.pos = tuple(i / scaleFactor for i in child.pos)
            
            # increase the size of the child's children if it has any
            if child.children:
                for grandchild in child.children:
                    grandchild.size = tuple(i / scaleFactor for i in grandchild.size)
                    grandchild.pos = (grandchild.pos[0] + xZoom, grandchild.pos[1] + yZoom)
                    grandchild.pos = tuple(i / scaleFactor for i in grandchild.pos)

        self.zoomButton.size = (25,25)
        self.zoomButton.pos = (710,20)
        self.homeButton.size = (50,25)
        self.homeButton.pos = (740,20)

        # workaround for slider to adjust to zoom out
        if self.ids.selector.value == 1:
            self.increment()
            self.decrement()
        else:
            self.decrement()
            self.increment()

    def disableZoom(self):
        self.allowZoom = False
    def enableZoom(self):
        self.allowZoom = True

    # convert polar coordinates to cartesian coordinates
    def pol2cart(self, r, theta):
        x = r * cos(theta)
        y = r * sin(theta)

        x *= self.xScale
        y *= self.yScale

        x += Window.width/2
        y += Window.height/2
        return(x, y)

    # tokenize a string by spaces
    def getCol(self, line):
        return line.strip().split()

    def cleanup(self):
        # removes the last motor unit added to the canvas
        if self.lastShown == "single":
            self.remove_widget(self.mu_visible)

        # removes all motor units from the canvas
        if self.lastShown == "all":
            for every in self.childDictionary.values():
                self.remove_widget(every)

        # remove the active motor units from the canvas
        if self.lastShown == "active":
            for every in self.childDictionary:
                if (every in self.activeIDs):
                    muToAdd = self.childDictionary.get(every)
                    self.remove_widget(muToAdd)
                elif every > self.maxID:
                    break

    def updateSlider(self, *args):
        # change the text representing the current ID
        self.currentID.text = str(int(args[1]))

        # remove the current MU
        self.cleanup()

        # get the id of the new MU selected by the slider and add it to the canvas
        visibleID = "%04d" % int(args[1])
        self.mu_visible = self.childDictionary.get(visibleID)
        self.add_widget(self.mu_visible)

        self.lastShown = "single"

    def increment(self):
        # increase the slider's value by 1
        if self.ids.selector.value != 200:
            self.ids.selector.value += 1

    def decrement(self):
        # decrease the slider's value by 1
        if self.ids.selector.value != 1:
            self.ids.selector.value -= 1

    # add all motor units to the canvas
    def showAllMU(self):
        self.cleanup()
        # iterate through all motor units and add them to the canvas
        for every in self.childDictionary.values():
            self.add_widget(every)
        self.lastShown = "all"

    # add the active motor units to the canvas
    def showActiveMU(self):
        self.cleanup()

        # iterate through the motor units
        for every in self.childDictionary:
            # if the motor unit is active add it to the canvas
            if (every in self.activeIDs):
                muToAdd = self.childDictionary.get(every)
                self.add_widget(muToAdd)
            # stop searching after adding the last active motor unit
            elif every > self.maxID:
                break
        self.lastShown = "active"

    def simulate(self):
        self.activeIDs = []
        active = False
        idNum = 1

        # open the AMU.dat file and skip the first line
        with open ("Firing-Data/AMU.dat", "r") as fp:
            next(fp)

            # get the list of active motor units
            for line in fp:
                self.maxID = "%04d" % int(line.strip())
                self.activeIDs.insert(0, self.maxID)

        # open the Muscle Fibre file
        #with open ("MF-unplowed.dat", 'r') as fp:
        with open ("emg/MF-plowed1.dat", 'r') as fp:
            # parse the file
            while line:
                # read a line
                line = fp.readline()

                # get the id of the current motor unit being read
                if ( len(line.strip()) == 8 ) and ( line.split(' ', 1)[0] == "id:" ):
                    # split the line
                    column = self.getCol(line)

                    # create a new motor unit object
                    mu = MotorUnit()
                    mu_id = str(column[1])
                    # check if the MU is active
                    if column[1] in self.activeIDs:
                        active = True
                    else:
                        active = False

                    # go to the line with motor unit info record the number of fibres in the MU
                    line = fp.readline()
                    column = self.getCol(line)
                    numFibres = int(column[0])

                    # scale the motor unit according to its diameter
                    mu.size = tuple(float(column[3]) * i for i in (self.sizeScale,self.sizeScale))

                    # set the location of the motor unit
                    mu.center = (self.pol2cart(float(column[1]), float(column[2])))

                    # print each muscle fibre onto the canvas
                    for i in range(numFibres):
                        fibre = Fibre()

                        # X and Y
                        line = fp.readline()
                        column = self.getCol(line)
                        
                        # set the coordinates of the muscle fibre
                        xCo = float(column[0]) / 20
                        yCo = float(column[1]) / 20

                            
                        # diameter and jshift
                        line = fp.readline()
                        column = self.getCol(line)

                        xCo *= self.xScale
                        yCo *= self.yScale

                        xCo += Window.width/2
                        yCo += Window.height/2
                        
                        fibre.size = tuple(float(column[0]) / 1000 * i for i in (self.sizeScale,self.sizeScale))
                        fibre.center = (xCo,yCo)

                        mu.add_widget(fibre)

                    # save the motor unit to a dictionary
                    self.childDictionary[str(mu_id)] = mu

        # draw the first motor unit
        visibleID = "%04d" % int(self.ids.selector.value)
        self.mu_visible = self.childDictionary.get(visibleID)
        self.add_widget(self.mu_visible)

        # add the muscle boundary
        self.ids.muscle.size = (10.344635*self.sizeScale,10.344635*self.sizeScale)
        self.ids.muscle.center = (Window.width/2, Window.height/2)

class SimulatorApp(App):
    def build(self):
        #Window.clearcolor = (0.251, 0.192, 0.306, 1)
        Window.clearcolor = (0.251/2.5, 0.192/2.5, 0.306/2.5, 1)
        sim = Simulator()
        sim.simulate()
        return sim
    

if __name__ == '__main__':
    SimulatorApp().run()


