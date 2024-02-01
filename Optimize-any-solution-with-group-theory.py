from collections import Counter
import itertools
from ast import literal_eval
from pathlib import Path
from pprint import pprint

import numpy as np
import pandas as pd
from sympy.combinatorics import Permutation
import matplotlib.pyplot as plt
from tqdm import tqdm

data_dir = Path("./data")

puzzle_info = pd.read_csv(data_dir / 'puzzle_info.csv', index_col='puzzle_type')
# Parse allowed_moves
puzzle_info['allowed_moves'] = puzzle_info['allowed_moves'].apply(literal_eval)

puzzles = pd.read_csv(data_dir / 'puzzles.csv', index_col='id')
# Parse color states
puzzles = puzzles.assign(
    initial_state=lambda df: df['initial_state'].str.split(';'),
    solution_state=lambda df: df['solution_state'].str.split(';')
)

sample_submission = pd.read_csv(data_dir / 'sample_submission.csv', index_col='id')
top_submission = pd.read_csv(
    'submission_330721.csv',
    index_col=0
)

def apply_sequence(sequence, moves, state):
    """Apply a sequence of moves in array form to a color state."""
    state = np.asarray(state)
    for m in sequence.split('.'):
        state = state[moves[m]]
    return state


# Convert allowed_moves to dict and add inverse moves
all_moves = puzzle_info.loc[:, 'allowed_moves'].to_dict()
for ptype, moves in all_moves.copy().items():
    for m, arr in moves.copy().items():
        all_moves[ptype][f"-{m}"] = np.argsort(arr).tolist()

def find_cube_inverse_move(move):
    if move[:2] == '--':
        return move
    elif move[0] == '-':
        return move [1:]
    else:
        return f'-{move}'

    
def is_same_group(move1, move2):
    """
    Check if two Rubik's cube moves belong to the same group (move the same side).

    Args:
        move1 (str): The first move.
        move2 (str): The second move.

    Returns:
        bool: True if moves belong to the same group, False otherwise.
    """
    return move1.lstrip('-')[0] == move2.lstrip('-')[0]


def group_cube_moves(moves):
    """
    Group Rubik's cube moves by side.

    Args:
        moves (list): A list of strings representing Rubik's cube moves.

    Returns:
        list: A list of lists, where each sublist contains consecutive moves of the same side.
    """
    grouped_moves = []
    current_group = []

    for move in moves:
        if not current_group or is_same_group(move, current_group[-1]):
            current_group.append(move)
        else:
            grouped_moves.append(current_group)
            current_group = [move]

    if current_group:
        grouped_moves.append(current_group)

    return grouped_moves

assert group_cube_moves(
    ['r1', 'r0', '-r1', '-r0', 'r0', 'f1', 'r0', '-f1', 'f1', 'f0']
) == [['r1', 'r0', '-r1', '-r0', 'r0'], ['f1'], ['r0'], ['-f1', 'f1', 'f0']]
assert group_cube_moves(['r1']) == [['r1']]
assert group_cube_moves(['r1', 'f1']) == [['r1'], ['f1']]
assert group_cube_moves(['r1', 'r0', 'f1']) == [['r1', 'r0'], ['f1']]


def remove_multiples_of_four(group):
    """
    Process a group of elements according to the specified algorithm.

    Args:
        group (list): A list of elements.

    Returns:
        list: A new list with elements repeated according to their modulo 4 count.
    """
    if len(group) < 4:
        return group
    
    # Step 1: Calculate the number of elements
    element_counts = Counter(group)

    # Step 2: Take modulo 4 for each count
    for element in element_counts:
        element_counts[element] %= 4

    # Step 3: Create a new list with the remaining counts
    new_group = []
    for element, count in element_counts.items():
        new_group.extend([element] * count)

    return new_group

assert sorted(remove_multiples_of_four(['r1', 'r1', 'r1', 'r1', 'r1', 'r0', 'r1'])) == ['r0', 'r1', 'r1']
assert remove_multiples_of_four(['r1', 'r1', 'r1', 'r1']) == []
assert remove_multiples_of_four(['r1', 'r1', 'r1']) == ['r1', 'r1', 'r1']
assert sorted(remove_multiples_of_four(['r1', 'r1', 'r1', 'r1', 'r1', 'r0', 'r1', 'r0', 'r0', 'r0'])) == ['r1', 'r1']
assert remove_multiples_of_four(['r1', 'r1', 'r1', 'r1', 'r0', 'r1', 'r1', 'r1', 'r1']) == ['r0']
assert sorted(remove_multiples_of_four(['r1', 'r1', 'r1', 'r1', 'r0', 'r1', 'r1', 'r1', 'r1', 'r1'])) == ['r0', 'r1']


def remove_cancelling_pairs(group):
    """
    Remove an element and its inverse from a group of Rubik's cube moves efficiently.

    Args:
        group (list): A list of strings representing a group of Rubik's cube moves.

    Returns:
        list: A list with paired elements and their inverses removed based on counts.
    """
    if len(group) < 2:
        return group
    
    move_counts = Counter(group)

    # Adjust counts for each move and its inverse
    for move, count in list(move_counts.items()):
        inv = find_cube_inverse_move(move)
        if inv in move_counts:
            min_count = min(move_counts[move], move_counts[inv])
            move_counts[move] -= min_count
            move_counts[inv] -= min_count

    # Construct the final list based on adjusted counts
    final_group = []
    for move, count in move_counts.items():
        final_group.extend([move] * count)

    return final_group

assert remove_cancelling_pairs(['r1', 'r0', '-r1']) == ['r0']
assert remove_cancelling_pairs(['-r1', 'r1', 'r1']) == ['r1']
assert remove_cancelling_pairs(['r1', 'r0', 'r1', '-r1', '-r1']) == ['r0']
assert remove_cancelling_pairs(['r1', 'r0', 'r1', '-r1', '-r1', '-r0']) == []
assert remove_cancelling_pairs(['r1', 'r0', 'r1', '-r1', '-r1', '-r0', 'r0']) == ['r0']
assert remove_cancelling_pairs(['r1']) == ['r1']
assert remove_cancelling_pairs(['r1', 'r1']) == ['r1', 'r1']


def substitute_three_for_inverse(group):
    """
    Substitute every three occurrences of an element with one occurrence of its inverse.

    Args:
        group (list): A list of strings representing a group of Rubik's cube moves.

    Returns:
        list: A list with every three occurrences of an element substituted with its inverse.
    """
    
    if len(group) < 3:
        return group

    move_counts = Counter(group)

    new_group = []
    for move, count in move_counts.items():
        inverse_count = count // 3
        remainder_count = count % 3
        new_group.extend([find_cube_inverse_move(move)] * inverse_count)
        new_group.extend([move] * remainder_count)

    return new_group

# Test cases
assert substitute_three_for_inverse(['r1', 'r1', 'r1']) == ['-r1']
assert sorted(substitute_three_for_inverse(['r1', 'r0', 'r1'])) == ['r0', 'r1', 'r1']
assert sorted(substitute_three_for_inverse(['r1', 'r0', 'r1', 'r1'])) == ['-r1', 'r0']
assert sorted(substitute_three_for_inverse(['r1', 'r0', 'r1', 'r1', 'r0', 'r0'])) == ['-r0', '-r1']
assert sorted(substitute_three_for_inverse(['r1', 'r0', 'r1', 'r1', 'r0', 'r0', 'r1'])) == ['-r0', '-r1', 'r1']
assert substitute_three_for_inverse(['r1']) == ['r1']
assert substitute_three_for_inverse(['r1', 'r1']) == ['r1', 'r1']

def groups_to_solution(groups: list):
    """Convert list of lists of moves to one list"""
    return list(itertools.chain.from_iterable(groups))


def regroup(groups):
    """Merge groups to a list of moves, then split to groups again to remove empty groups"""
    moves = groups_to_solution(groups)
    # print("Moves:", len(moves))
    return group_cube_moves(moves)


def optimize_solution(moves, puzzle="cube"):
    """Apply optimizations while length of moves is decreasing"""
    
    groups = group_cube_moves(moves)
    previous_length = len(moves)
    keep_optimizing = True
    
    while keep_optimizing:
        if puzzle == "cube":
            # First try to remove as many meaningless moves as possible
            # print("Removing 4s")
            groups = [remove_multiples_of_four(group) for group in groups]
            groups = regroup(groups)  # If some groups became empty, other groups can appear so we need to regroup
        
        if puzzle in ("cube", "wreath"):
            # Try to remove more elements by throwing out cancellations
            # print("Removing pairs")
            groups = [remove_cancelling_pairs(group) for group in groups]
            groups = regroup(groups)
        
        if puzzle == "cube":
            # Finally, try to reduce length a bit by substituting triplets. It will not require regrouping
            # print("Substituting triplets")
            groups = [substitute_three_for_inverse(group) for group in groups]
            moves = groups_to_solution(groups)

        keep_optimizing = (len(moves) != previous_length)
        previous_length = len(moves)
        # print("Moves:", len(moves))
        
    return moves


def get_full_face_rotations_substitutions(allowed_moves: dict, cube_size: int, initial_state):

    faces = ("f", "r", "d")

    rotation_template = ".".join("{face}" + str(i) for i in range(cube_size)) + ".{move}." + ".".join("-{face}" + str(i) for i in range(cube_size))
    # '{face}0.{face}1.{face}2.{move}.-{face}0.-{face}1.-{face}2'

    single_move_states = {}

    for move in allowed_moves.keys():
        state = tuple(apply_sequence(move, allowed_moves, state=initial_state))    
        single_move_states[state] = move

    rotated_states = {}  # From state to moves

    # dict from face type to dict of moves substitution
    # i.e., if, we rotate the whole "d" face, how each move corresponds to new moves
    rotated_face_to_moves = {}

    for face in faces:
        rotated_face_to_moves[face] = {}
        rotated_face_to_moves[f"-{face}"] = {}

        for move in allowed_moves.keys():
            composition = rotation_template.format(face=face, move=move)
            state = tuple(apply_sequence(composition, allowed_moves, state=initial_state))
            rotated_states[state] = composition

        for state, composition in rotated_states.items():
            # Find element in the middle of composition
            old_move = composition.split(".")[cube_size]
            new_move = single_move_states[state]

            rotated_face_to_moves[face][old_move] = new_move
            rotated_face_to_moves[f"-{face}"][new_move] = old_move 
    
    return rotated_face_to_moves


def get_group_type(group: list):
    first_elem = group[0]
    
    if first_elem[0] == "-":
        return first_elem[:2]

    return first_elem[0]
    

def substitute_face_rotation(group, cube_size):

    elements_counts = Counter(group)
    
#     print("elements_counts", elements_counts)

    group_type = get_group_type(group)

    n_face_rotations = 0
    n_inv_face_rotations = 0

    for i in range(cube_size):
        if f"{group_type}{i}" in elements_counts:
            n_face_rotations += 1
        if f"-{group_type}{i}" in elements_counts:
            n_inv_face_rotations += 1

    is_group_changed = (n_face_rotations > cube_size // 2) or (n_inv_face_rotations > cube_size // 2)

    if not is_group_changed:
        return None

    for i in range(cube_size):
        move = f"{group_type}{i}"
        if move in elements_counts:
            # Remove move as it is meaningless
            elements_counts[move] -= 1
        else:
            # Add move in the opposite direction
            elements_counts[find_cube_inverse_move(move)] += 1

#     print("n_face_rotations", n_face_rotations)
#     print("n_inv_face_rotations", n_inv_face_rotations)

    new_group = []
    for element, count in elements_counts.items():
        new_group.extend([element] * count)
        
#     print("elements_counts", elements_counts)
#     print("new_group", new_group)
        
    return new_group

assert substitute_face_rotation(["f0", "f1"], cube_size=5) is None
assert substitute_face_rotation(["f0", "f1"], cube_size=3) == ["-f2"]
assert substitute_face_rotation(["-f0", "-f1"], cube_size=3) == ["f2"]


def substitute_full_cube_rotations(solution, rotated_face_to_moves):
    groups = group_cube_moves(solution)

    full_cube_rotations = []

    for i, group in enumerate(groups):
        updated_group = substitute_face_rotation(group, cube_size)

        if updated_group is None:
            continue

        group_type = get_group_type(group)
        full_cube_rotations.append(group_type)

        # Update all the following groups
        groups[i] = updated_group

        for j in range(i + 1, len(groups)):
#             print("Old group:", groups[j])
            for move_idx in range(len(groups[j])):
                groups[j][move_idx] = rotated_face_to_moves[group_type][groups[j][move_idx]]

#             print("New group:", groups[j])

    new_solution = list(itertools.chain.from_iterable(groups))
    return new_solution, full_cube_rotations


def face_rotations_to_moves(rotated_faces, cube_size):
    moves = []
    
    for face in rotated_faces:
        moves.extend(f"{face}{i}" for i in range(cube_size))
        
    return moves


def apply_face_rotations(rotations, allowed_moves, state, cube_size):
    side_moves = face_rotations_to_moves(rotations, cube_size)
    
    return apply_sequence(".".join(side_moves), allowed_moves, state)


def all_combinations(iterable, max_combinations=3):
    s = list(iterable)  # allows duplicate elements
    return list(
        itertools.chain.from_iterable(
            itertools.combinations(s, r) for r in range(1, max_combinations + 1)
        )
    )


class RotationError(ValueError):
    pass

def optimize_full_cube_rotations(solution_moves, allowed_moves, rotated_face_to_moves, initial_state, solution_state, cube_size):
    updated_solution_moves, full_cube_rotations = substitute_full_cube_rotations(solution_moves, rotated_face_to_moves)

    optimized_solution = updated_solution_moves # + inverse_rotation_moves

    final_state = apply_sequence(".".join(optimized_solution), allowed_moves, initial_state)

    if not np.equal(final_state, solution_state).all():
        # I tried to inverse it smarter, but gave up
        all_possible_rotations = all_combinations(("f", "d", "r", "-f", "-d", "-r"))

        for rotation in all_possible_rotations:
            rotation_moves = face_rotations_to_moves(rotation, cube_size)
            new_state = apply_sequence(".".join(rotation_moves), allowed_moves, final_state)
            if np.equal(new_state, solution_state).all():
                optimized_solution += list(rotation_moves)
                break
        else:
            raise RotationError("Didn't find optimal rotation")
            
    return optimized_solution

def valid_check(state, target, num_wild) :
    cnt = 0
    for x, y in zip(state, target):
        if x != y : cnt+=1
    if cnt <= num_wild:
        return True
    return False


solutions = []
old_lengths = []
new_lengths = []

import sys

if len(sys.argv) != 2:
    print("input file name")
    exit(0)

sol = sys.argv[1]

print(sol)


for puzzle_idx in range(puzzles.shape[0]):
    puzzle_name = puzzles.loc[puzzle_idx, 'puzzle_type']
    puzzle_type = puzzle_name[:puzzle_name.find("_")]
    solution_state = puzzles.iloc[puzzle_idx, 1]
    initial_state = puzzles.iloc[puzzle_idx, 2]
    num_wild = puzzles.iloc[puzzle_idx, 3]
    
    top_solution = top_submission.loc[puzzle_idx, 'moves']


    solution_moves = top_solution.split('.')

    with open(f"{sol}/{puzzle_idx}.txt", "r") as f :
        solution_moves = f.read().split(".")
    
    if puzzle_type == "cube":
        cube_size = int(puzzle_name.split("/")[-1])
        allowed_moves = all_moves[puzzle_name]

        rotated_face_to_moves = get_full_face_rotations_substitutions(allowed_moves, cube_size, initial_state)
        
        old_length = len(solution_moves)
        new_length = 0
        new_solution = solution_moves.copy()
        
        while new_length < old_length:
            old_length = len(new_solution)
            try:
                new_solution = optimize_full_cube_rotations(
                    solution_moves=new_solution,
                    allowed_moves=allowed_moves,
                    rotated_face_to_moves=rotated_face_to_moves,
                    initial_state=initial_state,
                    solution_state=solution_state,
                    cube_size=cube_size
                )
            except RotationError:
                print("Failed to optimize rotations for puzzle #", puzzle_idx)
        
            new_solution = optimize_solution(new_solution, puzzle_type)
            new_length = len(new_solution)
        
    else:
        new_solution = optimize_solution(solution_moves, puzzle_type)
        
    if len(solution_moves) <= len(new_solution):
        # We did not improve
        new_solution = solution_moves

    solutions.append(new_solution)
    old_lengths.append(len(solution_moves))
    new_lengths.append(len(new_solution))
    
    if len(solution_moves) != len(new_solution):
        state = apply_sequence(".".join(new_solution), all_moves[puzzle_name], initial_state)
#         is_correct = np.array_equal(state, solution_state)
        is_correct = valid_check(state, solution_state, num_wild) 
        print(puzzle_type, puzzle_idx, "Solution is correct:", is_correct, "; diff:", new_lengths[-1] - old_lengths[-1])
        
        if is_correct :
            # print(puzzle_idx, ".".join(new_solution))
            with open(f"{sol}/{puzzle_idx}.txt", "w") as f :
                f.write(".".join(new_solution))     
        if not is_correct:
            solutions.pop()
            solutions.append(solution_moves)
    
#    print(len(solution), len(new_solution))
#    print()