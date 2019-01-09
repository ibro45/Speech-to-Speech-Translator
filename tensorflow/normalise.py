import os
import sys
import re
import subprocess
import mimetypes


def r128Stats(filePath):
    """ takes a path to an audio file, returns a dict with the loudness
    stats computed by the ffmpeg ebur128 filter """
    ffargs = ['ffmpeg',
              '-nostats',
              '-i',
              filePath,
              '-filter_complex',
              'ebur128',
              '-f',
              'null',
              '-']
    proc = subprocess.Popen(ffargs, stderr=subprocess.PIPE)
    stats = proc.communicate()[1]
    summaryIndex = stats.rfind('Summary:'.encode())
    summaryList = stats[summaryIndex:].split()
    ILufs = float(summaryList[summaryList.index('I:'.encode()) + 1])
    IThresh = float(summaryList[summaryList.index('I:'.encode()) + 4])
    LRA = float(summaryList[summaryList.index('LRA:'.encode()) + 1])
    LRAThresh = float(summaryList[summaryList.index('LRA:'.encode()) + 4])
    LRALow = float(summaryList[summaryList.index('low:'.encode()) + 1])
    LRAHigh = float(summaryList[summaryList.index('high:'.encode()) + 1])
    statsDict = {'I': ILufs, 'I Threshold': IThresh, 'LRA': LRA,
                 'LRA Threshold': LRAThresh, 'LRA Low': LRALow,
                 'LRA High': LRAHigh}
    return statsDict


def linearGain(iLUFS, goalLUFS=-23):
    """ takes a floating point value for iLUFS, returns the necessary
    multiplier for audio gain to get to the goalLUFS value """
    gainLog = -(iLUFS - goalLUFS)
    return 10 ** (gainLog / 20)


def ffApplyGain(inPath, outPath, linearAmount):
    """ creates a file from inpath at outpath, applying a filter
    for audio volume, multiplying by linearAmount """
    ffargs = ['ffmpeg', '-y', '-i', inPath,
              '-af', 'volume=' + str(linearAmount)]
    if outPath[-4:].lower() == '.mp3':
        ffargs += ['-acodec', 'libmp3lame', '-aq', '0']
    ffargs += [outPath]
    subprocess.Popen(ffargs, stderr=subprocess.PIPE)


def notAudio(filePath):
    if os.path.basename(filePath).startswith("audio"):
        return True
    thisMime = mimetypes.guess_type(re.escape(filePath))[0]
    if thisMime is None or not thisMime.startswith("audio"):
        return True
    return False


def neg23File(filePath):
    if notAudio(filePath):
        print("Not a valid audio file.")
        return False
    print("Scanning " + filePath + " for loudness...")
    try:
        loudnessStats = r128Stats(filePath)
    except:
        print("neg23 encountered an error scanning " + filePath)
    gainAmount = linearGain(loudnessStats['I'])
    print("Creating -23LUFS file at " + filePath)
    try:
        ffApplyGain(filePath, filePath, gainAmount)
    except:
        print("neg23 encountered an error applying gain to " + filePath)
    print("Done")
