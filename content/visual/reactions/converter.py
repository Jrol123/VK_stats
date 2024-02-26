"""
Перевод реакций из .svg формата в .png
"""
import cairosvg

COUNT_REACTIONS = 16
for id_reaction in range(1, COUNT_REACTIONS + 1):
    cairosvg.svg2png(url=f'svg/r{id_reaction}.svg', write_to=f'png/r{id_reaction}.png')
