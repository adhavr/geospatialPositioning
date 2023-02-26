import os

from flask import Flask, request, render_template
from PIL import Image
from google.cloud import vision
import os
from pathlib import Path
import json
import math

app = Flask(__name__)


app.config["IMAGE_UPLOADS"] = "C:/Users/ravik/PycharmProjects/flaskimageproject/"

#defaults to the file index.html
@app.route("/")
def home():
    return render_template("index.html")


# Route to output coordinates
@app.route('/upload-image/', methods=['POST'])
def upload_image():
    if request.method == "POST":
        # instantiate variables and data sets
        # "inpic" is the two dimensional array that contains all the data the program generates
        inpic = []
        client = vision.ImageAnnotatorClient()
        avgpairs = [["Golden Gate Bridge", "Golden Gate National Recreation Area"], ["Alcatraz Island", "Alcatraz"]]
        filenames = ["W", "WNW", "NNW", "N", "NNE", "ENE", "E", "ESE", "SSE", "S", "SSW", "WSW"]
        brokenplaces = ["San Francisco", "Fort Mason", "The Westminster", "Houses of Parliament", "London Eye"]
        replacements = [["Marina, View of San Francisco", "Fisherman's Wharf"]]

        # data set with coordinates of each location
        coordinates = [["Golden Gate Bridge", 37.813330, -122.477867],
                       ["Fisherman's Wharf", 37.808555, -122.411022],
                       ["Alcatraz Island", 37.826911, -122.422952],
                       ["Big Ben", 51.500700, -0.124600],
                       ["St Thomas' Hospital", 51.499562, -0.119438],
                       ["Lambeth Bridge", 51.494562, -0.122951],
                       ["London Eye", 51.503300, -0.119600]]

        for name in filenames:
            #opens the twelve images from the requested folder
            filepath = request.form["fname"] + "\\" + name + ".png"
            img = Image.open(filepath)

            width = img.width

            file_name = Path(filepath)

            with open(file_name, 'rb') as image_file:
                content = image_file.read()

            image = vision.Image(content=content)

            response = client.landmark_detection(image=image)
            landmarks = response.landmark_annotations
            # print(landmarks[0], "\n\n\n\n")

            for landmark in landmarks:
                boola = 0
                boolb = 0
                cumulativex = 0
                for pic in inpic:
                    if landmark.description in pic:
                        boola = 1
                        break
                l = filenames.index(name)
                if boola == 1 or boolb == 1:
                    continue
                for i in landmark.bounding_poly.vertices:
                    cumulativex += i.x
                if landmark.score < .2:
                    pass
                elif l == 0:
                    inpic.append([landmark.description, cumulativex / 4, width, name, 12 * 30 - 15])
                else:
                    inpic.append([landmark.description, cumulativex / 4, width, name, l * 30 - 15])
                # print (landmark.score, landmark.description)
        #print(inpic, "\n")
        for pair in avgpairs:
            for i in range(0, len(inpic) - 1):
                for j in range(0, len(inpic) - 1):
                    if inpic[i][0] in pair and inpic[j][0] in pair and inpic[i][3] == inpic[j][3] and inpic[i][0] != \
                            inpic[j][0]:
                        inpic[i][0] = pair[0]
                        inpic[i][1] = (inpic[i][1] + inpic[j][1]) / 2
                        inpic.pop(j)
        arraylength = len(inpic) - 1
        r = 0
        num = 0
        pops = []

        for pic in inpic:
            for place in replacements:
                if place[0] == pic[0]:
                    pic[0] = place[1]

        for pic in inpic:
            pic.append(((((pic[1]) / (pic[2])) * 30) + pic[4]))
            if pic[0] in brokenplaces:
                # inpic.pop(r)
                pops.append(r)
            r += 1
        pops.reverse()
        for popp in pops:
            inpic.pop(popp)

        for pic in inpic:
            for coordinate in coordinates:
                if pic[0] == coordinate[0]:
                    # pic.append(coordinate[1])
                    # pic.append(coordinate[2])
                    pic.append(coordinate[2])
                    pic.append(coordinate[1])
        #print(inpic)
        for pic in inpic:
            pic.append(math.tan(pic[5] * math.pi / 180) * -1)
            pic.append(pic[7] - pic[6] * pic[8])
        finalcoords = []
        finalcoordsr = []
        z = 0
        for pic in inpic:
            for apic in inpic:
                if apic != pic:
                    coordx = round((apic[9] - pic[9]) / (pic[8] - apic[8]), 8)
                    coordy = round(pic[8] * coordx + pic[9], 8)
                    if [round(coordx, 4), round(coordy, 4)] not in finalcoordsr:
                        finalcoordsr.append([round(coordx, 4)])
                        finalcoordsr[z].append(round(coordy, 4))
                        finalcoords.append([coordx])
                        finalcoords[z].append(coordy)
                        z += 1

        totx = 0
        toty = 0
        for coord in finalcoords:
            # toty += coord[1]
            # totx += coord[0]
            toty += coord[0]
            totx += coord[1]

        print("\n\n\n", inpic)
        print(finalcoords)
        returncoords = "(" + str(totx / len(finalcoords)) + ", " + str(toty / len(finalcoords)) + ")"
        link = "https://www.google.com/maps/search/?api=1&query=" + str(totx/len(finalcoords)) + "%2C" + str(toty/len(finalcoords))

        return render_template("upload_image.html", returncoords=returncoords, link=link)


@app.route('/uploads/<filename>')
def send_uploaded_file(filename=''):
    from flask import send_from_directory
    return send_from_directory(app.config["IMAGE_UPLOADS"], filename)


if __name__ == "__main__":
    app.run()