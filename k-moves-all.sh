if [ $# -eq 0 ]; then
    echo "No argument was specified."
    exit 1
fi

# seq  150 397 | xargs -I {} python3 k-moves.py --problem_id {} --time_limit 3600 --csv_file $1
# seq  30 149 | xargs -I {} python3 k-moves.py --problem_id {} --time_limit 3600 --csv_file $1
seq  0 397 | xargs -P 4 -I {} python3 k-moves.py --problem_id {} --time_limit 1800 --csv_file $1
