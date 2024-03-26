import math

def properRound(n, decimals=0):
    expoN = n * 10 ** decimals
    if abs(expoN) - abs(math.floor(expoN)) < 0.5:
        result =  math.floor(expoN) / 10 ** decimals
    else:
        result = math.ceil(expoN) / 10 ** decimals
    if decimals <= 0:
        return int(result)
    return result

def progressBar(current, total, bar_length=20):
    fraction = current / total
    arrow = int(fraction * bar_length - 1) * '-' + '>'
    padding = int(bar_length - len(arrow)) * ' '
    ending = '\n' if current == total else '\r'
    print(f'Progress: [{arrow}{padding}] {int(fraction*100)}%', end=ending)
