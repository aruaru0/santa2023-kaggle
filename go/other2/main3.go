package main

import (
	"bufio"
	"crypto/sha1"
	"encoding/csv"
	"flag"
	"fmt"
	"io/ioutil"
	"log"
	"math"
	"math/rand"
	"os"
	"strconv"
	"strings"
	"time"
)

// Data ... puzzle data
type Data struct {
	ptype             string
	solution, initial string
	numWild           int
}

// // Info ... Info
// type Info struct {
// 	name string
// 	move []int16
// }

func readCSV(fname string, pid int) Data {
	file, err := os.Open(fname)
	if err != nil {
		log.Fatal(err)
	}
	defer file.Close()

	r := csv.NewReader(file)
	rows, err := r.ReadAll()
	if err != nil {
		log.Fatal(err)
	}

	s := rows[pid+1]

	n, _ := strconv.Atoi(s[4])

	return Data{s[1], s[2], s[3], n}
}

func readInfo(ptype string) map[string][]int16 {
	ptype = strings.ReplaceAll(ptype, "/", "_")

	fname := fmt.Sprintf("info/%s.txt", ptype)
	// fmt.Println(fname)

	file, err := os.Open(fname)
	if err != nil {
		log.Fatal(err)
	}
	defer file.Close()

	scanner := bufio.NewScanner(file)

	ret := make(map[string][]int16, 0)

	scanner.Scan()
	n, err := strconv.Atoi(scanner.Text())
	if err != nil {
		log.Fatal(err)
	}
	fmt.Println("moves:", n)

	for scanner.Scan() {
		s := scanner.Text()
		strs := strings.Split(s, " ")
		name := strs[0]
		v := make([]int16, 0)
		for _, e := range strs[1:] {
			x, _ := strconv.Atoi(e)
			v = append(v, int16(x))
		}
		ret[name] = v
	}

	return ret
}

func readPath(dir string, pid int) []string {
	fname := fmt.Sprintf("%s/%d.txt", dir, pid)

	bytes, err := ioutil.ReadFile(fname)
	if err != nil {
		panic(err)
	}

	s := string(bytes)
	strs := strings.Split(s, ".")

	return strs
}

func writePath(dir string, pid int, path []string) {
	fname := fmt.Sprintf("%s/%d.txt", dir, pid)

	file, err := os.Create(fname)
	if err != nil {
		log.Fatal(err)
	}
	defer file.Close()

	s := strings.Join(path, ".")
	file.Write([]byte(s))
}

//--------------------------------------------------

func initReverseMoves(moves map[string][]int16) map[string][]int16 {
	newMoves := make(map[string][]int16, 0)
	for m, xform := range moves {
		mInv := "-" + m
		xformInv := make([]int16, len(xform))
		for i := 0; i < len(xform); i++ {
			xformInv[xform[i]] = int16(i)
		}
		newMoves[m] = xform
		newMoves[mInv] = xformInv
	}
	return newMoves
}

func applyMove(move string, state string, moves map[string][]int16) string {
	m := move
	s := strings.Split(state, ";")

	moveList := moves[m]
	newState := []string{}
	for _, e := range moveList {
		newState = append(newState, s[e])
	}
	return strings.Join(newState, ";")
}

func validCheck(state, target string, numWild int) bool {
	cnt := 0
	for i := 0; i < len(state); i++ {
		if state[i] != target[i] {
			cnt++
			if cnt > numWild {
				return false
			}
		}
	}
	if cnt <= numWild {
		return true
	}
	return false
}

var memo map[[20]byte]int16

func calcDiff(s0, s1 string) int {
	cnt := 0
	for i := 0; i < len(s0); i++ {
		if s0[i] == s1[i] {
			cnt++
		}
	}
	return cnt
}

// 見つけた最短経路のパスを作成
func makeRoute(goal int32, ipath []int32, node [][]Edge) ([]string, []int32) {
	ret := []int32{goal}
	pos := goal
	for ipath[pos] != -1 {
		pos = ipath[pos]
		ret = append(ret, pos)
	}
	p := []string{}
	rret := []int32{}
	for i := len(ret) - 1; i >= 0; i-- {
		rret = append(rret, ret[i])
	}
	ret = rret
	for i, e := range ret {
		if e == goal {
			break
		}
		for _, v := range node[e] {
			if v.to == ret[i+1] {
				p = append(p, v.pat)
				break
			}
		}
	}
	return p, ret
}

// def make_route(goal, ipath, node) :
//     ret = [goal]
//     pos = goal
//     while ipath[pos] != -1 :
//         pos = ipath[pos]
//         ret.append(pos)

//     p = []
//     ret = ret[::-1]
//     for i, e in enumerate(ret) :
//         if e == goal: break
//         for to, val in node[e] :
//             if to == ret[i+1] :
//                 p.append(val)
//                 break
//     return p , ret

type Pair struct {
	x, y int32
}

type Edge struct {
	to  int32
	pat string
}

func Search(paths []string, moves map[string][]int16, initial_state, solution_state string, num_wildcards int, prob float64, limit int) (int, []string) {
	// orgLen := len(paths)
	max_size := limit + len(paths)

	// 終了状態
	end := make(map[int]bool)

	// グラフを作成する
	node := make([][]Edge, max_size)
	pat2idx := make(map[[20]byte]int32)
	pair := make(map[Pair]bool)
	// curCnt := 0
	// 初期の状態遷移を作成
	state := initial_state
	hashed_state := sha1.Sum([]byte(state))
	pat2idx[hashed_state] = 0

	nodes := make(map[string]bool, 0)
	nodes[state] = true

	for _, e := range paths {
		hashed_state := sha1.Sum([]byte(state))
		from := pat2idx[hashed_state]
		next := applyMove(e, state, moves)
		hashed_next := sha1.Sum([]byte(next))
		if _, ok := pat2idx[hashed_next]; ok == false {
			if validCheck(next, solution_state, num_wildcards) {
				end[len(pat2idx)] = true
			}
			pat2idx[hashed_next] = int32(len(pat2idx))
			nodes[next] = true
		}
		to := pat2idx[hashed_next]
		if pair[Pair{from, to}] == false {
			node[from] = append(node[from], Edge{to, e})
			pair[Pair{from, to}] = true
		}
		if pair[Pair{to, from}] == false {
			if e[0] == '-' {
				e = e[1:]
			} else {
				e = "-" + e
			}
			node[to] = append(node[to], Edge{from, e})
			pair[Pair{to, from}] = true
		}
		state = next
	}

	if validCheck(state, solution_state, num_wildcards) {
		fmt.Println("OK")
	}

	// max_sizeになるまでループさせる
	moveList := make([]string, 0)
	for e := range moves {
		moveList = append(moveList, e)
	}
	K := 1

	// nodes := make(map[[20]byte]bool, 0)
	// for node := range pat2idx {
	// 	nodes[node] = true
	// }

LOOP:
	for len(pat2idx) < max_size {
		nextNodes := make(map[string]bool)
		if len(nodes) == 0 {
			fmt.Println("Eary Stopping")
			break
		}
		for state := range nodes {
			cur_to_cnt := calcDiff(state, solution_state)
			cur_from_cnt := calcDiff(state, initial_state)
			for _, e := range moveList {
				hashed_state := sha1.Sum([]byte(state))
				from := pat2idx[hashed_state]
				next := applyMove(e, state, moves)
				hashed_next := sha1.Sum([]byte(next))
				p_th := prob
				if _, ok := pat2idx[hashed_next]; ok {
					p_th += 1.0
				}
				next_from_cnt := calcDiff(next, initial_state)
				next_to_cnt := calcDiff(next, solution_state)
				if next_from_cnt >= cur_from_cnt {
					p_th += math.Max(0.1, (1-prob)/2)
					// p_th += 1.0
				}
				if next_to_cnt >= cur_to_cnt {
					p_th += math.Max(0.1, (1-prob)/2)
					// p_th += 1.0
				}

				if r.Float64() > p_th {
					continue
				}

				if _, ok := pat2idx[hashed_next]; ok == false {
					if validCheck(next, solution_state, num_wildcards) {
						end[len(pat2idx)] = true
					}
					pat2idx[hashed_next] = int32(len(pat2idx))
					nextNodes[next] = true
					if len(pat2idx)%1000000 == 0 {
						fmt.Println(" ", len(pat2idx), "nodes... ", len(pair), "edges...")
					}
				}
				to := pat2idx[hashed_next]
				if pair[Pair{from, to}] == false {
					node[from] = append(node[from], Edge{to, e})
					pair[Pair{from, to}] = true
				}
				if pair[Pair{to, from}] == false {
					if e[0] == '-' {
						e = e[1:]
					} else {
						e = "-" + e
					}
					node[to] = append(node[to], Edge{from, e})
					pair[Pair{to, from}] = true
				}
				if len(pat2idx) >= max_size {
					break LOOP
				}
			}
		}
		// fmt.Println(len(nextNodes), K)
		nodes = nextNodes
		K++
	}
	fmt.Println("K = ", K, len(pat2idx))

	// BSF
	start := 0
	fmt.Println("start = ", start, "goal = ", end)

	fmt.Println("BSF...")
	const inf = int(1e18)
	dist := make([]int, max_size)
	ipath := make([]int32, max_size)
	for i := 0; i < max_size; i++ {
		dist[i] = inf
		ipath[i] = -1.0
	}
	q := []int{start}
	dist[start] = 0

	for len(q) != 0 {
		cur := q[0]
		q = q[1:]
		for _, e := range node[cur] {
			if dist[e.to] > dist[cur]+1 {
				dist[e.to] = dist[cur] + 1
				ipath[e.to] = int32(cur)
				q = append(q, int(e.to))
			}
			if dist[e.to] == dist[cur]+1 {
				if r.Float64() > 0.8 {
					ipath[e.to] = int32(cur)
				}
			}
		}
	}

	fmt.Println("make path...")
	new_path := make([]string, 0)
	for e := range end {
		path, _ := makeRoute(int32(e), ipath, node)
		if len(new_path) == 0 || len(new_path) > len(path) {
			new_path = path
		}
	}
	score := len(new_path) - len(paths)
	fmt.Println("Score = ", len(new_path), "-", len(paths), "=", len(new_path)-len(paths))
	return score, new_path
	//     score = len(new_path)  - len(paths)
	//     pbar.write(f"Score = {len(new_path)} - {len(paths)} = {score}")

}

func max(a, b int) int {
	if a > b {
		return a
	}
	return b
}

func min(a, b int) int {
	if a < b {
		return a
	}
	return b
}

var r *rand.Rand

func main() {
	r = rand.New(rand.NewSource(time.Now().UnixNano()))
	pid := flag.Int("problem_id", -1, "")
	csvFile := flag.String("path_dir", "", "")
	step := flag.Int("step", -1, "")
	prob := flag.Float64("prob", 2.0, "")
	limit := flag.Int("limit", 100000, "")
	list := flag.String("separate_tbl", "1,1,1,1,2,2,2,3,3,3,4,4,5,5,6,7,8,9,10,15,20", "")

	flag.Parse()

	tbl := []int{}
	for _, e := range strings.Split(*list, ",") {
		v, _ := strconv.Atoi(e)
		tbl = append(tbl, v)
	}

	// fmt.Println("ARGS", *pid, *csvFile, *step, *prob)

	if *pid == -1 {
		fmt.Println("need --problem_id")
		return
	}

	fmt.Println("========================")
	fmt.Println("PID:", *pid)

	if *prob < 0 {
		*prob = r.Float64() + 2.0/10
	}
	fmt.Println("prob = ", *prob)

	PUZZLE_FILE := "../data/puzzles.csv"
	SAMPLEDIR := *csvFile

	ddf := readCSV(PUZZLE_FILE, *pid)
	info := readInfo(ddf.ptype)
	paths := readPath(SAMPLEDIR, *pid)

	fmt.Println("Path size = ", len(paths), ": ", ddf.ptype)

	moves := initReverseMoves(info)

	memo = make(map[[20]byte]int16)

	if *step < 0 {
		x := -(*step)
		if x >= 100 {
			// tbl := []int{1, 1, 1, 1, 2, 2, 2, 3, 3, 3, 4, 4, 5, 5, 6, 7, 8, 9, 10, 15, 20}
			x = tbl[r.Intn(len(tbl))]
		}
		*step = max(20, (len(paths)+x-1)/x)
	}
	n := (len(paths) + *step - 1) / (*step)
	fmt.Println("n = ", n, *step, "wild = ", ddf.numWild)

	new_path := make([]string, 0)

	// pathを作成
	// state1 := ddf.initial
	// states := []string{state1}
	// for _, path := range paths {
	// 	state1 = applyMove(path, state1, moves)
	// 	states = append(states, state1)
	// }

	// fmt.Println("PASS")

	start_state := ddf.initial
	state0 := start_state
	last := ""
	for pos := 0; pos < n; pos++ {
		fmt.Printf("[%d/%d]=========\n", pos+1, n)
		f := max(0, pos*(*step))
		e := min(len(paths), f+(*step))

		state0 = start_state
		for _, v := range paths[f:e] {
			state0 = applyMove(v, state0, moves)
		}
		// start_state := states[f]
		// end_state := states[e]
		end_state := state0
		num_wild := 0
		if pos == n-1 {
			num_wild = ddf.numWild
			end_state = ddf.solution
		}
		sel_path := paths[f:e]
		_, path := Search(sel_path, moves, start_state, end_state, num_wild, *prob, *limit)

		state := start_state
		for _, e := range path {
			state = applyMove(e, state, moves)
		}
		new_path = append(new_path, path...)
		start_state = end_state
		last = end_state
	}

	fmt.Println("initial path validation = ", validCheck(ddf.solution, last, ddf.numWild))

	// score, new_path := Search(paths, moves, ddf.initial, ddf.solution, ddf.numWild, *prob, *limit)
	fmt.Println("[Check] check new path")
	state := ddf.initial
	for _, path := range new_path {
		state = applyMove(path, state, moves)
	}

	fmt.Println("[valid check]")
	if validCheck(state, ddf.solution, ddf.numWild) == false {
		fmt.Println("Error...", *pid)
		return
	}

	score := len(new_path) - len(paths)
	fmt.Println("-----------------------------------------------------------------------")
	fmt.Printf("[%d]: Score = %d - %d = %d\n", *pid, len(new_path), len(paths), score)
	fmt.Println("-----------------------------------------------------------------------")

	if score < 0 {
		fmt.Println("Update...")
		writePath(SAMPLEDIR, *pid, new_path)
	} else if score == 0 {
		same := true
		for i := 0; i < len(new_path); i++ {
			if new_path[i] != paths[i] {
				same = false
			}
		}
		if !same {
			fmt.Println("Update...same size but change paths")
			writePath(SAMPLEDIR, *pid, new_path)
		}
	}

	// if score < 0 :
	// 	print("Update.")
	// 	with open(f"sol_2dir_k/{pid}.txt", "w") as f :
	// 		f.write(".".join(new_path))

}
