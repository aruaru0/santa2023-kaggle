package main

import (
	"bufio"
	"container/heap"
	"crypto/sha1"
	"encoding/csv"
	"flag"
	"fmt"
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

	// file, err := os.Open(fname)
	// if err != nil {
	// 	log.Fatal(err)
	// }
	// defer file.Close()
	// scanner := bufio.NewScanner(file)
	// scanner.Scan()
	// s := scanner.Text()
	bytes, err := os.ReadFile(fname)
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

func abs(x int) int {
	if x < 0 {
		return -x
	}
	return x
}

type pqi struct {
	a, b  float64
	state string
}

type priorityQueue []pqi

func (pq priorityQueue) Len() int            { return len(pq) }
func (pq priorityQueue) Swap(i, j int)       { pq[i], pq[j] = pq[j], pq[i] }
func (pq priorityQueue) Less(i, j int) bool  { return pq[i].a+pq[i].b < pq[j].a+pq[j].b }
func (pq *priorityQueue) Push(x interface{}) { *pq = append(*pq, x.(pqi)) }
func (pq *priorityQueue) Pop() interface{} {
	x := (*pq)[len(*pq)-1]
	*pq = (*pq)[0 : len(*pq)-1]
	return x
}

func hash(state string) [20]byte {
	ret := sha1.Sum([]byte(state))
	return ret
}

func reverse_path(path []string) []string {
	ret := make([]string, 0)
	for i := len(path) - 1; i >= 0; i-- {
		ret = append(ret, path[i])
	}
	return ret
}

type Route struct {
	from [20]byte
	move string
}

func calcDiff(s0, s1 string) int {
	cnt := 0
	for i := 0; i < len(s0); i++ {
		if s0[i] == s1[i] {
			cnt++
		}
	}
	return cnt
}

func manhattanDistance(cube1, cube2 string, n int) int {
	if len(cube1) != len(cube2) {
		panic("Both cubes must have the same length")
	}

	distance := 0
	for i := 0; i < len(cube1); i++ {
		row1, col1 := i/n, i%n
		row2, col2 := strings.IndexByte(cube2, cube1[i])/n, strings.IndexByte(cube2, cube1[i])%n
		distance += abs(row1-row2) + abs(col1-col2)
	}

	return distance
}

func num_of_change(cur string) int {
	p := cur[0]
	cnt := 0
	for i := 0; i < len(cur); i++ {
		if p != cur[i] {
			cnt++
		}
		p = cur[i]
	}
	return cnt
}

func calcDistance(s0, s1 string) int {
	dist := 0
	s := strings.Split(s1, ";")
	m := make(map[string][]int)
	for i, e := range s {
		m[e] = append(m[e], i)
	}

	s = strings.Split(s0, ";")
	for i, e := range s {
		d := inf
		for _, v := range m[e] {
			d = min(d, int(dmap[i][v]))
		}
		dist += d
	}

	return dist
}

// ⭐︎超重要な間数
func h(cur, target string, kn int) float64 {
	h0 := float64(calcDiff(cur, target))
	// n := math.Sqrt(float64(len(cur)))
	// h1 := manhattanDistance(cur, target, int(n))
	// h1 := float64(num_of_change(cur))
	h1 := float64(calcDistance(cur, target))
	// return 0.0
	return (h0 + h1) / float64(kn)
}

func bsf(start, last string, numWild int, moves map[string][]int16, limit int, timeout string) ([]string, bool) {
	// fmt.Println("bsf:")
	// fmt.Println("bsf:")
	// bar.Write([]byte("TEST\n"))

	pq0 := priorityQueue{}
	heap.Push(&pq0, pqi{0, 0, start})
	used0 := make(map[[20]byte]Route)
	used0[hash(start)] = Route{[20]byte{}, ""}

	pq1 := priorityQueue{}
	heap.Push(&pq1, pqi{0, 0, last})
	used1 := make(map[[20]byte]Route)
	used1[hash(last)] = Route{[20]byte{}, ""}

	find_state := ""

	start_time := time.Now()

	timeOut, _ := time.ParseDuration(timeout)
	loopcnt := 0

	kn := len(strings.Split(start, ";"))
LOOP:
	for len(pq0) != 0 || len(pq1) != 0 {
		if len(pq0) != 0 {
			cur := pq0[0]
			cur_hash := hash(cur.state)
			heap.Pop(&pq0)
			for e := range moves {
				next := applyMove(e, cur.state, moves)
				if _, ok := used0[hash(next)]; ok { // すでに訪問している場合はスキップ
					continue
				}
				// 訪問していない場合は、距離を計算して追加
				used0[hash(next)] = Route{cur_hash, e}
				heap.Push(&pq0, pqi{cur.a + 1, h(cur.state, last, kn), next})

				if _, ok := used1[hash(next)]; ok {
					find_state = next
					break LOOP
				}
			}
		}
		if len(pq1) != 0 {
			cur := pq1[0]
			cur_hash := hash(cur.state)
			heap.Pop(&pq1)
			for e := range moves {
				next := applyMove(e, cur.state, moves)
				if _, ok := used1[hash(next)]; ok { // すでに訪問している場合はスキップ
					continue
				}
				// 訪問していない場合は、距離を計算して追加
				used1[hash(next)] = Route{cur_hash, e}
				heap.Push(&pq1, pqi{cur.a + 1, h(cur.state, start, kn), next})

				if _, ok := used0[hash(next)]; ok {
					find_state = next
					break LOOP
				}
			}
		}
		// fmt.Println(len(used0), len(used1))
		cnt := len(used0) + len(used1)
		if cnt > limit {
			fmt.Println("-->Not found.")
			return []string{}, false
		}
		// fmt.Println(loopcnt, timeOut)
		if loopcnt%1000 == 0 && time.Since(start_time) >= timeOut {
			fmt.Println("-->Time out.")
			return []string{}, false
		}
		loopcnt++
	}

	// fmt.Println("time = ", time.Since(start_time))
	// make path
	state := hash(find_state)
	path := make([]string, 0)
	target := hash(start)
	for state != target {
		path = append(path, used0[state].move)
		state = used0[state].from
	}
	path = reverse_path(path)

	state = hash(find_state)
	target = hash(last)
	for state != target {
		e := used1[state].move
		if e[0] == '-' {
			e = e[1:]
		} else {
			e = "-" + e
		}
		path = append(path, e)
		state = used1[state].from
	}

	// fmt.Println("-->Found", path, len(path))

	return path, true
}

const inf = math.MaxInt16

// 各位置からの距離を計算
func make_distance_map(n int, moves map[string][]int16) [][]int16 {
	node := make([][]int16, n)
	dist := make([][]int16, n)

	for _, move := range moves {
		for f, e := range move {
			if int16(f) == e {
				continue
			}
			node[f] = append(node[f], e)
		}
	}

	for i := 0; i < n; i++ {
		dist[i] = make([]int16, n)
		d := dist[i]
		for j := 0; j < n; j++ {
			d[j] = inf
		}
		// bsf
		d[i] = 0
		q := []int{i}
		for len(q) != 0 {
			cur := q[0]
			q = q[1:]
			for _, e := range node[cur] {
				if d[e] > d[cur]+1 {
					d[e] = d[cur] + 1
					q = append(q, int(e))
				}
			}
		}
	}
	return dist
}

var dmap [][]int16
var r *rand.Rand

func main() {
	r = rand.New(rand.NewSource(time.Now().UnixNano()))
	pid := flag.Int("problem_id", -1, "")
	csvFile := flag.String("path_dir", "", "")
	astep := flag.Int("step", 10000000, "")
	prob := flag.Float64("prob", 2.0, "")
	limit := flag.Int("limit", 100000, "")
	timeout := flag.String("timeout", "300s", "")
	// list := flag.String("separate_tbl", "1,1,1,1,2,2,2,3,3,3,4,4,5,5,6,7,8,9,10,15,20", "")

	flag.Parse()

	// tbl := []int{}
	// for _, e := range strings.Split(*list, ",") {
	// 	v, _ := strconv.Atoi(e)
	// 	tbl = append(tbl, v)
	// }

	if *pid == -1 {
		fmt.Println("need --problem_id")
		return
	}

	fmt.Println("========================")
	fmt.Println("PID:", *pid, "==> Step:", *astep, "timeout", *timeout)
	if *prob < 0 {
		*prob = r.Float64() + 2.0/10
		fmt.Println("prob = ", *prob)
	}

	PUZZLE_FILE := "../../data/puzzles.csv"
	SAMPLEDIR := *csvFile

	ddf := readCSV(PUZZLE_FILE, *pid)
	info := readInfo(ddf.ptype)
	paths := readPath(SAMPLEDIR, *pid)

	fmt.Println("Path size = ", len(paths), ": ", ddf.ptype)

	// return
	moves := initReverseMoves(info)

	if ddf.ptype != "globe_1/8" {
		fmt.Println("not globe_1/8")
		return
	}

	//------------------------------------------------------------
	// 距離テーブルを作成
	N := len(strings.Split(ddf.initial, ";"))
	dmap = make_distance_map(N, moves)
	//------------------------------------------------------------

	fmt.Println(ddf)

	solpat := strings.Split(ddf.solution, ";")
	solLen := len(solpat)
	loop := solLen

	c := []int{6, 6, 6, 6, 6, 6, 9, 9, 9, 11, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 31, 31, 31, 32}

	if *pid < 343 {
		loop -= 2
		// c = []int{6, 6, 6, 6, 6, 6, 9, 9, 9, 11, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32}
		// c = []int{6, 6, 6, 6, 6, 6, 8, 8, 10, 10, 12, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32}
		c = []int{6, 6, 6, 6, 6, 6, 8, 8, 10, 10, 12, 12, 14, 14, 16, 16, 18, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 32, 32}
		// c = []int{6, 6, 6, 6, 6, 6, 8, 8, 10, 10, 12, 12, 14, 14, 16, 16, 18, 18, 20, 20, 22, 22, 24, 24, 26, 26, 28, 28, 30, 30, 32, 32}
		// c = []int{8, 8, 8, 8, 8, 8, 8, 8, 10, 10, 12, 12, 14, 14, 16, 16, 18, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 32, 32}

	}
	newpath := []string{}

	for n := 0; n < loop; n++ {
		solution := []string{}
		cnt := c[n]
		for i := 0; i < solLen; i++ {
			if i < cnt {
				// solution = append(solution, strconv.FormatInt(int64(i), 10))
				solution = append(solution, solpat[i])
			} else {
				solution = append(solution, "x")
			}
		}
		solState := strings.Join(solution, ";")
		fmt.Println(solLen)
		fmt.Println("STATE = ", solState)

		state := solState
		for i := len(paths) - 1; i >= 0; i-- {
			e := paths[i]
			if e[0] == '-' {
				e = e[1:]
			} else {
				e = "-" + e
			}
			state = applyMove(e, state, moves)
		}
		for _, e := range newpath {
			state = applyMove(e, state, moves)
		}

		if state == solState {
			continue
		}
		fmt.Println("INIT  = ", state)

		ret, ok := bsf(
			state, solState,
			ddf.numWild, moves, *limit, *timeout)

		if ok == false {
			break
		}

		fmt.Println("n = ", n, "path = ", ret)
		newpath = append(newpath, ret...)
	}

	fmt.Println(newpath)
	// fmt.Println(*limit)
	// newpath := paths

	fmt.Println("[Check] check new path")
	state := ddf.initial
	fmt.Println(state)
	for _, path := range newpath {
		state = applyMove(path, state, moves)
		fmt.Println(state)
	}

	fmt.Println("[valid check]")
	if validCheck(state, ddf.solution, ddf.numWild) == false {
		fmt.Println("Error...", *pid)
		return
	}

	score := len(newpath) - len(paths)
	fmt.Println("-----------------------------------------------------------------------")
	fmt.Printf("[%d]: Score = %d - %d = %d\n", *pid, len(newpath), len(paths), score)
	fmt.Println("-----------------------------------------------------------------------")

	if score < 0 {
		fmt.Println("Update...")
		writePath(SAMPLEDIR, *pid, newpath)
	}
	// fmt.Println(SAMPLEDIR)
	// writePath(SAMPLEDIR, *pid, newpath)

	// if score < 0 :
	// 	print("Update.")
	// 	with open(f"sol_2dir_k/{pid}.txt", "w") as f :
	// 		f.write(".".join(new_path))

}
