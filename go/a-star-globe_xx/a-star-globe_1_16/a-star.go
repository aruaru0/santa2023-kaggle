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
	"sort"
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

func initReverseMoves(moves map[string][]int16, ptype string) map[string][]int16 {
	flg := strings.Contains(ptype, "globe_")
	if flg {
		fmt.Println("type flg = ", flg)
	}

	newMoves := make(map[string][]int16, 0)
	for m, xform := range moves {
		newMoves[m] = xform
		if flg && m[0] != 'r' {
			continue
		}
		mInv := "-" + m
		xformInv := make([]int16, len(xform))
		for i := 0; i < len(xform); i++ {
			xformInv[xform[i]] = int16(i)
		}
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
	move  string
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

func get_r_move(m string, moves map[string][]int16) string {
	// fmt.Println("get_r_move", m)
	t := m
	if m[0] == '-' {
		t = m[1:]
	} else {
		t = "-" + m
		if _, ok := moves[t]; ok == false {
			t = m
		}
	}
	// fmt.Println("get_r_move", t)

	return t
}

// ⭐︎超重要な間数
func h(cur, next, target string, kn int) float64 {
	// n := math.Sqrt(float64(len(cur)))
	// h1 := manhattanDistance(cur, target, int(n))
	// h1 := float64(num_of_change(cur))
	// h1 := float64(calcDistance(next, target) - calcDistance(cur, target))
	// return 0.0
	// h1 := 0.0
	// nx := float64(calcDistance(next, target))
	// cu := float64(calcDistance(cur, target))
	// h1 := 1.0
	// if cu <= nx {
	// 	h1 = 0.0
	// }
	// return h0/float64(kn) + h1
	// return 0
	h0 := float64(calcDiff(next, target))
	h1 := float64(calcDistance(next, target))
	return (h0 + h1) / float64(kn)
}

func rule(prev, cur string) bool {

	// if strings.Contains(ddf.ptype, "globe") {
	// 	e := strings.Split(prev, "_")[0]
	// 	if e[0] == '-' {
	// 		e = e[1:]
	// 	}
	// 	v := strings.Split(cur, "_")[0]
	// 	if v[0] == '-' {
	// 		v = v[1:]
	// 	}
	// 	if v == e {
	// 		return false
	// 	}
	// }

	return true
}

func bsf(start, last string, numWild int, moves map[string][]int16, limit int, timeout string) ([]string, bool) {
	// fmt.Println("bsf:")
	// fmt.Println("bsf:")
	// bar.Write([]byte("TEST\n"))

	pq0 := priorityQueue{}
	heap.Push(&pq0, pqi{0, 0, start, "xx"})
	used0 := make(map[[20]byte]Route)
	used0[hash(start)] = Route{[20]byte{}, ""}

	pq1 := priorityQueue{}
	heap.Push(&pq1, pqi{0, 0, last, "xx"})
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
			for _, e := range movelist {
				if rule(cur.move, e) == false {
					continue
				}
				if cur.a > maxDepth {
					continue
				}
				next := applyMove(e, cur.state, moves)
				if _, ok := used0[hash(next)]; ok { // すでに訪問している場合はスキップ
					continue
				}
				// 訪問していない場合は、距離を計算して追加
				used0[hash(next)] = Route{cur_hash, e}
				heap.Push(&pq0, pqi{cur.a + 1, h(cur.state, next, last, kn), next, e})

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
			for _, e := range movelist {
				if rule(cur.move, e) == false {
					continue
				}
				if cur.a > maxDepth {
					continue
				}
				next := applyMove(e, cur.state, moves)
				if _, ok := used1[hash(next)]; ok { // すでに訪問している場合はスキップ
					continue
				}
				// 訪問していない場合は、距離を計算して追加
				used1[hash(next)] = Route{cur_hash, e}
				heap.Push(&pq1, pqi{cur.a + 1, h(cur.state, next, start, kn), next, e})

				if _, ok := used0[hash(next)]; ok {
					find_state = next
					break LOOP
				}
			}
		}
		// fmt.Println("PATH size = ", len(used0), len(used1))
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
	l := len(path)

	state = hash(find_state)
	target = hash(last)
	for state != target {
		e := used1[state].move
		e = get_r_move(e, moves)
		// if e[0] == '-' {
		// 	e = e[1:]
		// } else {
		// 	e = "-" + e
		// }
		path = append(path, e)
		state = used1[state].from
	}
	r := len(path)
	fmt.Println("-->Found", l, "+", r-l, "=", r)
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

	maxdist := 0
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
					maxdist = max(maxdist, int(d[e]))
					q = append(q, int(e))
				}
			}
		}
	}

	fmt.Println("max distance = ", maxdist)
	maxDepth = float64(max(30, maxdist+6))
	return dist
}

// func makeMove(moveList []int16, state []int16) []int16 {
// 	newState := make([]int16, len(state))
// 	for _, e := range moveList {
// 		newState = append(newState, state[e])
// 	}
// 	return newState
// }

// func addRotate(moves map[string][]int16, N, M int) map[string][]int16 {
// 	newMoves := make(map[string][]int16, 0)
// 	for m, xform := range moves {
// 		newMoves[m] = xform
// 		if m[0] == 'r' {
// 			l := make([]int16, M)
// 			for i := 0; i < M; i++ {
// 				l[i] = int16(i)
// 			}
// 			l = makeMove(xform, l)
// 			for i := 2; i < N/2; i++ {
// 				l = makeMove(xform, l)
// 				s := fmt.Sprintf("%d%s", i, m)
// 				newMoves[s] = l
// 			}
// 		}
// 	}
// 	return newMoves
// }

func appendPattern(ptype string, moves map[string][]int16) map[string][]int16 {
	fmt.Println("appendPattern", ptype)
	// if strings.Contains(ptype, "wreath") == false {
	// 	return moves
	// }
	n := 0
	target := map[string]bool{"r": true, "l": true}
	switch ptype {
	case "wreath_100/100":
		n = (100 + 1) / 2
		target = map[string]bool{"r": true, "l": true}
	case "wreath_33/33":
		n = (33 + 1) / 2
		target = map[string]bool{"r": true, "l": true}
	case "globe_1/8":
		n = 2
		target = map[string]bool{"r0": true, "r1": true}
	case "globe_1/16":
		n = 4
		target = map[string]bool{"r0": true, "r1": true}
	// case "globe_3/4":
	// 	n = 3
	// target = map[string]bool{"r0": true, "r1": true, "r2": true, "r3": true}
	case "globe_6/10":
		n = 10
		target = map[string]bool{"r0": true, "r1": true, "r2": true, "r3": true, "r4": true, "r5": true, "r6": true}
	case "globe_3/33":
		n = 8
		target = map[string]bool{"r0": true, "r1": true, "r2": true, "r3": true}
	default:
		return moves
	}

	new := make(map[string][]int16)

	// savepat := map[int]bool{
	// 	1:  true,
	// 	2:  true,
	// 	4:  true,
	// 	8:  true,
	// 	16: true,
	// 	32: true,
	// }

	for e := range moves {
		if target[e] == false {
			new[e] = moves[e]
			continue
		}
		s := moves[e]
		state := make([]int16, len(s))
		for i := 0; i < len(s); i++ {
			state[i] = int16(i)
		}
		// new[e] = s
		for i := 1; i <= n; i++ {
			newState := make([]int16, 0)
			for _, e := range s {
				newState = append(newState, state[e])
			}
			p := e
			if i != 1 {
				p = fmt.Sprintf("%s_%d", e, i)
			}
			// if savepat[i] {
			new[p] = newState
			// }
			state = newState
		}
	}

	return new
}

func convertPath(ptype string, path []string) []string {
	if strings.Contains(ptype, "wreath") == false {
		return path
	}
	tot := 0
	ret := []string{}
	for _, e := range path {
		x := strings.Split(e, "_")
		if len(x) == 1 {
			ret = append(ret, e)
			tot++
			continue
		}
		prefix := x[0]
		postfix := x[1]
		// fmt.Println(prefix, postfix)
		n, _ := strconv.Atoi(postfix)
		sub := []string{}
		for i := 0; i < n; i++ {
			sub = append(sub, prefix)
		}
		// fmt.Println(sub)
		ret = append(ret, sub...)
		tot += n
	}

	fmt.Println(tot)
	return ret
}

var dmap [][]int16
var r *rand.Rand
var maxDepth float64

var ddf Data
var movelist []string

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

	ddf = readCSV(PUZZLE_FILE, *pid)
	info := readInfo(ddf.ptype)
	paths := readPath(SAMPLEDIR, *pid)

	fmt.Println("Path size = ", len(paths), ": ", ddf.ptype, "wild:", ddf.numWild)

	// return
	info = appendPattern(ddf.ptype, info)

	moves := initReverseMoves(info, ddf.ptype)
	// fmt.Println(moves)

	// t := get_r_move("f0", moves)
	// fmt.Println(t)
	// t = get_r_move("r0", moves)
	// fmt.Println(t)
	// return
	// if ddf.ptype != "globe_1/16" {
	// 	fmt.Println("not globe_1/16")
	// 	return
	// }

	for e := range moves {
		movelist = append(movelist, e)
	}

	sort.Slice(movelist, func(i, j int) bool {
		ni, nj := 1, 1
		if s := strings.Split(movelist[i], "_"); len(s) != 1 {
			ni, _ = strconv.Atoi(s[1])
		}
		if s := strings.Split(movelist[j], "_"); len(s) != 1 {
			nj, _ = strconv.Atoi(s[1])
		}
		if ni == nj {
			return movelist[i] < movelist[j]
		}
		return ni < nj
	})

	// r.Shuffle(len(movelist), func(i, j int) {
	// 	movelist[i], movelist[j] = movelist[j], movelist[i]
	// })

	fmt.Println("MoveList", movelist)

	//------------------------------------------------------------
	// 距離テーブルを作成
	N := len(strings.Split(ddf.initial, ";"))
	dmap = make_distance_map(N, moves)
	//------------------------------------------------------------

	// moves = addRotate(info, 33, len(strings.Split(ddf.initial, ";")))
	// moves = initReverseMoves(info)

	fmt.Println(ddf)

	solpat := strings.Split(ddf.solution, ";")
	solLen := len(solpat)
	loop := solLen

	// loop -= 3

	c := []int{}
	idx := []int{}
	for i := 0; i < solLen; i++ {
		if i < 8 {
			// c = append(c, i+1)
			c = append(c, (i+1+3)/4*4)
		} else if i < 14 {
			c = append(c, (i+2)/2*2)
		} else if i >= solLen-4 {
			c = append(c, solLen)
		} else {
			c = append(c, i+1) //(i+1+3)/4*4)
		}

		// c = append(c, i+1)
		idx = append(idx, i)
	}

	c = []int{6, 6, 6, 6, 6, 6, 9, 9, 9, 11, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 31, 31, 31, 32}

	fmt.Println(c)

	for i := 0; i < solLen; i++ {
		// idx[i] = solLen - i - 1
		idx[i] = i
	}

	// for i := 0; i < solLen; i += 2 {
	// 	idx[i] = i / 2
	// }
	// for i := 1; i < solLen; i += 2 {
	// 	idx[i] = i/2 + solLen/2
	// }

	fmt.Println(idx)

	// return
	// return
	// c = []int{
	// 	4, 4, 4, 4, 6, 6, 8, 8,
	// 	10, 10, 12, 12,
	// 	13, 14, 15, 16,
	// 	17, 18, 19, 20,
	// 	21, 22, 23, 24,
	// 	25, 26, 27, 28,
	// 	29, 30, 32, 32}
	newpath := []string{}
	// newpath = strings.Split("d2 d2 -r4 f4 f0 f0 r0 r0 -r4 -d0 r4 -d0 -f4 r0 f4 f0 f0 d0 d0 -f0 d0 d0 f0 f0 d0 -f4 -d4 -r0 d4 -r0 f4 r0 -d2 d0 -f4 -d0 -f4 d2 r0 r0 -f0 -d4 f0 r0 r0 f4 f4 f0 d2 d2 f0 f0 d2 f0 d2 r1 f1 f2 -d0 -f2 d0 -r4 -d3 r4 f3 f0 f0 r1 f0 f0 r3 f4 f4 -r2 f4 r2 f4 -f0 -r1 f0 -f3 -d4 -r1 d4 d2 -r4 -d2 r4 d3 d3 -r0 -f1 r0 -f1 -f1 -d4 r3 r3 d4 f1 f1 -f4 d0 r2 -d0 -r2 f4 -f2 -d2 -r0 d2 r0 f2 f0 r3 f0 f0 -r3 f0 -d0 -f0 -r2 f0 d0 -f0 r2 f0 -d3 -f0 r1 f0 f0 -r1 -f0 -f0 -r4 -f4 -r1 f4 r4 f0 -r0 -f2 r0 r0 f2 -r0 -d0 -f4 -d3 f4 f4 -d1 -f4 d0 -r3 -f1 -d3 r3 f1 -f1 r2 r2 -f1 r2 r2 f1 f1 r1 d1 -r1 f2 f2 -r1 f2 f2 r1 -d0 -f2 d3 d3 f2 d0 r3 -d3 -r3 -r2 f0 f0 d3 d3 f0 f0 r2 -f1 r0 r0 d3 d3 r0 r0 f1 -f1 -d3 r0 r0 d3 r0 r0 f1 -d0 -f2 -d1 f0 f0 d1 f0 f0 f2 d0 -d0 -r3 d1 r4 r4 -d1 r4 r4 r3 d0 -f2 -d1 f0 f0 d1 f0 f0 f2 -f2 d3 f4 f4 -d3 f4 f4 f2 -f3 -d3 r0 r0 d3 r0 r0 f3 -d2 -f3 -d2 f0 f0 d2 f0 f0 f3 d2 -d0 -r1 d1 r4 r4 -d1 r4 r4 r1 d0 d1 r2 r2 d1 r2 r2 -f3 r1 f3 f3 -r1 -f3 -f2 r3 f2 f2 -r3 -f2 f1 f1 -d2 f1 f1 d2 -f0 -d3 r1 r1 d3 r1 r1 f0 -d1 f2 f2 d1 f2 f2 -d1 -r4 -f1 -f1 d1 d1 f1 f1 d1 d1 r4 d1 -r0 -d3 -d3 f1 f1 d3 d3 f1 f1 r0 -d2 f2 -r1 f2 f2 r1 f2 d2 -f3 -f3 -d1 f4 f4 d1 f4 f4 f3 f3 -d1 -r2 -d2 -d2 f3 d2 d2 -f3 r2 d1 -d1 -f3 -r2 f3 f3 r2 -f3 d1 -r4 -f1 -f1 r4 -d1 -r4 f1 f1 r4 d1 -d1 -r3 -r3 -d1 -r4 -r4 d1 r3 r3 d1 r4 r4 -r0 -d3 -d3 r0 -d1 -r0 d3 d3 r0 d1 r4 r4 d3 r4 r4 -d3 -d3 -f4 -d2 f4 d3 -f4 d2 f4 -d3 -f3 -f3 d3 f4 -d3 f3 f3 d3 -f4 -d2 -r4 -d2 -d2 -f1 -f1 d2 d2 f1 f1 r4 d2 -f2 r3 f2 -r4 -f2 -r3 f2 r4 -d1 -f3 -f3 d1 f4 -d1 f3 f3 d1 -f4 -f1 r3 f1 -r4 -f1 -r3 f1 r4 -d1 -f1 r3 f1 -r4 -f1 -r3 f1 r4 d1 -d2 -d2 -r0 -d1 -d1 -f2 -f2 d1 d1 f2 f2 r0 d2 d2 -d1 -f4 -d1 -f1 -f1 d1 f4 -d1 f1 f1 d1 d1 -d1 -r4 -r4 -f1 r2 f1 r4 r4 -f1 -r2 f1 d1 -d1 -f4 -f4 d1 -f0 -f0 -d1 f4 f4 d1 f0 f0 -f0 r2 f0 -r0 -r0 -f0 -r2 f0 r0 r0 -f4 r1 -f4 -r0 -r0 f4 -r1 -f4 r0 r0 f4 f4 -d1 -r4 -r4 d3 -r0 -r0 -d3 r4 r4 d3 r0 r0 -d3 d1", " ")
	// sst := ddf.initial
	// for _, e := range newpath {
	// 	sst = applyMove(e, sst, moves)
	// }
	// tt := strings.Split(ddf.solution, ";")
	// ss := strings.Split(sst, ";")

	// ssx := []int{}
	// idx = []int{}
	// for i := 0; i < N; i++ {
	// 	if tt[i] != ss[i] {
	// 		ssx = append(ssx, i)
	// 	} else {
	// 		idx = append(idx, i)
	// 	}
	// }
	// idx = append(idx, ssx...)
	// fmt.Println(ssx)

	for n := 0; n < loop; n++ {
		solution := make([]string, solLen)
		cnt := c[n]
		for i := 0; i < solLen; i++ {
			if i < cnt {
				solution[idx[i]] = solpat[idx[i]]
			} else {
				solution[idx[i]] = "x"
			}
		}

		solState := strings.Join(solution, ";")
		// fmt.Println(solLen)
		fmt.Println("STATE = ", solState)

		state := solState

		for i := len(paths) - 1; i >= 0; i-- {
			e := paths[i]
			// fmt.Println(n, e)
			e = get_r_move(e, moves)
			// fmt.Println(e, moves[e])
			// if e[0] == '-' {
			// 	e = e[1:]
			// } else {
			// 	e = "-" + e
			// }
			state = applyMove(e, state, moves)
		}

		mstate := ddf.initial
		for _, e := range newpath {
			state = applyMove(e, state, moves)
			mstate = applyMove(e, mstate, moves)
		}

		fmt.Println("INIT  = ", state)

		// s0 := solution
		// s1 := strings.Split(mstate, ";")
		// ok := true
		// for i := 0; i < solLen; i++ {
		// 	if s0[i] == "x" {
		// 		continue
		// 	}
		// 	if s0[i] != s1[i] {
		// 		ok = false
		// 	}
		// }

		// fmt.Println(state)
		// fmt.Println(mstate)
		// fmt.Println(ok)
		// if ok {
		// 	continue
		// }

		if state == solState {
			continue
		}

		fmt.Println("current  = ", mstate)
		fmt.Println("solution = ", ddf.solution)

		if validCheck(mstate, ddf.solution, ddf.numWild) == true {
			break
		}

		ret, ok := bsf(
			state, solState,
			ddf.numWild, moves, *limit, *timeout)

		if ok == false {
			return
		}

		newpath = append(newpath, ret...)
		fmt.Println("n = ", n, "path = ", ret, len(newpath))
	}

	fmt.Println(newpath)
	// fmt.Println(*limit)
	// newpath := paths
	writePath("../../tmp", -1, newpath)
	newpath = convertPath("wreath", newpath)
	writePath("../../tmp", -2, newpath)

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
	writePath("../../tmp", *pid, newpath)

	// fmt.Println(SAMPLEDIR)
	// writePath(SAMPLEDIR, *pid, newpath)

	// if score < 0 :
	// 	print("Update.")
	// 	with open(f"check/{pid}.txt", "w") as f :
	// 		f.write(".".join(new_path))

}
