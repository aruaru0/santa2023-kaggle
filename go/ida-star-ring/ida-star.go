package main

import (
	"bufio"
	"crypto/sha1"
	"encoding/csv"
	"flag"
	"fmt"
	"log"
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

// --------------------------------------------------
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

func validCheckWithX(state, target string) bool {
	ok := true
	for i := 0; i < len(state); i++ {
		if state[i] == 'x' || target[i] == 'x' {
			continue
		}
		if state[i] != target[i] {
			return false
		}
	}
	return ok
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

// var dmap [][]int16
var r *rand.Rand

// var maxDepth float64

var ddf Data
var find []string
var moves map[string][]int16

var used map[string]bool

func masked(cur, mask string) string {
	ret := []byte{}
	for i := 0; i < len(cur); i++ {
		if mask[i] == 'x' {
			ret = append(ret, 'x')
		} else {
			ret = append(ret, cur[i])
		}
	}
	return string(ret)
}

func maskedCheck(cur, mask, target string, num int) bool {
	cnt := 0
	wild := 0
	for i := 0; i < len(cur); i++ {
		if mask[i] == 'x' {
			if cur[i] != target[i] {
				wild++
			}
		} else if cur[i] != target[i] {
			cnt++
		}
	}

	if cnt+wild <= num {
		return true
	}
	if cnt == 0 {
		return true
	}
	return false
}

func hash(state string) [20]byte {
	return sha1.Sum([]byte(state))
}

func rule(next string, paths []string) bool {
	n := len(paths)
	if n == 0 {
		return true
	}

	sameMax := 0
	same := 0
	prevMove := ""
	cng := 0
	for _, e := range paths {
		if e == prevMove {
			same++
		} else {
			same = 0
			cng++
		}
		sameMax = max(sameMax, same)
		prevMove = e
	}
	if prevMove == next {
		sameMax = max(sameMax, same+1)
	}

	if sameMax > maxLength/4 {
		return false
	}
	// if cng > 10 { // 8回もlとrを交互に切り替えて動かすパターンはない
	// 	return false
	// }

	prev := paths[n-1]
	if prev[0] == '-' && prev[1:] == next {
		return false
	}
	if next[0] == '-' && next[1:] == prev {
		return false
	}
	// switch {
	// case prev == "-r" && next == "r":
	// 	fallthrough
	// case prev == "r" && next == "-r":
	// 	fallthrough
	// case prev == "l" && next == "-l":
	// 	fallthrough
	// case prev == "-l" && next == "l":
	// 	return false
	// }
	return true
}

var ng map[[20]byte]bool
var limitNgSize int
var maxLength int

// var moveList = []string{"r", "l", "-r", "-l"}

var moveList = map[string][]string{
	"-":  []string{"l", "r", "-l", "-r"},
	"BB": []string{"r", "l", "-r", "-l"},
	"BA": []string{"r", "l", "-r", "-l"},
	"BC": []string{"r", "l", "-r", "-l"},
	"AB": []string{"l", "r", "-l", "-r"},
	"CB": []string{"l", "r", "-l", "-r"},
	"AA": []string{"l", "r", "-l", "-r"},
	"CC": []string{"l", "r", "-l", "-r"},
	"AC": []string{"l", "r", "-l", "-r"},
	"CA": []string{"l", "r", "-l", "-r"},
}

func checkCnt(cur, prev, target string) bool {
	cur_cnt, prev_cnt := 0, 0
	// rc := ""
	// rp := ""
	for i := 0; i < len(cur); i++ {
		if target[i] == 'B' {
			if cur[i] == target[i] {
				cur_cnt++
			}
			if prev[i] == target[i] {
				prev_cnt++
			}
			// if cur[i] == 'B' {
			// 	rc += string(cur[i])
			// } else {
			// 	rc += " "
			// }
			// if prev[i] == 'B' {
			// 	rp += string(prev[i])
			// } else {
			// 	rp += " "
			// }
		}
	}

	if prev_cnt < cur_cnt {
		// 	fmt.Println("---------------")
		// 	fmt.Println("check")
		// 	fmt.Println(rc)
		// 	fmt.Println(rp)
		// 	fmt.Println("---------------")
		return true
	}
	return false
}

func dfs(cur, prev string, mask string, depth int, paths []string) bool {
	if maskedCheck(cur, mask, ddf.solution, ddf.numWild) {
		// if checkCnt(cur, prev, ddf.solution) {
		find = paths
		return true
	}
	if depth == 0 {
		if len(ng) < limitNgSize {
			ng[hash(cur)] = true // チェック済みリスト
			if len(ng) == limitNgSize {
				fmt.Println("clear cache")
				ng = make(map[[20]byte]bool)
			}
		}
		return false
	}

	// last := "-"
	// if len(paths) != 0 {
	// 	last = paths[len(paths)-1]
	// }
	// x := "-"
	x := string([]byte{cur[0], cur[50]})
	for _, e := range moveList[x] {
		if rule(e, paths) == false {
			continue
		}
		state := applyMove(e, cur, moves)
		if ng[hash(state)] {
			continue
		}
		if _, ok := used[state]; ok {
			continue
		}
		used[state] = true
		ret := dfs(state, prev, mask, depth-1, append(paths, e))
		delete(used, state)
		if ret {
			return true
		}
	}

	if len(ng) < limitNgSize {
		ng[hash(cur)] = true // チェック済みリスト
		if len(ng) == limitNgSize {
			fmt.Println("clear cache")
			ng = make(map[[20]byte]bool)
		}
	}

	return false
}

// // dfsを使ってキャッシュする
// func dfs2(cur string, depth int, paths []string) {
// 	if depth == 0 {
// 		return
// 	}

// 	for _, e := range moveList['-'] {
// 		if rule(e, paths) == false {
// 			continue
// 		}
// 		state := applyMove(e, cur, moves)
// 		hashed_state := hash(state)
// 		if _, ok := cached[hashed_state]; ok {
// 			continue
// 		}
// 		cached[hashed_state] = append(paths, e)
// 		dfs2(state, depth-1, append(paths, e))
// 	}
// }

// var cached map[[20]byte][]string

func main() {
	r = rand.New(rand.NewSource(time.Now().UnixNano()))
	pid := flag.Int("problem_id", -1, "")
	csvFile := flag.String("path_dir", "", "")
	timeout := flag.String("timeout", "300s", "")
	maxdepth := flag.Int("depth", 20, "")
	limit := flag.Int("limit", 1000000, "")

	flag.Parse()

	limitNgSize = *limit
	fmt.Println("Limit", limitNgSize)

	if *pid == -1 {
		fmt.Println("need --problem_id")
		return
	}

	PUZZLE_FILE := "../../data/puzzles.csv"
	SAMPLEDIR := *csvFile

	ddf = readCSV(PUZZLE_FILE, *pid)
	info := readInfo(ddf.ptype)
	paths := readPath(SAMPLEDIR, *pid)

	fmt.Println("Path size = ", len(paths), ": ", ddf.ptype, "wild:", ddf.numWild)

	moves = initReverseMoves(info, ddf.ptype)

	// moves = addRotate(info, 33, len(strings.Split(ddf.initial, ";")))
	// moves = initReverseMoves(info)

	fmt.Println(ddf, timeout)

	solpat := strings.Split(ddf.solution, ";")
	solLen := len(solpat)
	maxLength = solLen
	// loop -= 3

	// depth := 3
	mask := make([]string, solLen)
	for i := 0; i < solLen; i++ {
		mask[i] = "x"
	}
	fmt.Println(mask)

	newpath := []string{}

	fmt.Println(ddf.solution, len(newpath))

	solState := strings.Split(ddf.solution, ";")

	// statex := "A;B;B;B;A;B;A;A;A;A;B;B;A;A;A;A;B;A;A;B;B;A;A;A;A;B;C;A;A;A;A;A;A;A;A;A;A;A;A;A;A;A;A;A;A;A;A;A;A;A;A;B;A;A;A;A;B;A;B;A;B;A;A;B;A;A;B;A;B;B;A;A;B;A;B;A;A;A;A;B;A;A;B;A;B;A;A;A;A;B;B;A;B;A;A;A;B;B;B;A;A;A;A;A;A;A;A;A;B;A;A;B;B;B;B;B;A;B;B;B;A;A;B;C;A;B;A;A;A;B;B;A;A;A;B;A;A;A;A;B;B;A;A;A;B;A;B;B;B;B;B;B;B;B;B;B;B;B;B;B;B;B;B;B;B;B;B;B;B;B;B;B;B;B;B;B;B;B;B;B;B;B;B;B;B;B;B;B;B;B;B;B;B;B;B;B;B;B"
	// fmt.Println("-----")
	// fmt.Println(statex)
	// statex = applyMove("l", statex, moves)
	// fmt.Println(statex)
	// statex = applyMove("r", statex, moves)
	// fmt.Println(statex)

	// offset := (solLen-2)/2 + 2
	for i := 0; i < solLen; i++ {
		state := ddf.initial
		for _, e := range newpath {
			state = applyMove(e, state, moves)
		}
		if validCheck(state, ddf.solution, ddf.numWild) == true {
			break
		}

		// if i < (solLen-2)/2 {
		// mask[(i+offset)%solLen] = solState[(i+offset)%solLen]
		// } else {
		mask[solLen-1-i] = solState[solLen-1-i]
		// }
		fmt.Println("START :", state)
		fmt.Println("TARGET:", ddf.solution)

		maskstr := strings.Join(mask, ";")

		fmt.Println("MASK  :", maskstr)

		// s := []byte{state[0], state[50]}
		// fmt.Println("C zone = ", string(s))
		//

		for depth := 1; depth < *maxdepth; depth++ {
			startTime := time.Now()
			fmt.Print("Depth .... ", depth)
			used = make(map[string]bool)
			ng = make(map[[20]byte]bool)
			used[state] = true
			ok := dfs(state, state, maskstr, depth, []string{})
			fmt.Println(": time = ", time.Since(startTime))
			if ok {
				fmt.Println(ok, find, len(find))
				newpath = append(newpath, find...)
				break
			}
		}
		fmt.Println(newpath)
	}

	fmt.Println(newpath)

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

	// if score < 0 {
	// 	fmt.Println("Update...")
	// 	writePath(SAMPLEDIR, *pid, newpath)
	// }
	writePath("../../tmp", *pid, newpath)

}
