import os
import cairosvg

for file in os.listdir("svg"):
    if file.endswith(".svg"):
        name = file.split(".svg")[0]
        cairosvg.svg2png(
            url="svg/" + name + ".svg", write_to="png/" + name.upper() + ".png"
        )
