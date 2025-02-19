import subprocess
import os
import argparse
import pandas as pd

def combine_files(files, output_file):
    with open(output_file, 'w', newline='', encoding='utf-8', errors='replace') as outfile:
        first_file = True
        for file in files:
            file_path = os.path.join(csvPath, file)
            if os.path.exists(file_path):
                df = pd.read_csv(file_path)
                df.insert(0, 'SourceCSV', file)
                if not first_file:
                    outfile.write('\n')
                df.to_csv(outfile, index=False, mode='a', encoding='utf-8', errors='replace')
                first_file = False
            else:
                print(f"Warning: {file_path} does not exist and will be skipped.")

def combine_keyword(files, output_file, keyword):
    with open(output_file, 'w', newline='') as outfile:
        first_file = True
        for file in files:
            file_path = os.path.join(csvPath, file)
            if os.path.exists(file_path):
                df = pd.read_csv(file_path)
                mask = df.apply(lambda row: row.astype(str).str.contains(keyword, case=False, na=False).any(), axis=1)
                filtered_df = df[mask]
                if not filtered_df.empty:
                    filtered_df.insert(0, 'SourceCSV', file)
                    if not first_file:
                        outfile.write('\n')
                    filtered_df.to_csv(outfile, index=False)
                    first_file = False
            else:
                print(f"Warning: {file_path} does not exist and will be skipped.")

evtxPath = "./EvtxECmd/EvtxeCmd/EvtxECmd.exe"
pecmdPath = "./PECmd/PECmd.exe"
appcompatPath = "./AppCompatCacheParser/AppCompatCacheParser.exe"
csvPath = "./Output/"

parser = argparse.ArgumentParser(description="Process and combine forensic artifacts.")

parser.add_argument('-ef', type=str, help='Path to a single .evtx file')
parser.add_argument('-pf', type=str, help='Path to a single .pf file')
parser.add_argument('-sf', type=str, help='Path to a single SYSTEM file')
parser.add_argument('-ed', type=str, help='Path to a Windows Log directory')
parser.add_argument('-pd', type=str, help='Path to a Prefetch directory')

parser.add_argument('--files', nargs='+', type=str, help='List of CSV files to combine')
parser.add_argument('--keyword', type=str, help='Keyword to filter rows in the combined CSV')
parser.add_argument('--evtx', type=str, default="evtx.csv", help='Filename of EvtxECmd output CSV')
parser.add_argument('--pecmd', type=str, default="pecmd.csv", help='Filename of PECmd output CSV')
parser.add_argument('--appcompat', type=str, default="appcompat.csv", help='Filename of AppCompatCacheParser output CSV')
parser.add_argument('--comb', type=str, default="combined_output.csv", help='Filename for combined output CSV')

args = parser.parse_args()

# Process individual files or directories
if args.ef:
    command = [evtxPath, '-f', args.ef, '--csv', csvPath, '--csvf', args.evtx]
    subprocess.run(command)
if args.pf:
    command = [pecmdPath, '-f', args.pf, '--csv', csvPath, '--csvf', args.pecmd]
    subprocess.run(command)
if args.sf:
    command = [appcompatPath, '-f', args.sf, '--csv', csvPath, '--csvf', args.appcompat]
    subprocess.run(command)
if args.ed:
    command = [evtxPath, '-d', args.ed, '--csv', csvPath, '--csvf', args.evtx]
    subprocess.run(command)
if args.pd:
    command = [pecmdPath, '-d', args.pd, '--csv', csvPath, '--csvf', args.pecmd]
    subprocess.run(command)

# Combine CSV files
if args.files:
    output_path = os.path.join(csvPath, args.comb)
    if args.keyword:
        combine_keyword(args.files, output_path, args.keyword)
    else:
        combine_files(args.files, output_path)
