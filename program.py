import subprocess
import os
import argparse
import pandas as pd

FILE_HEADERS = {
    'appcompat.csv': 'LastModifiedTimeUTC',
    'evtx.csv': 'TimeCreated',
    'pecmd_Timeline.csv': 'RunTime',
    'pecmd.csv': 'LastRun',
}

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

def normalize_timestamps(df, date_column):
    if date_column in df.columns:
        df[date_column] = pd.to_datetime(df[date_column], errors='coerce', utc=True)
        df.dropna(subset=[date_column], inplace=True)
        df.sort_values(by=[date_column], inplace=True)
    return df

def arrange_files(directory):
    for file_name, date_column in FILE_HEADERS.items():
        file_path = os.path.join(directory, file_name)
        
        if os.path.exists(file_path):
            try:
                df = pd.read_csv(file_path, on_bad_lines='skip', engine='python')
                
                if date_column in df.columns:
                    df = normalize_timestamps(df, date_column)
                    df.to_csv(file_path, index=False, encoding='utf-8')
                    print(f"SYSTEM: Processed and sorted {file_name} by {date_column}.")
                else:
                    print(f"WARNING: {date_column} column not found in {file_name}. Skipping normalization.")
            except Exception as e:
                print(f"ERROR: Failed to process {file_name}: {str(e)}")
        else:
            print(f"WARNING: {file_name} not found in directory.")

def combine_and_sort_timeline(directory, output_file):
    files = get_csv_files(directory)
    if not files:
        print("ERROR: No CSV files found.")
        return
    
    all_dfs = []
    
    for file in files:
        file_name = os.path.basename(file)
        date_column = FILE_HEADERS.get(file_name)

        df = pd.read_csv(file, on_bad_lines='skip', engine='python')
        df.insert(0, 'SourceCSV', file_name)

        if date_column and date_column in df.columns:
            df = normalize_timestamps(df, date_column)
            df.rename(columns={date_column: 'NormalizedTimestamp'}, inplace=True)
            all_dfs.append(df)

    if not all_dfs:
        print("ERROR: No valid data to merge.")
        return
    
    final_df = pd.concat(all_dfs, ignore_index=True)
    final_df.sort_values(by=['NormalizedTimestamp'], inplace=True)
    
    output_path = os.path.join(directory, output_file)
    final_df.to_csv(output_path, index=False, encoding='utf-8')
    
    print(f"SYSTEM: Successfully created {output_file}")
        
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

parser.add_argument('-timeline', type=str, help='Path to output timeline directory')

# Filename
parser.add_argument('-comb', type=str, default="combined_output.csv", help='Filename for combined output CSV')

args = parser.parse_args()

if args.d:
    if not args.timeline:
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
elif args.keyword and not args.dir:
    print("ERROR : Provide a directory containing CSV files to combine.")

if args.d and args.timeline:
    # Ensure output directory exists
    ensure_directory_exists(args.timeline)
    
    # Extract Evtx and PECmd data
    evtx_cmd = [evtxPath, '-d', args.d, '--csv', args.timeline, '--csvf', "evtx.csv"]
    pec_cmd = [pecmdPath, '-d', args.d, '--csv', args.timeline, '--csvf', "pecmd.csv"]
    
    subprocess.run(evtx_cmd)
    subprocess.run(pec_cmd)

    # Process AppCompatCacheParser if SYSTEM file is found
    sys_dir = find_sys(args.d)
    if sys_dir:
        appcompat_cmd = [appcompatPath, '-f', sys_dir, '--csv', args.timeline, '--csvf', "appcompat.csv"]
        subprocess.run(appcompat_cmd)
    else:
        print("WARNING: SYSTEM file not found. Skipping AppCompatCacheParser.")

    # Normalize timestamps and create timeline
    arrange_files(args.timeline)
    combine_and_sort_timeline(args.timeline, 'Final_Timeline.csv')

else:
    print("ERROR: Provide both -d and -timeline arguments.")