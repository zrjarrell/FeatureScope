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

def progressBar(current, total, targetNum, targetTotal, bar_length=40):
    fraction = current / total
    arrow = int(fraction * bar_length - 1) * '-' + '>'
    padding = int(bar_length - len(arrow)) * ' '
    ending = '\n' if (current == total) and (targetNum == targetTotal) else '\r'
    print(f'Progress: [{arrow}{padding}] {int(fraction*100)}% Searching study {"0"*(len(str(total))-len(str(current)))}{current}/{total}: Target {"0"*(len(str(targetTotal))-len(str(targetNum)))}{targetNum} of {targetTotal}', end=ending)

def makeID(label, length, i):
    lead = length - len(str(i))
    newID = label + "0" * lead + str(i)
    return newID