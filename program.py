import subprocess
import os
import argparse
import pandas as pd

def combine_files(files, output_file, dir):
    output_path = os.path.join(dir, output_file)

    with open(output_path, 'w', newline='', encoding='utf-8', errors='replace') as outfile:
        first_file = True
        for file in files:
            if os.path.exists(file):
                df = pd.read_csv(file)
                df.insert(0, 'SourceCSV', file)
                if not first_file:
                    outfile.write('\n')
                df.to_csv(outfile, index=False, mode='a', encoding='utf-8', errors='replace')
                first_file = False
            else:
                print(f"Warning: {file} does not exist and will be skipped.")

def combine_keyword(files, output_file, keyword, dir):
    output_path = os.path.join(dir, output_file)

    with open(output_path, 'w', newline='') as outfile:
        first_file = True
        for file in files:
            if os.path.exists(file):
                df = pd.read_csv(file)
                mask = df.apply(lambda row: row.astype(str).str.contains(keyword, case=False, na=False).any(), axis=1)
                filtered_df = df[mask]
                if not filtered_df.empty:
                    filtered_df.insert(0, 'SourceCSV', file)
                    if not first_file:
                        outfile.write('\n')
                    filtered_df.to_csv(outfile, index=False)
                    first_file = False
            else:
                print(f"Warning: {file} does not exist and will be skipped.")

def find_sys(dir):
    for root, dirs, files in os.walk(dir):
        for file in files:
            file_name, _ = os.path.splitext(file)
            if file_name.lower() == 'system':
                return os.path.join(root, file)
    return False

evtxPath = "./EvtxECmd/EvtxeCmd/EvtxECmd.exe"
pecmdPath = "./PECmd/PECmd.exe"
appcompatPath = "./AppCompatCacheParser/AppCompatCacheParser.exe"
evidencePath = './Evidence'

parser = argparse.ArgumentParser(description="Process and combine forensic artifacts.")

# DIR Commands
parser.add_argument('-d', type=str, help='Path to directory to process')
parser.add_argument('-df', type=str, default="./", help='Path to dump output CSV')

# Tool Commands
parser.add_argument('--files', nargs='+', type=str, help='List of CSV files to combine')
parser.add_argument('--keyword', type=str, help='Keyword to filter rows in the combined CSV')

# Filename
parser.add_argument('--evtx', type=str, default="evtx.csv", help='Filename of EvtxECmd output CSV')
parser.add_argument('--pecmd', type=str, default="pecmd.csv", help='Filename of PECmd output CSV')
parser.add_argument('--appcompat', type=str, default="appcompat.csv", help='Filename of AppCompatCacheParser output CSV')
parser.add_argument('--comb', type=str, default="combined_output.csv", help='Filename for combined output CSV')

args = parser.parse_args()

if args.d:
    evtx_cmd = [evtxPath, '-d', args.d, '--csv', args.df, '--csvf', args.evtx]
    pec_cmd = [pecmdPath, '-d', args.d, '--csv', args.df, '--csvf', args.pecmd]
    
    sys_dir = find_sys(args.d)
    if sys_dir != False:
        sys_cmd = [appcompatPath, '-f', sys_dir, '--csv', args.df, '--csvf', args.appcompat]
        subprocess.run(evtx_cmd)
        subprocess.run(pec_cmd)
        subprocess.run(sys_cmd)
    else:
        print("ERROR : SYSTEM file not found")

if args.keyword and not args.files:
    print("ERROR : Provide files to combine with keyword")
elif args.comb and not args.files:
    print("ERROR : Provide files to combine")

# Combine CSV files
if args.files:
    if args.keyword:
        combine_keyword(args.files, args.comb, args.keyword, args.df)
        print("SYSTEM : Keyword successfully filtered")
    else:
        combine_files(args.files, args.comb, args.df)
        print("SYSTEM : Successfully combined files")
