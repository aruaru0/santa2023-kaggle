import argparse
import time

import numpy as np
import pandas as pd
from tqdm import tqdm


class ExceedMaxSizeError(RuntimeError):
    pass


def get_shortest_path(
    moves: dict[str, tuple[int, ...]], K: int, max_size: int 
) -> dict[tuple[int, ...], list[str]]:
    n = len(next(iter(moves.values())))

    state = tuple(range(n))
    cur_states = [state]

    shortest_path: dict[tuple[int, ...], list[str]] = {}
    shortest_path[state] = []

    for _ in range(100 if K is None else K):
        next_states = []
        for state in cur_states:
            for move_name, perm in moves.items():
                next_state = tuple(state[i] for i in perm)
                if next_state in shortest_path:
                    continue
                shortest_path[next_state] = shortest_path[state] + [move_name]

                if max_size is not None and len(shortest_path) > max_size:
                    raise ExceedMaxSizeError

                next_states.append(next_state)
        cur_states = next_states

    return shortest_path


def get_moves(puzzle_type: str) -> dict[str, tuple[int, ...]]:
    moves = eval(pd.read_csv("data/puzzle_info.csv").set_index("puzzle_type").loc[puzzle_type, "allowed_moves"])
    for key in list(moves.keys()):
        moves["-" + key] = list(np.argsort(moves[key]))
    return moves


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--problem_id", type=int, required=True)
    parser.add_argument("--time_limit", type=float, default=2 * 60 * 60)  # 2h
    args = parser.parse_args()

    puzzle = pd.read_csv("data/puzzles.csv").set_index("id").loc[args.problem_id]
    sample_submission = pd.read_csv("data/sample_submission.csv").set_index("id").loc[args.problem_id]
    sample_moves = sample_submission["moves"].split(".")
    print(puzzle)
    print(f"Sample score: {len(sample_moves)}")

    moves = get_moves(puzzle["puzzle_type"])
    print(f"Number of moves: {len(moves)}")

    K = 2
    while True:
        try:
            shortest_path = get_shortest_path(moves, K, None if K == 2 else 100000)
        except ExceedMaxSizeError:
            break
        K += 1
    print(f"K: {K}")
    print(f"Number of shortest_path: {len(shortest_path)}")

    current_state = puzzle["initial_state"].split(";")
    current_solution = list(sample_moves)
    initial_score = len(current_solution)
    start_time = time.time()

    with tqdm(total=len(current_solution) - K, desc=f"Score: {len(current_solution)} (-0)") as pbar:
        step = 0
        while step + K < len(current_solution) and time.time() - start_time < args.time_limit:
            replaced_moves = current_solution[step : step + K + 1]
            state_before = current_state
            state_after = current_state
            for move_name in replaced_moves:
                state_after = [state_after[i] for i in moves[move_name]]

            found_moves = None
            for perm, move_names in shortest_path.items():
                for i, j in enumerate(perm):
                    if state_after[i] != state_before[j]:
                        break
                else:
                    found_moves = move_names
                    break

            if found_moves is not None:
                length_before = len(current_solution)
                current_solution = current_solution[:step] + list(found_moves) + current_solution[step + K + 1 :]
                pbar.update(length_before - len(current_solution))
                pbar.set_description(f"Score: {len(current_solution)} ({len(current_solution) - initial_score})")
                for _ in range(K):
                    if step == 0:
                        break
                    step -= 1
                    pbar.update(-1)
                    move_name = current_solution[step]
                    move_name = move_name[1:] if move_name.startswith("-") else f"-{move_name}"
                    current_state = [current_state[i] for i in moves[move_name]]
            else:
                current_state = [current_state[i] for i in moves[current_solution[step]]]
                step += 1
                pbar.update(1)

    # validation
    state = puzzle["initial_state"].split(";")
    for move_name in current_solution:
        state = [state[i] for i in moves[move_name]]
    assert puzzle["solution_state"].split(";") == state

    with open(f"solutions/{args.problem_id}.txt", "w") as fp:
        fp.write(".".join(current_solution))


if __name__ == "__main__":
    main()