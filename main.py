import csv
import platform
import tkinter as tk

from PIL.Image import Transpose

import os
import pandas as pd

import constants
import datetime
from PIL import Image, ImageFont, ImageDraw
from resizeimage import resizeimage
import subprocess

# create a basic tkinter window
from tkinter.ttk import *
from tkcalendar import Calendar


def dateLimite(date):
    date = date + datetime.timedelta(days=6)
    return date.strftime('%d/%m/%Y')


def numeroLot(type, poids, date):
    return f"{date.strftime('%Y%m%d')}-{constants.TYPES[type]}{constants.WEIGHT[poids]}"


# save the pdf
def createImg(type, poids, date):
    # Création de l'image
    W, H = (400, 200)
    img = Image.new('RGB', (W, H), color=(255, 255, 255))
    d = ImageDraw.Draw(img)

    # Création de la font
    fnt = ImageFont.truetype('Font/Calibri Regular.ttf', 12)
    fntBold20 = ImageFont.truetype('Font/Calibri Bold.ttf', 20)
    fntBold12 = ImageFont.truetype('Font/Calibri Bold.ttf', 12)

    # Type de patates
    w, h = d.textsize(type)
    d.text(((W - w) / 2 - 40, 20), type, font=fntBold20, fill=(0, 0, 0))

    # Information degré
    d.text((W / 2 - 70, 40), "(A conserver entre 0°C et 4°C)", font=fnt, fill=(0, 0, 0))

    # Poids
    msg = f"Poids net         {poids}"
    w, h = d.textsize(msg)
    d.text(((W - w) / 2 - 10, 60), msg, font=fntBold20, fill=(0, 0, 0))

    # Origine
    d.text((85, 85), "Origine : France", font=fnt, fill=(0, 0, 0))

    # N° Lot
    d.text((85, 105), "N° Lot : ", font=fnt, fill=(0, 0, 0))
    d.text((250, 105), numeroLot(type, poids, date), font=fntBold12, fill=(0, 0, 0))

    # Date péremption
    d.text((85, 125), "A consommé jusqu'au : ", font=fnt, fill=(0, 0, 0))
    d.text((250, 125), dateLimite(date), font=fntBold12, fill=(0, 0, 0))

    # DOMFRITE
    msg = "DOMFRITE"
    w, h = d.textsize(msg)
    d.text(((W - w) / 2 - 20, 150), msg, font=fntBold20, fill=(0, 0, 0))

    # Adresse
    msg = "95, chem de la Giroday - Bois Rouge - 97460 St Paul"
    d.text((80, 175), msg, font=fnt, fill=(0, 0, 0))

    img = img.transpose(Transpose.ROTATE_90)
    img.save('etiquette.png', q=100)
    formatImg()

    # Afficher l'image
    showFile("etiquette.png")

    storeHistory(type, poids, date)


def formatImg():
    with open('etiquette.png', 'r+b') as f:
        with Image.open(f) as image:
            cover = resizeimage.resize_cover(image, [151, 302])
            cover.save('etiquette.png', image.format)


def storeHistory(type, poids, date):
    with open("history.csv", "a") as csvfile:
        writer = csv.writer(csvfile, delimiter=';')
        writer.writerow([
            date.strftime('%d/%m/%Y'),
            type,
            poids,
            constants.TYPES[type],
            constants.WEIGHT[poids],
            dateLimite(date),
            numeroLot(type, poids, date)])
        csvfile.close()


def showFile(filename):
    if platform.system() == "Windows":
        os.startfile(filename)
    elif platform.system() == "Darwin":
        subprocess.call(('open', filename))
    else:
        subprocess.call(('xdg-open', filename))


root = tk.Tk()
root.title("DomFrite")
root.geometry("400x400")

# Création du fichier pour les sauvegarde de données
if not (os.path.isfile("history.csv")):
    with open("history.csv", "w") as csvfile:
        writer = csv.writer(csvfile, delimiter=";")
        writer.writerow(["DATE", "TYPE", "POIDS", "CODE TYPE", "CODE POIDS", "DELAI", "N° LOT"])

Label(root, text="Choisissez un type de patates:").pack()
choiceType = Combobox(root, width=30)
choiceType['values'] = list(constants.TYPES.keys())
choiceType.current(0)
choiceType.pack()

Label(root, text="Choisissez un poids:").pack()
choiceWeight = Combobox(root, width=10)
choiceWeight['values'] = list(constants.WEIGHT.keys())
choiceWeight.current(0)
choiceWeight.pack()

Label(root, text="Choisissez une date:").pack()
choiceDate = Calendar(root, selectmode='day')
choiceDate.pack()

printButton = Button(root, text="Sauvegarder l'image",
                     command=lambda: createImg(choiceType.get(), choiceWeight.get(), choiceDate.selection_get()))
printButton.pack()

historyButton = Button(root, text="Historique", command=lambda: showFile("history.csv"))
historyButton.pack()

root.mainloop()
