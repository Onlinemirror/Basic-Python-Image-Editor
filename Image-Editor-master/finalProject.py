from tkinter import filedialog
from tkinter import *
import tkinter.messagebox
from PIL import Image, ImageTk
from PIL import ImageOps
import imghdr
from collections import *


def colourPop(canvas):
    canvas.data.cropPopToHappen = False
    canvas.data.colourPopToHappen = True
    canvas.data.drawOn = False
    tkinter.messagebox.showinfo(title="Colour Pop", message="Click on a part of the image which you want in colour",
                          parent=canvas.data.mainWindow)
    if canvas.data.cropPopToHappen == False:
        canvas.data.mainWindow.bind("<ButtonPress-1>", lambda event: getPixel(event, canvas))


def getPixel(event, canvas):
    try:
        if canvas.data.colourPopToHappen == True and \
                canvas.data.cropPopToHappen == False and canvas.data.image != None:
            data = []
            canvas.data.pixelx = \
                int(round((event.x - canvas.data.imageTopX) * canvas.data.imageScale))
            canvas.data.pixely = \
                int(round((event.y - canvas.data.imageTopY) * canvas.data.imageScale))
            pixelr, pixelg, pixelb = \
                canvas.data.image.getpixel((canvas.data.pixelx, canvas.data.pixely))
            tolerance = 60
            for y in range(canvas.data.image.size[1]):
                for x in range(canvas.data.image.size[0]):
                    r, g, b = canvas.data.image.getpixel((x, y))
                    avg = int(round((r + g + b) / 3.0))
                    if (abs(r - pixelr) > tolerance or
                            abs(g - pixelg) > tolerance or
                            abs(b - pixelb) > tolerance):
                        R, G, B = avg, avg, avg
                    else:
                        R, G, B = r, g, b
                    data.append((R, G, B))
            canvas.data.image.putdata(data)
            save(canvas)
            canvas.data.undoQueue.append(canvas.data.image.copy())
            canvas.data.imageForTk = makeImageForTk(canvas)
            drawImage(canvas)
    except:
        pass
    canvas.data.colourPopToHappen = False


def crop(canvas):
    canvas.data.colourPopToHappen = False
    canvas.data.drawOn = False
    canvas.data.cropPopToHappen = True
    tkinter.messagebox.showinfo(title="Crop", \
                          message="Draw cropping rectangle and press Enter", \
                          parent=canvas.data.mainWindow)
    if canvas.data.image != None:
        canvas.data.mainWindow.bind("<ButtonPress-1>", \
                                    lambda event: startCrop(event, canvas))
        canvas.data.mainWindow.bind("<B1-Motion>", \
                                    lambda event: drawCrop(event, canvas))
        canvas.data.mainWindow.bind("<ButtonRelease-1>", \
                                    lambda event: endCrop(event, canvas))


def startCrop(event, canvas):
    if canvas.data.endCrop == False and canvas.data.cropPopToHappen == True:
        canvas.data.startCropX = event.x
        canvas.data.startCropY = event.y


def drawCrop(event, canvas):
    if canvas.data.endCrop == False and canvas.data.cropPopToHappen == True:
        canvas.data.tempCropX = event.x
        canvas.data.tempCropY = event.y
        canvas.create_rectangle(canvas.data.startCropX, \
                                canvas.data.startCropY,
                                canvas.data.tempCropX, \
                                canvas.data.tempCropY, fill="blue", stipple="gray75", width=0)


def endCrop(event, canvas):
    if canvas.data.cropPopToHappen == True:
        canvas.data.endCrop = True
        canvas.data.endCropX = event.x
        canvas.data.endCropY = event.y
        canvas.create_rectangle(canvas.data.startCropX, \
                                canvas.data.startCropY,
                                canvas.data.endCropX, \
                                canvas.data.endCropY, fill="blue", stipple="gray75", width=0)
        canvas.data.mainWindow.bind("<Return>", \
                                    lambda event: performCrop(event, canvas))


def performCrop(event, canvas):
    canvas.data.image = \
        canvas.data.image.crop( \
            (int(round((canvas.data.startCropX - canvas.data.imageTopX) * canvas.data.imageScale)),
             int(round((canvas.data.startCropY - canvas.data.imageTopY) * canvas.data.imageScale)),
             int(round((canvas.data.endCropX - canvas.data.imageTopX) * canvas.data.imageScale)),
             int(round((canvas.data.endCropY - canvas.data.imageTopY) * canvas.data.imageScale))))
    canvas.data.endCrop = False
    canvas.data.cropPopToHappen = False
    save(canvas)
    canvas.data.undoQueue.append(canvas.data.image.copy())
    canvas.data.imageForTk = makeImageForTk(canvas)
    drawImage(canvas)


def rotateFinished(canvas, rotateWindow, rotateSlider, previousAngle):
    if canvas.data.rotateWindowClose == True:
        rotateWindow.destroy()
        canvas.data.rotateWindowClose = False
    else:
        if canvas.data.image != None and rotateWindow.winfo_exists():
            canvas.data.angleSelected = rotateSlider.get()
            if canvas.data.angleSelected != None and \
                    canvas.data.angleSelected != previousAngle:
                canvas.data.image = \
                    canvas.data.image.rotate(float(canvas.data.angleSelected))
                canvas.data.imageForTk = makeImageForTk(canvas)
                drawImage(canvas)
        canvas.after(200, lambda: rotateFinished(canvas, \
                                                 rotateWindow, rotateSlider, canvas.data.angleSelected))


def closeRotateWindow(canvas):
    if canvas.data.image != None:
        save(canvas)
        canvas.data.undoQueue.append(canvas.data.image.copy())
        canvas.data.rotateWindowClose = True


def rotate(canvas):
    canvas.data.colourPopToHappen = False
    canvas.data.cropPopToHappen = False
    canvas.data.drawOn = False
    rotateWindow = Toplevel(canvas.data.mainWindow)
    rotateWindow.title("Rotate")
    rotateSlider = Scale(rotateWindow, from_=0, to=360, orient=HORIZONTAL)
    rotateSlider.pack()
    OkRotateFrame = Frame(rotateWindow)
    OkRotateButton = Button(OkRotateFrame, text="OK", \
                            command=lambda: closeRotateWindow(canvas))
    OkRotateButton.grid(row=0, column=0)
    OkRotateFrame.pack(side=BOTTOM)
    rotateFinished(canvas, rotateWindow, rotateSlider, 0)


def closeBrightnessWindow(canvas):
    if canvas.data.image != None:
        save(canvas)
        canvas.data.undoQueue.append(canvas.data.image.copy())
        canvas.data.brightnessWindowClose = True


def changeBrightness(canvas, brightnessWindow, brightnessSlider, \
                     previousVal):
    if canvas.data.brightnessWindowClose == True:
        brightnessWindow.destroy()
        canvas.data.brightnessWindowClose = False

    else:
        if canvas.data.image != None and brightnessWindow.winfo_exists():
            sliderVal = brightnessSlider.get()
            scale = (sliderVal - previousVal) / 100.0
            canvas.data.image = canvas.data.image.point(
                lambda i: i + int(round(i * scale)))
            canvas.data.imageForTk = makeImageForTk(canvas)
            drawImage(canvas)
            canvas.after(200,
                         lambda: changeBrightness(canvas, brightnessWindow,
                                                  brightnessSlider, sliderVal))


def brightness(canvas):
    canvas.data.colourPopToHappen = False
    canvas.data.cropPopToHappen = False
    canvas.data.drawOn = False
    brightnessWindow = Toplevel(canvas.data.mainWindow)
    brightnessWindow.title("Brightness")
    brightnessSlider = Scale(brightnessWindow, from_=-100, to=100,
                             orient=HORIZONTAL)
    brightnessSlider.pack()
    OkBrightnessFrame = Frame(brightnessWindow)
    OkBrightnessButton = Button(OkBrightnessFrame, text="OK",
                                command=lambda: closeBrightnessWindow(canvas))
    OkBrightnessButton.grid(row=0, column=0)
    OkBrightnessFrame.pack(side=BOTTOM)
    changeBrightness(canvas, brightnessWindow, brightnessSlider, 0)
    brightnessSlider.set(0)


def reset(canvas):
    canvas.data.colourPopToHappen = False
    canvas.data.cropPopToHappen = False
    canvas.data.drawOn = False
    if canvas.data.image != None:
        canvas.data.image = canvas.data.originalImage.copy()
        save(canvas)
        canvas.data.undoQueue.append(canvas.data.image.copy())
        canvas.data.imageForTk = makeImageForTk(canvas)
        drawImage(canvas)


def mirror(canvas):
    canvas.data.colourPopToHappen = False
    canvas.data.cropPopToHappen = False
    canvas.data.drawOn = False
    if canvas.data.image != None:
        canvas.data.image = ImageOps.mirror(canvas.data.image)
        save(canvas)
        canvas.data.undoQueue.append(canvas.data.image.copy())
        canvas.data.imageForTk = makeImageForTk(canvas)
        drawImage(canvas)


def flip(canvas):
    canvas.data.colourPopToHappen = False
    canvas.data.cropPopToHappen = False
    canvas.data.drawOn = False
    if canvas.data.image != None:
        canvas.data.image = ImageOps.flip(canvas.data.image)
        save(canvas)
        canvas.data.undoQueue.append(canvas.data.image.copy())
        canvas.data.imageForTk = makeImageForTk(canvas)
        drawImage(canvas)



#-----------------FILTERS------------------#

def covertGray(canvas):
    canvas.data.colourPopToHappen = False
    canvas.data.cropPopToHappen = False
    canvas.data.drawOn = False
    if canvas.data.image != None:
        data = []
        for col in range(canvas.data.image.size[1]):
            for row in range(canvas.data.image.size[0]):
                r, g, b = canvas.data.image.getpixel((row, col))
                avg = int(round((r + g + b) / 3.0))
                R, G, B = avg, avg, avg
                data.append((R, G, B))
        canvas.data.image.putdata(data)
        save(canvas)
        canvas.data.undoQueue.append(canvas.data.image.copy())
        canvas.data.imageForTk = makeImageForTk(canvas)
        drawImage(canvas)


def sepia(canvas):
    canvas.data.colourPopToHappen = False
    canvas.data.cropPopToHappen = False
    canvas.data.drawOn = False
    if canvas.data.image != None:
        sepiaData = []
        for col in range(canvas.data.image.size[1]):
            for row in range(canvas.data.image.size[0]):
                r, g, b = canvas.data.image.getpixel((row, col))
                avg = int(round((r + g + b) / 3.0))
                R, G, B = avg + 100, avg + 50, avg
                sepiaData.append((R, G, B))
        canvas.data.image.putdata(sepiaData)
        save(canvas)
        canvas.data.undoQueue.append(canvas.data.image.copy())
        canvas.data.imageForTk = makeImageForTk(canvas)
        drawImage(canvas)


def invert(canvas):
    canvas.data.colourPopToHappen = False
    canvas.data.cropPopToHappen = False
    canvas.data.drawOn = False
    if canvas.data.image != None:
        canvas.data.image = ImageOps.invert(canvas.data.image)
        save(canvas)
        canvas.data.undoQueue.append(canvas.data.image.copy())
        canvas.data.imageForTk = makeImageForTk(canvas)
        drawImage(canvas)


def solarize(canvas):
    canvas.data.colourPopToHappen = False
    canvas.data.cropPopToHappen = False
    solarizeWindow = Toplevel(canvas.data.mainWindow)
    solarizeWindow.title("Solarize")
    solarizeSlider = Scale(solarizeWindow, from_=0, to=255, orient=HORIZONTAL)
    solarizeSlider.pack()
    OkSolarizeFrame = Frame(solarizeWindow)
    OkSolarizeButton = Button(OkSolarizeFrame, text="OK", \
                              command=lambda: closeSolarizeWindow(canvas))
    OkSolarizeButton.grid(row=0, column=0)
    OkSolarizeFrame.pack(side=BOTTOM)
    performSolarize(canvas, solarizeWindow, solarizeSlider, 255)


def performSolarize(canvas, solarizeWindow, solarizeSlider, previousThreshold):
    if canvas.data.solarizeWindowClose == True:
        solarizeWindow.destroy()
        canvas.data.solarizeWindowClose = False

    else:
        if solarizeWindow.winfo_exists():
            sliderVal = solarizeSlider.get()
            threshold_ = 255 - sliderVal
            if canvas.data.image != None and threshold_ != previousThreshold:
                canvas.data.image = ImageOps.solarize(canvas.data.image, \
                                                      threshold=threshold_)
                canvas.data.imageForTk = makeImageForTk(canvas)
                drawImage(canvas)
            canvas.after(200, lambda: performSolarize(canvas, \
                                                      solarizeWindow, solarizeSlider, threshold_))


def closeSolarizeWindow(canvas):
    if canvas.data.image != None:
        save(canvas)
        canvas.data.undoQueue.append(canvas.data.image.copy())
        canvas.data.solarizeWindowClose = True


def posterize(canvas):
    canvas.data.colourPopToHappen = False
    canvas.data.cropPopToHappen = False
    canvas.data.drawOn = False
    posterData = []
    if canvas.data.image != None:
        for col in range(canvas.data.imageSize[1]):
            for row in range(canvas.data.imageSize[0]):
                r, g, b = canvas.data.image.getpixel((row, col))
                if r in range(32):
                    R = 0
                elif r in range(32, 96):
                    R = 64
                elif r in range(96, 160):
                    R = 128
                elif r in range(160, 224):
                    R = 192
                elif r in range(224, 256):
                    R = 255
                if g in range(32):
                    G = 0
                elif g in range(32, 96):
                    G = 64
                elif g in range(96, 160):
                    G = 128
                elif r in range(160, 224):
                    g = 192
                elif r in range(224, 256):
                    G = 255
                if b in range(32):
                    B = 0
                elif b in range(32, 96):
                    B = 64
                elif b in range(96, 160):
                    B = 128
                elif b in range(160, 224):
                    B = 192
                elif b in range(224, 256):
                    B = 255
                posterData.append((R, G, B))
        canvas.data.image.putdata(posterData)
        save(canvas)
        canvas.data.undoQueue.append(canvas.data.image.copy())
        canvas.data.imageForTk = makeImageForTk(canvas)
        drawImage(canvas)


#-------------------EDIT MENU FUNCTIONS-------------------#

def undo(canvas):
    if len(canvas.data.undoQueue) > 0:
        lastImage = canvas.data.undoQueue.pop()
        canvas.data.redoQueue.appendleft(lastImage)
    if len(canvas.data.undoQueue) > 0:
        canvas.data.image = canvas.data.undoQueue[-1]
    save(canvas)
    canvas.data.imageForTk = makeImageForTk(canvas)
    drawImage(canvas)


def redo(canvas):
    if len(canvas.data.redoQueue) > 0:
        canvas.data.image = canvas.data.redoQueue[0]
    save(canvas)
    if len(canvas.data.redoQueue) > 0:
        lastImage = canvas.data.redoQueue.popleft()
        canvas.data.undoQueue.append(lastImage)
    canvas.data.imageForTk = makeImageForTk(canvas)
    drawImage(canvas)


#-------------------MENU COMMANDS--------------------#

def saveAs(canvas):
    if canvas.data.image != None:
        filename = tkinter.filedialog.asksaveasfilename(defaultextension=".jpg")
        im = canvas.data.image
        im.save(filename)


def save(canvas):
    if canvas.data.image != None:
        im = canvas.data.image
        im.save(canvas.data.imageLocation)


def newImage(canvas):
    imageName = filedialog.askopenfilename()
    filetype = ""
    try:
        filetype = imghdr.what(imageName)
    except:
        tkinter.messagebox.showinfo(title="Image File", \
                              message="Choose an Image File!", parent=canvas.data.mainWindow)
    if filetype in ['jpeg', 'bmp', 'png', 'tiff']:
        canvas.data.imageLocation = imageName
        im = Image.open(imageName)
        canvas.data.image = im
        canvas.data.originalImage = im.copy()
        canvas.data.undoQueue.append(im.copy())
        canvas.data.imageSize = im.size
        canvas.data.imageForTk = makeImageForTk(canvas)
        drawImage(canvas)
    else:
        tkinter.messagebox.showinfo(title="Image File", \
                              message="Choose an Image File!", parent=canvas.data.mainWindow)



def makeImageForTk(canvas):
    im = canvas.data.image
    if canvas.data.image != None:
        imageWidth = canvas.data.image.size[0]
        imageHeight = canvas.data.image.size[1]
        if imageWidth > imageHeight:
            resizedImage = im.resize((canvas.data.width, \
                                      int(round(float(imageHeight) * canvas.data.width / imageWidth))))
            canvas.data.imageScale = float(imageWidth) / canvas.data.width
        else:
            resizedImage = im.resize((int(round(float(imageWidth) * canvas.data.height / imageHeight)), \
                                      canvas.data.height))
            canvas.data.imageScale = float(imageHeight) / canvas.data.height
        canvas.data.resizedIm = resizedImage
        return ImageTk.PhotoImage(resizedImage)


def drawImage(canvas):
    if canvas.data.image != None:
        canvas.create_image(canvas.data.width / 2.0 - canvas.data.resizedIm.size[0] / 2.0,
                            canvas.data.height / 2.0 - canvas.data.resizedIm.size[1] / 2.0,
                            anchor=NW, image=canvas.data.imageForTk)
        canvas.data.imageTopX = int(round(canvas.data.width / 2.0 - canvas.data.resizedIm.size[0] / 2.0))
        canvas.data.imageTopY = int(round(canvas.data.height / 2.0 - canvas.data.resizedIm.size[1] / 2.0))



#--------------INITIALIZE-----------------#

def init(root, canvas):
    buttonsInit(root, canvas)
    menuInit(root, canvas)
    canvas.data.image = None
    canvas.data.angleSelected = None
    canvas.data.rotateWindowClose = False
    canvas.data.brightnessWindowClose = False
    canvas.data.brightnessLevel = None
    canvas.data.histWindowClose = False
    canvas.data.solarizeWindowClose = False
    canvas.data.posterizeWindowClose = False
    canvas.data.colourPopToHappen = False
    canvas.data.cropPopToHappen = False
    canvas.data.endCrop = False
    canvas.data.drawOn = True

    canvas.data.undoQueue = deque([], 10)
    canvas.data.redoQueue = deque([], 10)
    canvas.pack()


def buttonsInit(root, canvas):
    backgroundColour = "white"
    buttonWidth = 14
    buttonHeight = 2
    toolKitFrame = Frame(root)
    cropButton = Button(toolKitFrame, text="Crop",
                        background=backgroundColour, \
                        width=buttonWidth, height=buttonHeight, \
                        command=lambda: crop(canvas))
    cropButton.grid(row=0, column=0)
    rotateButton = Button(toolKitFrame, text="Rotate", \
                          background=backgroundColour, \
                          width=buttonWidth, height=buttonHeight, \
                          command=lambda: rotate(canvas))
    rotateButton.grid(row=1, column=0)
    brightnessButton = Button(toolKitFrame, text="Brightness", \
                              background=backgroundColour, \
                              width=buttonWidth, height=buttonHeight, \
                              command=lambda: brightness(canvas))
    brightnessButton.grid(row=2, column=0)
    colourPopButton = Button(toolKitFrame, text="Colour Pop", \
                             background=backgroundColour, \
                             width=buttonWidth, height=buttonHeight, \
                             command=lambda: colourPop(canvas))
    colourPopButton.grid(row=4, column=0)
    mirrorButton = Button(toolKitFrame, text="Mirror", \
                          background=backgroundColour, \
                          width=buttonWidth, height=buttonHeight, \
                          command=lambda: mirror(canvas))
    mirrorButton.grid(row=5, column=0)
    flipButton = Button(toolKitFrame, text="Flip", \
                        background=backgroundColour, \
                        width=buttonWidth, height=buttonHeight, \
                        command=lambda: flip(canvas))
    flipButton.grid(row=6, column=0)
    resetButton = Button(toolKitFrame, text="Reset", \
                         background=backgroundColour, width=buttonWidth, \
                         height=buttonHeight, command=lambda: reset(canvas))
    resetButton.grid(row=9, column=0)
    toolKitFrame.pack(side=LEFT)


def menuInit(root, canvas):
    menubar = Menu(root)
    filemenu = Menu(menubar, tearoff=0)
    filemenu.add_command(label="New", command=lambda: newImage(canvas))
    filemenu.add_command(label="Save", command=lambda: save(canvas))
    filemenu.add_command(label="Save As", command=lambda: saveAs(canvas))
    menubar.add_cascade(label="File", menu=filemenu)
    root.config(menu=menubar)
    ## Edit pull-down Menu
    editmenu = Menu(menubar, tearoff=0)
    editmenu.add_command(label="Undo   Ctrl+Z", command=lambda: undo(canvas))
    editmenu.add_command(label="Redo   Ctrl+Y", command=lambda: redo(canvas))
    menubar.add_cascade(label="Edit", menu=editmenu)
    root.config(menu=menubar)
    ## Filter pull-down Menu
    filtermenu = Menu(menubar, tearoff=0)
    filtermenu.add_command(label="Black and White",
                           command=lambda: covertGray(canvas))
    filtermenu.add_command(label="Sepia",
                           command=lambda: sepia(canvas))
    filtermenu.add_command(label="Invert",
                           command=lambda: invert(canvas))
    filtermenu.add_command(label="Solarize",
                           command=lambda: solarize(canvas))
    filtermenu.add_command(label="Posterize",
                           command=lambda: posterize(canvas))
    menubar.add_cascade(label="Filter", menu=filtermenu)
    root.config(menu=menubar)


def run():
    root = Tk()
    root.title("Image Editor")
    canvasWidth = 500
    canvasHeight = 500
    canvas = Canvas(root, width=canvasWidth, height=canvasHeight, \
                    background="gray")

    class Struct: pass

    canvas.data = Struct()
    canvas.data.width = canvasWidth
    canvas.data.height = canvasHeight
    canvas.data.mainWindow = root
    init(root, canvas)
    root.bind("<Control-z>", lambda event: undo(canvas))
    root.bind("<Control-y>", lambda event: redo(canvas))
    root.mainloop()


run()
