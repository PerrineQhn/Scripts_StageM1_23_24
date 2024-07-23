import math

def semitones_between(frequency1, frequency2):
    if frequency1 <= 0 or frequency2 <= 0:
        return None

    if frequency1 == frequency2:
        return 0

    ratio = frequency1 / frequency2
    semitones = 12 * math.log2(ratio)

    return round(semitones, 3)

#print(semitones_between(160.5, 13))

