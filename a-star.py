# A-starアルゴリズムの実装

import pandas as pd

# File paths
puzzle_info_path = './data/puzzle_info.csv'
puzzles_path = './data/puzzles.csv'
sample_submission_path = './data/sample_submission.csv'

# Loading the data
puzzle_info_df = pd.read_csv(puzzle_info_path)
puzzles_df = pd.read_csv(puzzles_path)
sample_submission_df = pd.read_csv(sample_submission_path)

# Displaying the first few rows of each dataframe
print(puzzle_info_df.head())


#---
# Parsing the initial_state and solution_state columns
# Converting the semicolon-separated string values into lists of colors
puzzles_df['parsed_initial_state'] = puzzles_df['initial_state'].apply(lambda x: x.split(';'))
puzzles_df['parsed_solution_state'] = puzzles_df['solution_state'].apply(lambda x: x.split(';'))

# Displaying the modified dataframe with parsed states
print(puzzles_df[['id', 'puzzle_type', 'parsed_initial_state', 'parsed_solution_state']].head())

#---
import json

# Converting the string representation of allowed_moves to dictionary
puzzle_info_df['allowed_moves'] = puzzle_info_df['allowed_moves'].apply(lambda x: json.loads(x.replace("'", '"')))

# Selecting an example puzzle type and displaying its allowed moves
example_puzzle_type = puzzle_info_df['puzzle_type'].iloc[0]
example_allowed_moves = puzzle_info_df[puzzle_info_df['puzzle_type'] == example_puzzle_type]['allowed_moves'].iloc[0]

print(example_puzzle_type)

#---
def apply_move(state, move, inverse=False):
    """
    Apply a move or its inverse to the puzzle state.

    :param state: List of colors representing the current state of the puzzle.
    :param move: List representing the move as a permutation.
    :param inverse: Boolean indicating whether to apply the inverse of the move.
    :return: New state of the puzzle after applying the move.
    """
    if inverse:
        # Creating a dictionary to map the original positions to the new positions
        inverse_move = {v: k for k, v in enumerate(move)}
        return [state[inverse_move[i]] for i in range(len(state))]
    else:
        return [state[i] for i in move]

# Testing the function with an example move from the 'cube_2/2/2' puzzle
test_state = puzzles_df['parsed_initial_state'].iloc[0]
test_move = example_allowed_moves['f1']

# Applying the move and its inverse to the test state
applied_state = apply_move(test_state, test_move)
reverted_state = apply_move(applied_state, test_move, inverse=True)

print(pd.DataFrame(test_state).T)

#---
import heapq

def heuristic(state, goal_state):
    """
    Heuristic function estimating the cost from the current state to the goal state.
    Here, we use the number of mismatched colors between the current state and the goal state.
    """
    return sum(s != g for s, g in zip(state, goal_state))

import time

def a_star_search_with_timeout(initial_state, goal_state, allowed_moves, timeout=300):
    """
    A* search algorithm with a timeout feature.

    :param initial_state: The starting state of the puzzle.
    :param goal_state: The target state to reach.
    :param allowed_moves: A dictionary of moves that can be applied to the state.
    :param timeout: The maximum time (in seconds) allowed for the search.
    :return: The shortest sequence of moves to solve the puzzle, or None if unsolved within timeout.
    """
    start_time = time.time()
    open_set = []  # Priority queue for states to explore
    heapq.heappush(open_set, (0, initial_state, []))  # Each entry: (priority, state, path taken)

    closed_set = set()  # Set to keep track of already explored states

    while open_set:
        if time.time() - start_time > timeout:
            return None  # Timeout check

        _, current_state, path = heapq.heappop(open_set)

        if current_state == goal_state:
            return path  # Goal state reached

        state_tuple = tuple(current_state)
        if state_tuple in closed_set:
            continue  # Skip already explored states

        closed_set.add(state_tuple)

        for move_name, move in allowed_moves.items():
            for inverse in [False, True]:  # Consider both move and its inverse
                new_state = apply_move(current_state, move, inverse)
                new_state_tuple = tuple(new_state)
                if new_state_tuple not in closed_set:
                    priority = len(path) + 1 + heuristic(new_state, goal_state)
                    heapq.heappush(open_set, (priority, new_state, path + [(move_name, inverse)]))

# Testing the A* search algorithm with an example
test_initial_state = puzzles_df['parsed_initial_state'].iloc[0]
test_goal_state = puzzles_df['parsed_solution_state'].iloc[0]
test_allowed_moves = example_allowed_moves

# Running the A* search to find a solution
a_star_solution = a_star_search_with_timeout(test_initial_state, test_goal_state, test_allowed_moves)
print(a_star_solution)  # Display the solution moves (if found)

#----
# Modifying the A* search algorithm to improve efficiency
def improved_heuristic_with_wildcards(state, goal_state, num_wildcards):
    """
    Improved heuristic function considering wildcards.
    """
    mismatches = sum(s != g for s, g in zip(state, goal_state))
    return max(0, mismatches - num_wildcards)

def improved_a_star_search_with_wildcards(initial_state, goal_state, allowed_moves, num_wildcards, max_depth=30, timeout=100):
    """
    Improved A* search algorithm with wildcards, depth limit, and timeout.

    :param initial_state: List representing the initial state of the puzzle.
    :param goal_state: List representing the goal state of the puzzle.
    :param allowed_moves: Dictionary of allowed moves and their corresponding permutations.
    :param num_wildcards: Number of wildcards allowed for the puzzle.
    :param max_depth: Maximum depth to search to limit the search space.
    :param timeout: Time limit in seconds for the search.
    :return: Shortest sequence of moves to solve the puzzle, or None if no solution is found.
    """
    start_time = time.time()
    open_set = []
    heapq.heappush(open_set, (0, initial_state, [], num_wildcards))  # (priority, state, path, remaining wildcards)
    closed_set = set()

    while open_set:
        if time.time() - start_time > timeout:
            return None  # Timeout

        _, current_state, path, remaining_wildcards = heapq.heappop(open_set)

        if len(path) > max_depth:  # Depth limit
            continue

        if current_state == goal_state or improved_heuristic_with_wildcards(current_state, goal_state, remaining_wildcards) == 0:
            return path

        closed_set.add((tuple(current_state), remaining_wildcards))

        for move_name, move in allowed_moves.items():
            for inverse in [False, True]:
                new_state = apply_move(current_state, move, inverse)
                if (tuple(new_state), remaining_wildcards) not in closed_set:
                    priority = len(path) + 1 + improved_heuristic_with_wildcards(new_state, goal_state, remaining_wildcards)
                    heapq.heappush(open_set, (priority, new_state, path + [(move_name, inverse)], remaining_wildcards))

    return None  # No solution found

# Running the improved A* search to find a solution
test_num_wildcards = puzzles_df['num_wildcards'].iloc[0]
improved_a_star_solution = improved_a_star_search_with_wildcards(test_initial_state, test_goal_state, test_allowed_moves, test_num_wildcards)
print(improved_a_star_solution)  # Display the solution moves (if found)

#---
def format_solution_for_submission(puzzle_id, solution_moves):
    """
    Format the solution to a puzzle for submission.

    :param puzzle_id: The unique identifier of the puzzle.
    :param solution_moves: List of tuples representing the solution moves.
    :return: Formatted string suitable for submission.
    """
    formatted_moves = []
    for move, inverse in solution_moves:
        move_str = '-' + move if inverse else move
        formatted_moves.append(move_str)

    # Joining the moves into a single string separated by periods
    return {'id': puzzle_id, 'moves': '.'.join(formatted_moves)}

# Example: Formatting the solution for the first puzzle in the dataframe for submission
puzzle_id_example = puzzles_df['id'].iloc[0]
formatted_solution = format_solution_for_submission(puzzle_id_example, a_star_solution)
print(formatted_solution)

#---
from tqdm import tqdm

def solve_puzzles(puzzles_df, puzzle_info_df, sample_submission_df, num_puzzles=None, limit_index=30):
    """
    Solve a set of puzzles using the A* search algorithm.

    :param puzzles_df: DataFrame containing puzzles.
    :param puzzle_info_df: DataFrame containing allowed moves for each puzzle type.
    :param sample_submission_df: DataFrame containing sample submission format.
    :param num_puzzles: Number of puzzles to solve (if None, solve all).
    :return: DataFrame with the solutions formatted for submission.
    """
    solutions = []

    print("=="*80)
    print(puzzles_df)
    # Limit the number of puzzles if specified
    puzzles_to_solve = puzzles_df if num_puzzles is None else puzzles_df.head(num_puzzles)

    for index, row in tqdm(puzzles_to_solve.iterrows(), total=puzzles_to_solve.shape[0], desc="Solving Puzzles"):
        puzzle_id = row['id']
        initial_state = row['parsed_initial_state']
        goal_state = row['parsed_solution_state']
        puzzle_type = row['puzzle_type']
        num_wildcards = row['num_wildcards']
        allowed_moves = puzzle_info_df[puzzle_info_df['puzzle_type'] == puzzle_type]['allowed_moves'].iloc[0]
        
        solution_moves = None
        
        # Attempt to find a solution
        if index < limit_index:
            solution_moves = improved_a_star_search_with_wildcards(initial_state, goal_state, allowed_moves, num_wildcards, timeout=100)

        # If no solution found, use the sample submission's result
        if solution_moves is None:
            solution_moves = sample_submission_df[sample_submission_df['id'] == puzzle_id]['moves'].iloc[0].split('.')
            solution_moves = [(move.replace('-', ''), move.startswith('-')) for move in solution_moves]
        else :
            sample_solution_moves = sample_submission_df[sample_submission_df['id'] == puzzle_id]['moves'].iloc[0].split('.')
            sample_solution_moves = [(move.replace('-', ''), move.startswith('-')) for move in sample_solution_moves]
            tqdm.write(f"{puzzle_id} : {len(solution_moves)}, {len(sample_solution_moves)}")

        formatted_solution = format_solution_for_submission(puzzle_id, solution_moves)
        if solution_moves is not None:
            with open(f"sol_astar/{formatted_solution['id']}.txt", "w") as fp:
                fp.write(formatted_solution['moves'])

        solutions.append(formatted_solution)

    return pd.DataFrame(solutions)

# Solving the first 3 puzzles in the dataset for testing
# solved_puzzles_df = solve_puzzles(puzzles_df, puzzle_info_df, sample_submission_df, num_puzzles=3)
# print(solved_puzzles_df)

# start = 30
# end  = 31
# solved_puzzles_df = solve_puzzles(puzzles_df.iloc[start:end], puzzle_info_df, sample_submission_df, num_puzzles=None, limit_index=398)
# print(solved_puzzles_df)
# exit()

# #---
# # Solving the first 30 puzzles in the dataset
print("----start-----")
solved_puzzles_df = solve_puzzles(puzzles_df, puzzle_info_df, sample_submission_df, num_puzzles=None, limit_index=30)

print("-"*80)

tot = 0
for i in range(len(solved_puzzles_df)) :
    path = solved_puzzles_df.iloc[i].moves.split(".")
    tot += len(path)
    print(f"{i} : {len(path)}")
    
print(f"score={tot}")

# Define the file path for the output CSV file
output_csv_path = f'submission_astar_{tot}.csv'
# # Save the output DataFrame to a CSV file
solved_puzzles_df.to_csv(output_csv_path, index=False)

