#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import argparse

# Parse command line arguments
def parse_args():
    parser = argparse.ArgumentParser(description='Rename a file to a shorter name')
    parser.add_argument('-i', '--input', type=str, required=True, help='Input file path. required.')
    parser.add_argument('-o', '--output', type=str, default=None, help='Output file path. If not provided, the input file will be renamed in place.')
    parser.add_argument('-m', '--map', type=str, default=None, help='Mapping file for renaming. If provided, it should contain old and new names.')
    
    return parser.parse_args()

# input check
def input_check(args):
    ### input file
    if not os.path.exists(args.input):
        print(f'Error: {args.input} does not exist.')
        exit(1)
    with open(args.input, 'r') as f:
        input_lines = f.readlines()
    
    ### output file
    if args.output is None:
        args.output = os.path.splitext(os.path.basename(args.input))[0] + '_renamed.pdb'
    
    ### mapping file
    rename_map = {}
    if args.map is not None:
        if not os.path.exists(args.map):
            print(f'Error: {args.map} does not exist.')
            exit(1)
        with open(args.map, 'r') as f:
            for line in f:
                old_name, new_name = line.strip().split()
                rename_map[old_name] = new_name
    
    return input_lines, args.output, rename_map

# main
def main():
    input_args = parse_args()
    input_lines, output_file, rename_map = input_check(input_args)
    
    # Rename lines
    # if the atom name is in the rename_map, rename it accordingly
    # if the atom name is 4 characters long, use first 3 characters for its atom name
    renamed_lines = []
    for line in input_lines:
        if line.startswith(('ATOM', 'HETATM')):
            atom_name = line[12:16].strip()
            if atom_name in rename_map:
                new_atom_name = rename_map[atom_name]
            if len(atom_name) > 3:
                new_atom_name = atom_name[:3]
            else:
                new_atom_name = atom_name
            renamed_line = line[:12] + f' {new_atom_name:<3}' + line[16:]
            renamed_lines.append(renamed_line)
        else:
            renamed_lines.append(line)
    
    # Write to output file
    with open(output_file, 'w') as f:
        f.writelines(renamed_lines)

if __name__ == '__main__':
    main()
