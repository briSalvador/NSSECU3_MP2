import subprocess
import os
import argparse
import pandas as pd

def get_csv_files(directory):
    return [os.path.join(directory, f) for f in os.listdir(directory) if f.endswith('.csv')]

def ensure_directory_exists(directory):
    if not os.path.exists(directory):
        os.makedirs(directory)

def combine_files(directory, output_file, output_dir):
    files = get_csv_files(directory)
    if not files:
        print("No CSV files found in the directory.")
        return
    
    ensure_directory_exists(output_dir)
    output_path = os.path.join(output_dir, output_file)
    first_file = True
    with open(output_path, 'w', newline='', encoding='utf-8', errors='replace') as outfile:
        for file in files:
            df = pd.read_csv(file, on_bad_lines='skip', engine='python')
            df.insert(0, 'SourceCSV', os.path.basename(file))
            if first_file:
                df.to_csv(outfile, index=False, mode='a', encoding='utf-8', errors='replace')
                first_file = False
            else:
                outfile.write('\n')  # Ensure a blank line between different files
                df.to_csv(outfile, index=False, mode='a', header=True, encoding='utf-8', errors='replace')

def combine_keyword(directory, output_file, keyword, output_dir):
    files = get_csv_files(directory)
    if not files:
        print("No CSV files found in the directory.")
        return
    
    ensure_directory_exists(output_dir)
    output_path = os.path.join(output_dir, output_file)
    first_file = True
    with open(output_path, 'w', newline='') as outfile:
        for file in files:
            df = pd.read_csv(file, on_bad_lines='skip', engine='python')
            mask = df.apply(lambda row: row.astype(str).str.contains(keyword, case=False, na=False).any(), axis=1)
            filtered_df = df[mask]
            if not filtered_df.empty:
                filtered_df.insert(0, 'SourceCSV', os.path.basename(file))
                if first_file:
                    filtered_df.to_csv(outfile, index=False, mode='a')
                    first_file = False
                else:
                    outfile.write('\n')  # Ensure a blank line between different files
                    filtered_df.to_csv(outfile, index=False, mode='a', header=True)

def find_sys(directory):
    for root, _, files in os.walk(directory):
        for file in files:
            if file.lower() == 'system':
                return os.path.join(root, file)
    return False

evtxPath = "./EvtxECmd/EvtxeCmd/EvtxECmd.exe"
pecmdPath = "./PECmd/PECmd.exe"
appcompatPath = "./AppCompatCacheParser/AppCompatCacheParser.exe"
evidencePath = './Evidence'

parser = argparse.ArgumentParser(description="Process and combine forensic artifacts.")

# Directory Input
parser.add_argument('-d', type=str, help='Path to directory to process')
parser.add_argument('-df', type=str, default="./", help='Path to dump output CSV')
parser.add_argument('-dir', type=str, help='Path to directory containing CSV files to combine')
parser.add_argument('-keyword', type=str, help='Keyword to filter rows in the combined CSV')

# Filename
parser.add_argument('-comb', type=str, default="combined_output.csv", help='Filename for combined output CSV')

args = parser.parse_args()

if args.d:
    evtx_cmd = [evtxPath, '-d', args.d, '--csv', args.df, '--csvf', "evtx.csv"]
    pec_cmd = [pecmdPath, '-d', args.d, '--csv', args.df, '--csvf', "pecmd.csv"]
    
    sys_dir = find_sys(args.d)
    if sys_dir:
        sys_cmd = [appcompatPath, '-f', sys_dir, '--csv', args.df, '--csvf', "appcompat.csv"]
        subprocess.run(evtx_cmd)
        subprocess.run(pec_cmd)
        subprocess.run(sys_cmd)
    else:
        print("ERROR : SYSTEM file not found")

if args.dir:
    if args.keyword:
        combine_keyword(args.dir, args.comb, args.keyword, args.df)
        print("SYSTEM : Keyword successfully filtered")
    else:
        combine_files(args.dir, args.comb, args.df)
        print("SYSTEM : Successfully combined files")