import subprocess
import csv
import json
import argparse

# USAGE (EvtxECmd) : py program.py -f [filename] -csv [csvPath] -csvf [csvFilename]

path = "EvtLogs/APTSimulatorVM_EventLogs_Server2022"
evtxPath = "./EvtxECmd/EvtxeCmd/EvtxECmd.exe"
csvPath = "./Output/"

filepath = "EvtLogs/APTSimulatorVM_EventLogs_Server2022/logs/"

parser = argparse.ArgumentParser()
parser.add_argument('-f', type=str, required=True, help='The filename to process')
parser.add_argument('-csv', type=str, default=csvPath, required=False, help='CSV save filepath')
parser.add_argument('-csvf', type=str, default="output.csv", required=False, help='CSV filename')

args = parser.parse_args()

filepath = args.f
csvPath = args.csv
csvName = args.csvf

command = [evtxPath, '-f', filepath, '--csv', csvPath, '--csvf', csvName]
subprocess.run(command)