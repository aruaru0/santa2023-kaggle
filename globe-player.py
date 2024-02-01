#!/usr/bin/env python3

import argparse
import ast
import fileinput
import re
import sys

puzzle_info = {}
puzzles_by_id = {}
played_moves = []
globe_dims = {
    'globe_1/8': (2, 16),
    'globe_1/16': (2, 32),
    'globe_2/6': (3, 12),
    'globe_3/4': (4, 8),
    'globe_6/4': (7, 8),
    'globe_6/8': (7, 16),
    'globe_6/10': (7, 20),
    'globe_3/33': (4, 66),
    'globe_8/25': (9, 50)
}

def load_puzzle_info():
    first = True
    for line in fileinput.input(files=('./data/puzzle_info.csv')):
        if not first:
            match = re.match('([^,]+),\"(.*)\"', line)
            puzzle, mvs = match.groups()
            puzzle_info[puzzle] = ast.literal_eval(mvs)
        first = False
    init_reverse_moves(puzzle_info)

def init_reverse_moves(puzzle_info):
    for k in list(puzzle_info.keys()):
        moves = puzzle_info[k]
        new_moves = {}
    
        for m in moves.keys():
            new_moves[m] = moves[m]
            xform = moves[m]
            m_inv = '-' + m
            xform_inv = len(xform) * [0]
            for i in range(len(xform)):
                xform_inv[xform[i]] = i
            new_moves[m_inv] = xform_inv

        puzzle_info[k] = new_moves

def load_puzzles():
    first = True
    for line in fileinput.input(files=('./data/puzzles.csv')):

        # Skip the header.
        if first:
            first = False
            continue

        id, type, solution, initial_state, wc = line.rstrip().split(',')
        puzzles_by_id[id] = {
            'type': type,
            'solution': solution,
            'initial_state': initial_state,
            'wildcards': wc
        }

def apply_move(move, state, moves=None):

    m = move
    s = state.split(';')

    move_list = moves[m]
    new_state = []
    for i in move_list:
        new_state.append(s[i])
    s = new_state

    return ';'.join(s)

def reverse_move(move, state, moves=None):
    m = move[1:] if move[0] == '-' else '-' + move
    return apply_move(m, state, moves=moves)

def display_globe(state, type='globe_3/33'):
    tiles = state.split(';')
    rows, cols = globe_dims[type]
    for j in range(cols):
        print(("    " + str(j))[-4:], end='')
    print()
    for i in range(rows):
        for j in range(cols):
            print(("    " + tiles[i*cols + j])[-4:], end='')
        print()

def display_moves(type='globe_1/8'):
    moves = [k for k in puzzle_info[type].keys() if k[0] != '-']
    print(','.join(moves))

def display_game_state(id, state, type='globe_1/8'):

    print()
    print('Solution:')
    display_globe(puzzles_by_id[id]['solution'], type=type)
    print()

    print('Current State:')
    display_globe(state, type=type)
    print()

    print('Available Moves:')
    display_moves(type=type)
    print()

    print('Played Moves:')
    print('.'.join(played_moves))
    print()

def display_globe2(state, type='globe_1/8'):
    tiles = state.split(';')
    rows, cols = globe_dims[type]
    for j in range(cols):
        print(("    " + str(j))[-4:], end='')
    print()

    for i in range(rows):
        for j in range(cols):
            print(("    " + tiles[i*cols + j])[-4:], end='')
        print()

parser = argparse.ArgumentParser()
parser.add_argument('id')
args = parser.parse_args()

load_puzzle_info()
load_puzzles()

puzzle = puzzles_by_id[args.id]
if not puzzle['type'].startswith('globe'):
    print('globe_player.py: error: puzzle ' + args.id + ' is not a globe.')
    exit(1)

state = puzzle['initial_state']
# state = "N0;N1;N2;N3;N4;N5;N6;N7;N8;N9;N10;N11;N12;N13;N14;N15;N16;N17;N18;N19;N20;N21;N22;N23;N24;N25;N26;N27;N28;A;C;B"
# #                                                                                              1 1 1 1 1 1 1 1 1  
# #                                                                        0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9
# state = "A;A;A;A;A;A;C;C;C;C;C;C;E;E;E;E;E;E;G;G;G;G;G;G;I;I;I;I;I;I;K;K;K;K;K;K;M;M;M;M;M;M;O;O;O;O;O;O;Q;Q;Q;Q;Q;Q;S;S;S;S;S;S;U;U;U;U;U;U;A;A;A;A;A;A;C;C;C;C;C;C;E;E;E;E;E;E;G;G;G;G;G;G;I;I;I;I;I;I;K;K;K;K;K;K;M;M;M;M;M;M;O;O;O;O;O;O;Q;Q;Q;Q;Q;Q;S;S;S;S;S;S;U;U;U;U;U;U;B;B;B;B;B;B;D;D;D;D;D;D;F;F;F;F;F;F;H;H;H;H;H;H;J;J;J;J;J;J;L;L;L;L;L;L;N;N;N;N;N;N;P;P;P;P;P;P;R;R;R;R;R;R;T;T;T;T;T;T;V;V;V;V;V;V;x;x;x;x;x;x;x;x;x;x;x;x;x;x;x;B;x;x;x;x;x;x;x;x;x;x;x;x;x;x;x;x;x;x;x;x;x;x;x;x;x;x;x;x;x;x;x;x;x;x;x;x;x;x;x;x;x;x;x;x;x;x;x;x;A;B"
state = "N0;N1;N2;N3;N4;N5;N6;N7;N8;N9;N10;N11;N12;N13;N14;N15;N16;N17;N18;N19;N20;N21;N22;N23;N24;N25;N26;N27;N28;N29;N30;N31;N32;N33;N34;N35;N36;N37;N38;N39;N40;N41;N42;N43;N44;N45;N46;N47;N48;N49;N50;N51;N52;N53;.;.;.;.;.;.;.;.;.;X"

while True:
    display_game_state(args.id, state, puzzle['type'])
    print('> ', end='')
    sys.stdout.flush()
    command = sys.stdin.readline().rstrip()
    if command == "":
        state = reverse_move(played_moves.pop(), state, moves=puzzle_info[puzzle['type']])
    elif command == 'exit':
        break
    else :
        for e in command.split(" ") :
            v = e.split("_")
            n = 1
            if len(v) != 1 :
                n = int(v[1])
            for i in range(n) :
                if v[0] in puzzle_info[puzzle['type']].keys():
                    state = apply_move(v[0], state, moves=puzzle_info[puzzle['type']])
                    print("MOVE =", v[0], ":")
                    display_globe2(state, puzzle['type'])
            played_moves.append(e)

