#
# K個のshrtestパスで置き換える
# 
import argparse
import time

import numpy as np
import pandas as pd
from tqdm import tqdm
import sys


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

    # 初期パターンからK回置換を繰り返して到達できるパターンを全探索する
    # もし、パターンが登録されていなければshottest_pathにパターンを登録する
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

                if len(shortest_path)%1000000 == 0 : print(len(shortest_path), K)
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
    parser.add_argument("--csv_file", type=str, required=True)
    args = parser.parse_args()


    not_process = set([0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 
                       27, 28, 29, 284, 285, 286, 287, 288, 289, 290, 291, 292, 293, 294, 295, 296, 297, 298, 299, 
                       300, 301, 302, 303, 304, 305, 306, 307, 308, 309, 310, 311, 312, 313, 314, 315, 316, 317, 318, 319, 
                       320, 321, 322, 323, 324, 325, 326, 327, 328, 329,])
    if args.problem_id in not_process :
        exit()


    puzzle = pd.read_csv("data/puzzles.csv").set_index("id").loc[args.problem_id]
    # sample_submission = pd.read_csv("data/sample_submission.csv").set_index("id").loc[args.problem_id]
    print(f"file = {args.csv_file}")
    sample_submission = pd.read_csv(args.csv_file).set_index("id").loc[args.problem_id]
    sample_moves = sample_submission["moves"].split(".")
    print(puzzle)
    print(f"Sample score: {len(sample_moves)}")

    moves = get_moves(puzzle["puzzle_type"])
    print(f"Number of moves: {len(moves)}")

    K = 2
    
    # alpha = 10
    # if len(sample_moves) > 1000 : 
    #     alpha = 2
    # elif len(sample_moves) > 500 :
    #     alpha = 5
    # print("*****aplha = ", alpha, len(sample_moves))
    max_size = 1000000   

    # timeout
    #  281, 282, 283, 330, 331, 332, 333, 334, 335, 336, 337,  384, 385, 388, 389, 390, 391, 391, 393, 394,  395
    if args.problem_id in (278, 279, 280, 281, 282, 283, 330, 331, 332, 333, 334, 335, 336, 337,  384, 385, 388, 389, 390, 391, 391, 393, 394, 395) :
        max_size = 100000

    while True:
        try:
            shortest_path = get_shortest_path(moves, K, None if K == 2 else max_size)
        except ExceedMaxSizeError:
            break
        if len(shortest_path) > max_size : break
        K += 1
    print(f"K: {K}")
    print(f"Number of shortest_path: {len(shortest_path)}")

    tmp = []
    for s in shortest_path:
        tmp.append((s, shortest_path[s]))

    shortest_path = sorted(tmp, key = lambda x: len(x[1])) 


    current_state = puzzle["initial_state"].split(";")
    current_solution = list(sample_moves)
    initial_score = len(current_solution)
    start_time = time.time()


    tot = (len(current_solution) - K)
    with tqdm(total=tot, desc=f"Score: {len(current_solution)} (-0)") as pbar:
        step = 0
        # 現在のソリューションの長さまでstepを動かしながら
        while step + K < len(current_solution) and time.time() - start_time < args.time_limit:
            # 対象となる部分を抽出
            replaced_moves = current_solution[step : step + K + 1]
            state_before = current_state
            state_after = current_state
            for move_name in replaced_moves:
                state_after = [state_after[i] for i in moves[move_name]]
            # state_beforeとstate_afterに、前後のステートを入れる

            found_moves = None
            for perm, move_names in shortest_path: #.items():
                for i, j in enumerate(perm):
                    if state_after[i] != state_before[j]:
                        break
                else:
                    found_moves = move_names
                    break

            # 事前に作ったパスリストから、一致するものが見つかったら
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

    if time.time() - start_time > args.time_limit: 
        print(f"********** time out!! {args.problem_id} *************")
        exit()

    print(f"========= solution {args.problem_id} result: {len(current_solution)-initial_score}")

    with open(f"solutions/{args.problem_id}.txt", "w") as fp:
        fp.write(".".join(current_solution))


if __name__ == "__main__":
    main()
