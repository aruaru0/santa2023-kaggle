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

// --------------------------------------------------
func initReverseMoves(moves map[string][]int16, ptype string) map[string][]int16 {
	// flg := strings.Contains(ptype, "globe_")
	// if flg {
	// 	fmt.Println("type flg = ", flg)
	// }
	flg := false

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

func applyMove(move string, state string, index []int16, moves map[string][]int16) (string, []int16) {
	m := move
	s := strings.Split(state, ";")

	moveList := moves[m]
	newState := []string{}
	newIndex := []int16(nil)
	if index != nil {
		newIndex = []int16{}
	}
	for _, e := range moveList {
		newState = append(newState, s[e])
		if index != nil {
			newIndex = append(newIndex, index[e])
		}
	}
	return strings.Join(newState, ";"), newIndex
}

func applyMoveByte(move string, state, index []int16, moves map[string][]int16) ([]int16, []int16) {
	m := move
	s := state

	moveList := moves[m]
	newState := []int16{}
	newIndex := []int16(nil)
	if index != nil {
		newIndex = []int16{}
	}
	for _, e := range moveList {
		newState = append(newState, s[e])
		if index != nil {
			newIndex = append(newIndex, index[e])
		}
	}
	return newState, newIndex
}

func validCheckWithX(state, target string) bool {
	ok := true
	for i := 0; i < len(state); i++ {
		if state[i] == '.' || target[i] == '.' {
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

// -----------------------------------------------------------------------------------------------------------------
// CUBE index maker
// -----------------------------------------------------------------------------------------------------------------
type cubeEdge struct {
	x, y int
}

type cubeCorner struct {
	x, y, z int
}

func makeCubeIndex(n int) ([]int, []int) {
	ce := make([]cubeEdge, 0)
	ce2 := make([]cubeEdge, 0)
	ce3 := make([]cubeEdge, 0)
	cc := make([]cubeCorner, 0)

	U, F, R, B, L, D := 0, n*n, 2*n*n, 3*n*n, 4*n*n, 5*n*n
	var u, f, r, b, l, d int
	// Corner
	cc = append(cc, cubeCorner{0 + U, 0 + L, n - 1 + B})
	cc = append(cc, cubeCorner{n - 1 + U, n - 1 + R, 0 + B})
	cc = append(cc, cubeCorner{n*(n-1) + U, 0 + F, n - 1 + L})
	cc = append(cc, cubeCorner{n*n - 1 + U, n - 1 + F, 0 + R})
	cc = append(cc, cubeCorner{0 + D, n*(n-1) + F, n*n - 1 + L})
	cc = append(cc, cubeCorner{n - 1 + D, n*n - 1 + F, n*(n-1) + R})
	cc = append(cc, cubeCorner{n*(n-1) + D, n*(n-1) + L, n*n - 1 + B})
	cc = append(cc, cubeCorner{n*n - 1 + D, n*n - 1 + R, n*(n-1) + B})

	fmt.Println(cc)

	// Edges
	// UF
	u, f = n*(n-1)+1, 1
	for i := 0; i < n-2; i++ {
		ce = append(ce, cubeEdge{u + U, f + F})
		u++
		f++
	}
	// UR
	u, r = n*n-1-n, 1
	for i := 0; i < n-2; i++ {
		ce = append(ce, cubeEdge{u + U, r + R})
		u -= n
		r++
	}
	// UB
	u, b = 1, n-2
	for i := 0; i < n-2; i++ {
		ce = append(ce, cubeEdge{u + U, b + B})
		u++
		b--
	}
	// UL
	u, l = n, 1
	for i := 0; i < n-2; i++ {
		ce = append(ce, cubeEdge{u + U, l + L})
		u += n
		l++
	}

	// DF
	d, f = 1, n*(n-1)+1
	for i := 0; i < n-2; i++ {
		ce3 = append(ce3, cubeEdge{d + D, f + F})
		d++
		f++
	}
	// DR
	d, r = 2*n-1, n*(n-1)+1
	for i := 0; i < n-2; i++ {
		ce3 = append(ce3, cubeEdge{d + D, r + R})
		d += n
		r++
	}
	// DB
	d, b = n*(n-1)+1, n*n-2
	for i := 0; i < n-2; i++ {
		ce = append(ce, cubeEdge{d + D, b + B})
		d++
		b--
	}
	// DL
	d, l = n, n*n-2
	for i := 0; i < n-2; i++ {
		ce3 = append(ce3, cubeEdge{d + D, l + L})
		d += n
		l--
	}

	// FR
	f, r = n*2-1, n*1
	for i := 0; i < n-2; i++ {
		ce2 = append(ce2, cubeEdge{f + F, r + R})
		f += n
		r += n
	}
	// FL
	f, l = n*1, n*2-1
	for i := 0; i < n-2; i++ {
		ce2 = append(ce2, cubeEdge{f + F, l + L})
		f += n
		l += n
	}
	// RB
	r, b = n*2-1, n*1
	for i := 0; i < n-2; i++ {
		ce2 = append(ce2, cubeEdge{r + R, b + B})
		r += n
		b += n
	}
	// BL
	b, l = n*2-1, n*1
	for i := 0; i < n-2; i++ {
		ce2 = append(ce2, cubeEdge{b + B, l + L})
		b += n
		l += n
	}

	// make
	ret := make([]int, 0)
	cnt := make([]int, 0)
	m := make(map[int]bool)
	if n%2 == 1 {
		pos := n * n / 2
		for i := 0; i < 6; i++ {
			ret = append(ret, pos)
			m[pos] = true
			cnt = append(cnt, 1)
			pos += n * n
		}
	}

	for _, e := range cc {
		m[e.x] = true
		m[e.y] = true
		m[e.z] = true
	}
	for _, e := range ce {
		m[e.x] = true
		m[e.y] = true
	}
	for _, e := range ce2 {
		m[e.x] = true
		m[e.y] = true
	}
	for _, e := range ce3 {
		m[e.x] = true
		m[e.y] = true
	}

	// コーナーを揃える
	for _, e := range cc {
		ret = append(ret, e.x)
		ret = append(ret, e.y)
		ret = append(ret, e.z)
		cnt = append(cnt, 3)
	}

	// 上面内側
	pat := []int{0} //, 1, 2, 3, 4}
	for _, p := range pat {
		off := p * n * n
		for i := off; i < off+n*n; i++ {
			if m[i] == false {
				ret = append(ret, i)
				cnt = append(cnt, 1)
			}
		}
	}

	// 上面エッジ
	randRand.Shuffle(len(ce), func(i, j int) {
		ce[i], ce[j] = ce[j], ce[i]
	})
	for _, e := range ce {
		ret = append(ret, e.x)
		ret = append(ret, e.y)
		cnt = append(cnt, 2)
	}

	// 下面内側
	pat = []int{5}
	for _, p := range pat {
		off := p * n * n
		for i := off; i < off+n*n; i++ {
			if m[i] == false {
				ret = append(ret, i)
				cnt = append(cnt, 1)
			}
		}
	}
	randRand.Shuffle(len(ce3), func(i, j int) {
		ce3[i], ce3[j] = ce3[j], ce3[i]
	})
	// 下面エッジ
	for _, e := range ce3 {
		ret = append(ret, e.x)
		ret = append(ret, e.y)
		cnt = append(cnt, 2)
	}

	// 側面エッジ
	randRand.Shuffle(len(ce2), func(i, j int) {
		ce2[i], ce2[j] = ce2[j], ce2[i]
	})
	for _, e := range ce2 {
		ret = append(ret, e.x)
		ret = append(ret, e.y)
		cnt = append(cnt, 2)
	}
	// 側面内側
	// pat = []int{1, 2, 3, 4}
	pat = []int{1, 2, 3, 4}
	pos := make([]int, 0)
	for _, p := range pat {
		off := p * n * n
		for i := off; i < off+n*n; i++ {
			if m[i] == false {
				// ret = append(ret, i)
				pos = append(pos, i)
				cnt = append(cnt, 1)
			}
		}
	}
	randRand.Shuffle(len(pos), func(i, j int) {
		pos[i], pos[j] = pos[j], pos[i]
	})
	ret = append(ret, pos...)

	// if ddf.ptype == "cube_5/5/5" {
	// 	sort.Slice(pos, func(i, j int) bool {
	// 		flgI := 2
	// 		flgJ := 2
	// 		for x := 0; x < 6; x++ {
	// 			if 10+x*25 <= pos[i] && pos[i] <= 10+x*25+4 {
	// 				flgI = 0
	// 			}
	// 			if 10+x*25 <= pos[j] && pos[j] <= 10+x*25+4 {
	// 				flgJ = 0
	// 			}
	// 			if pos[i] == 12+x*25-5 || pos[i] == 12+x*25+5 {
	// 				flgI = 1
	// 			}
	// 			if pos[j] == 12+x*25-5 || pos[j] == 12+x*25+5 {
	// 				flgJ = 1
	// 			}
	// 		}
	// 		// if flgI == flgJ {
	// 		// 	return pos[i] < pos[j]
	// 		// }
	// 		return flgI < flgJ
	// 	})
	// 	fmt.Println("SORTED:", pos)
	// 	randRand.Shuffle(len(pos), func(i, j int) {
	// 		if i >= 8 && j >= 8 {
	// 			pos[i], pos[j] = pos[j], pos[i]
	// 		}
	// 	})
	// }

	for i := 1; i < len(cnt); i++ {
		cnt[i] += cnt[i-1]
	}

	return ret, cnt
}

type CubeState struct {
	flg bool // キューブの中心が揃っているかどうかのフラグ
	cn  int  //　キューブの中心（偶数の場合は-1)
	m   map[string]bool
}

func makeCubeStatePattern(n int) {
	cubeState.m = make(map[string]bool)
	if n%2 == 0 {
		cubeState.cn = -1
		return
	}
	cubeState.cn = n / 2
	scn := strconv.FormatInt(int64(cubeState.cn), 10)
	for _, e := range []string{"f", "r", "d"} {
		s := e + scn
		cubeState.m[s] = true
		cubeState.m["-"+s] = true
		cubeState.m[s+"_2"] = true
		cubeState.m["-"+s+"_2"] = true
	}
}

var cubeState CubeState

//-----------------------------------------------------------------------------------------------------------------

// var dmap [][]int16
var randRand *rand.Rand

// var maxDepth float64

var ddf Data
var find []string
var moves map[string][]int16

var used map[[20]byte]bool

func masked(cur, mask string) string {
	ret := []byte{}
	for i := 0; i < len(cur); i++ {
		if mask[i] == '.' {
			ret = append(ret, '.')
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
		if mask[i] == '.' {
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

func toByte(p []int16) []byte {
	ret := []byte{}
	for _, e := range p {
		ret = append(ret, byte(e&255))
		ret = append(ret, byte(e>>8&255))
	}
	return ret
}

func hash(state []int16) [20]byte {
	return sha1.Sum(toByte(state))
}

func rule(next string, paths []string) bool {
	n := len(paths)
	if ddf.ptype[:4] == "cube" {

		// 中心は回転させない
		if cubeState.flg && cubeState.m[next] {
			return false
		}

		// -r_2などの符号付きの180度回転は検索をカット
		// fmt.Print(next, strings.Split(next, "_"), "--->")
		if s := strings.Split(next, "_"); len(s) == 2 && s[1] == "2" && s[0][0] == '-' {
			// fmt.Println(next, "skip")
			return false
		}
		// fmt.Println(next)
	}

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

	// １手前と同じ場所を逆方向へ回転させるのはなし
	prev := paths[n-1]
	if prev[0] == '-' && prev[1:] == next {
		return false
	}
	if next[0] == '-' && next[1:] == prev {
		return false
	}

	// for cube
	if ddf.ptype[:4] == "cube" {
		// 中心は回転させない
		if cubeState.flg && cubeState.m[next] {
			return false
		}

		// -r_2などの符号付きの180度回転は検索をカット
		if s := strings.Split(next, "_"); len(s) == 2 && s[1] == "2" && s[0][0] == '-' {
			// fmt.Println(next, "skip")
			return false
		}

		if len(paths) >= 2 { // 3回連続で同じ操作はなし
			if paths[n-1] == paths[n-2] && paths[n-1] == next {
				return false
			}
		}
		e := strings.Split(paths[n-1], "_")[0]
		v := strings.Split(next, "_")[0]
		if e == v { // 同じ方向に2回回すはなし（半回転を導入した場合）
			return false
		}

		// -r0 r1 r2 r3 -r0の最後のr0はできない（途中に他の方向の回転がないものは消す）
		cur := v
		curinv := v
		var target string
		if curinv[0] == '-' {
			curinv = curinv[1:]
			target = string(curinv[0])
		} else {
			target = string(curinv[0])
			curinv = "-" + curinv
		}
		for i := len(paths) - 1; i >= 0; i-- {
			if strings.Contains(paths[i], target) == false {
				break
			}
			x := strings.Split(paths[i], "_")[0]
			if x == cur || x == curinv {
				return false
			}
		}
	}

	// for wealth
	if ddf.ptype[:5] == "globe" {
		// -f と　fは同じなので2回は繰り返さない
		e := next
		if e[0] == '-' {
			e = e[1:]
		}
		v := paths[n-1]
		if v[0] == '-' {
			v = v[1:]
		}
		if e == "f" && e == v {
			return false
		}
		// 同じ方向へr0_2, r0_4みたいな繰り返しと、f0, f0みたいな繰り返しはNG
		x := strings.Split(paths[n-1], "_")[0]
		y := strings.Split(next, "_")[0]
		if x == y {
			return false
		}
		// r1, r2, r3, r1みたいなやつはなし
		v = strings.Split(next, "_")[0]
		cur := v
		curinv := v
		var target string
		if curinv[0] == '-' {
			curinv = curinv[1:]
			target = string(curinv[0])
		} else {
			target = string(curinv[0])
			curinv = "-" + curinv
		}
		if cur[0] == 'r' {
			for i := len(paths) - 1; i >= 0; i-- {
				if strings.Contains(paths[i], target) == false {
					break
				}
				x := strings.Split(paths[i], "_")[0]
				if x == cur || x == curinv {
					return false
				}
			}
		}
		// f0, fx xは独立 f0 はなし
	}

	return true
}

var ng map[[20]byte]bool
var limitNgSize int
var maxLength int

func checkCnt(cur, target []int16) bool {
	cnt := 0
	for i := 0; i < len(cur); i++ {
		if target[i] == -1 {
			continue
		}
		if cur[i] != target[i] {
			cnt++
		}
	}

	if cnt == 0 {
		return true
	}
	return false
}

var movelist []string

func dfs(cur, target, curindex []int16, depth int, paths []string) bool {
	// fmt.Println("\ndfs------")
	// fmt.Println(cur, target)
	if checkCnt(cur, target) {
		// if checkCnt(cur, prev, ddf.solution) {
		find = paths
		return true
	}
	// hashed_cur := hash(cur)
	// if _, flg := cashed[hashed_cur]; flg {
	if hashed_cur, flg := match(cur); flg {
		// fmt.Println("find...")
		find = paths
		path := cashed[hashed_cur]
		// fmt.Println(cur)
		// fmt.Println(target, nextPos)
		// fmt.Println(path)

		for i := len(path) - 1; i >= 0; i-- {
			e := path[i]
			if e[0] == '-' {
				e = e[1:]
			} else {
				e = "-" + e
			}
			find = append(find, e)
		}
		return true
	}

	// // 最小の残り距離がdepthより大きい場合は探索を辞める
	// if calcDistance(cur, target) > depth {
	// 	return false
	// }

	if depth == 0 {
		if len(ng) < limitNgSize {
			ng[hash(cur)] = true // チェック済みリスト
			if len(ng) == limitNgSize {
				fmt.Println("cache filled")
				// ng = make(map[[20]byte]bool)
			}
		}
		return false
	}

	for _, e := range movelist {
		if rule(e, paths) == false {
			continue
		}
		state, index := applyMoveByte(e, cur, curindex, moves)
		// 最小の残り距離がdepthより大きい場合は探索を辞める
		if calcDistanceIndex(state, index) > depth {
			return false
		}

		hashed_state := hash(state)
		if ng[hashed_state] {
			continue
		}
		if _, ok := used[hashed_state]; ok {
			continue
		}
		used[hashed_state] = true
		ret := dfs(state, target, index, depth-1, append(paths, e))
		delete(used, hashed_state)
		if ret {
			return true
		}
	}

	if len(ng) < limitNgSize {
		ng[hash(cur)] = true // チェック済みリスト
		if len(ng) == limitNgSize {
			fmt.Println("cache filled")
			// ng = make(map[[20]byte]bool)
		}
	}

	return false
}

func bsf(init, target, curindex []int16, depth int, paths []string) {
	q := [][]int16{target}
	// hashed_init := hash(init)
	// fmt.Println("BSF-----")
	cashed[hash(target)] = []string{}
	// fmt.Println("target", target, cashed[hash(target)])
	fmt.Print("BSF:")
	for d := 0; d < depth; d++ {
		nq := [][]int16{}
		for _, cur := range q {
			path := cashed[hash(cur)]
			for _, e := range movelist {
				if rule(e, path) == false {
					continue
				}
				state, _ := applyMoveByte(e, cur, curindex, moves)
				hashed_state := hash(state)
				if _, ok := cashed[hashed_state]; ok {
					continue
				}
				// 複製しないと壊れるので注意
				tmp := make([]string, len(path))
				copy(tmp, path)
				cashed[hashed_state] = append(tmp, e)
				nq = append(nq, state)

				// fmt.Println(state, tmp, e)
				// if _, flg := cashed[hashed_init]; flg {

				// マッチングのチェック
				// if _, flg := match(init); flg {
				// 	return
				// }
				if _, flg := cashed[hash(init)]; flg {
					fmt.Print("bsf(cached)")
					return
				}
				if len(cashed) > limit_size {
					fmt.Print("bsf(size limit)")
					return
				}
				if len(cashed)%10000 == 0 {
					fmt.Print(".")
					if len(cashed)%100000 == 0 {
						fmt.Print(len(cashed))
					}
				}
			}
		}
		q = nq
	}
	fmt.Println("")
}

// とりあえず、新しいものは+100するように改造中
// マッチングアルゴリズムをよく考えないとどうしょうもないことに気づいた・・・・
func match(init []int16) ([20]byte, bool) {
	hashval := hash(init)
	if _, flg := cashed[hashval]; flg {
		return hashval, true
	}
	return [20]byte{}, false
}

// func match(init []byte) ([20]byte, bool) {
// 	// fmt.Println("match ------- ")
// 	mask := []byte{}
// 	p := make([]int, 0)
// 	chr := byte(255)
// 	for i := 0; i < len(init); i++ {
// 		if init[i] == 255 || init[i] < 100 {
// 			mask = append(mask, init[i])
// 		} else {
// 			mask = append(mask, 255)
// 			p = append(p, i)
// 			chr = init[i]
// 		}
// 	}

// 	// fmt.Println(mask)
// 	// fmt.Println("chr", chr, p)

// 	prev := -1
// 	find := false
// 	ret := [20]byte{}
// 	for _, e := range p {
// 		if prev != -1 {
// 			mask[prev] = 255
// 		}
// 		mask[e] = chr
// 		// fmt.Println(e, "->", mask)
// 		hash_val := hash(mask)
// 		if _, ok := cashed[hash_val]; ok {
// 			if find == false {
// 				ret = hash_val
// 			}
// 			find = true
// 			if len(cashed[ret]) > len(cashed[hash_val]) {
// 				ret = hash_val
// 			}
// 			// return hash_val, true
// 		}
// 		prev = e
// 	}

// 	return ret, find
// }

// func match(init, target []byte, pos int) ([20]byte, bool) {
// 	mask := make([]byte, len(target))
// 	copy(mask, target)
// 	fmt.Println("match ------- ")
// 	fmt.Println(mask, target, pos)

// 	chr := mask[pos]
// 	mask[pos] = 255
// 	fmt.Println("init", init)
// 	fmt.Println("mask", mask)
// 	p := []int{}
// 	for i := 0; i < len(init); i++ {
// 		if init[i] == chr {
// 			p = append(p, i)
// 		}
// 	}
// 	prev := -1
// 	find := false
// 	ret := [20]byte{}
// 	for _, e := range p {
// 		if prev != -1 {
// 			mask[prev] = 255
// 		}
// 		mask[e] = chr
// 		hash_val := hash(mask)
// 		if _, ok := cashed[hash_val]; ok {
// 			if find == false {
// 				ret = hash_val
// 			}
// 			find = true
// 			if len(cashed[ret]) > len(cashed[hash_val]) {
// 				ret = hash_val
// 			}
// 			// return hash_val, true
// 		}
// 		prev = e
// 	}

// 	return ret, find
// }

var cashed map[[20]byte][]string

// パターンを文字列に変換する
func toInt16(str string) []int16 {
	ret := []int16{}
	s := strings.Split(str, ";")

	// fmt.Println("toByte------")
	// fmt.Println(str)
	const offset = 100
	for _, e := range s {
		if 'A' <= e[0] && e[0] <= 'Z' {
			if e[0] == 'N' {
				v, _ := strconv.Atoi(e[1:])
				ret = append(ret, int16(v))
			} else if e[0] == '.' {
				ret = append(ret, -1)
			} else {
				ret = append(ret, int16(e[0])-'A')
			}
		} else {
			if e[0] == 'N' {
				v, _ := strconv.Atoi(e[1:])
				ret = append(ret, int16(v)+offset)
			} else if e[0] == '.' {
				ret = append(ret, -1)
			} else {
				ret = append(ret, int16(e[0])-'a'+offset)
			}

		}
	}
	return ret
}

func appendPattern(ptype string, moves map[string][]int16) map[string][]int16 {
	fmt.Println("appendPattern", ptype)
	// if strings.Contains(ptype, "wreath") == false {
	// 	return moves
	// }
	n := 0
	ok := false
	target := map[string]bool{"r": true, "l": true}

	// if strings.Contains(ptype, "cube_5/5/5") {
	// 	m := []string{"r", "d", "f"}
	// 	p := [][2]int64{{0, 1}, {3, 4}}
	// 	for _, e := range m {
	// 		for _, v := range p {
	// 			x0 := e + strconv.FormatInt(v[0], 10)
	// 			x1 := e + strconv.FormatInt(v[1], 10)
	// 			state := make([]int16, len(moves[x0]))
	// 			copy(state, moves[x0])
	// 			newState := make([]int16, 0)
	// 			for _, e := range moves[x1] {
	// 				newState = append(newState, state[e])
	// 			}
	// 			y := "y" + x0 + x1
	// 			moves[y] = newState
	// 		}
	// 	}
	// 	{ // Triple
	// 		p := [][3]int64{{1, 2, 3}}
	// 		for _, e := range m {
	// 			for _, v := range p {
	// 				x0 := e + strconv.FormatInt(v[0], 10)
	// 				x1 := e + strconv.FormatInt(v[1], 10)
	// 				x2 := e + strconv.FormatInt(v[2], 10)
	// 				state := make([]int16, len(moves[x0]))
	// 				copy(state, moves[x0])
	// 				newState := make([]int16, 0)
	// 				for _, e := range moves[x1] {
	// 					newState = append(newState, state[e])
	// 				}
	// 				state = newState
	// 				newState = make([]int16, 0)
	// 				for _, e := range moves[x2] {
	// 					newState = append(newState, state[e])
	// 				}
	// 				z := "z" + x0 + x1 + x2
	// 				moves[z] = newState
	// 			}
	// 		}
	// 	}
	// }

	if strings.Contains(ptype, "cube") {
		n = 2
		target = map[string]bool{}
		for e := range moves {
			target[e] = true
		}
		ok = true
	}

	switch ptype {
	case "wreath_100/100":
		n = (100 + 1) / 2
		target = map[string]bool{"r": true, "l": true}
	case "wreath_33/33":
		n = (33 + 1) / 2
		target = map[string]bool{"r": true, "l": true}
	case "globe_3/4":
		n = 4
		target = map[string]bool{"r0": true, "r1": true, "r2": true}
	case "globe_6/10":
		n = 10
		target = map[string]bool{"r0": true, "r1": true, "r2": true, "r3": true, "r4": true, "r5": true, "r6": true}
	case "globe_3/33":
		n = 33
		target = map[string]bool{"r0": true, "r1": true, "r2": true, "r3": true}
	default:
		if !ok {
			return moves
		}
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

func shrink_path(path []string) []string {
	newpath := []string{}
	for _, e := range path {
		if len(newpath) == 0 {
			newpath = append(newpath, e)
		} else {
			prev := newpath[len(newpath)-1]
			psign := true
			pchr := ""
			if prev[0] == '-' {
				psign = false
				pchr = prev[1:]
			} else {
				psign = true
				pchr = prev
			}
			csign := true
			cchr := e
			if e[0] == '-' {
				csign = false
				cchr = e[1:]
			} else {
				csign = true
				cchr = e
			}
			if psign != csign && pchr == cchr {
				newpath = newpath[:len(newpath)-1]
			} else {
				newpath = append(newpath, e)
			}
		}
	}

	return newpath
}

func make_movelist() {
	movelist = make([]string, 0)
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

	fmt.Println("MOVELIST", movelist)
}

const inf = 10000

var dmap [][]int16

func calcDistanceIndex(cur, index []int16) int {
	dist := 0
	// fmt.Println(cur)
	// fmt.Println(index)
	for i, e := range index {
		if cur[i] == -1 {
			continue
		}
		dist = max(dist, int(dmap[e][i]))
	}

	return dist
}

func calcDistance(s0, s1 []int16) int {
	dist := 0
	m := make(map[int16][]int)
	for i, e := range s0 {
		m[e] = append(m[e], i)
	}

	for i, e := range s1 {
		if e == -1 {
			continue
		}
		d := inf
		for _, v := range m[e] {
			d = min(d, int(dmap[i][v]))
		}
		dist = max(dist, d)
	}

	return dist
}

func makeDistanceMap(n int, moves map[string][]int16) [][]int16 {
	node := make([][]int16, n)
	dist := make([][]int16, n)

	for _, move := range moves {
		// if len(strings.Split(m, "_")) != 1 {
		// 	continue
		// }
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
	return dist
}

// ＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝
// bsfを使ってキャッシュする
const limit_size = 5000000

// ＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝

func main() {
	// xxx := strings.Split("d2_2 -r4 f4 f0_2 r0_2 -r4 -d0 r4 -d0 -f4 r0 f4 f0_2 d0_2 -f0 d0_2 f0_2 d0 -f4 -d4 -r0 d4 -r0 f4 r0 -d2 d0 -f4 -d0 -f4 d2 r0_2 -f0 -d4 f0 r0_2 f4_2 f0 d2_2 f0_2 d2 f0 d2 r1 f1 f2 -d0 -f2 d0 -r4 -d3 r4 f3 f0_2 r1 f0_2 r3 f4_2 -r2 f4 r2 f4 -f0 -r1 f0 -f3 -d4 -r1 d4 d2 -r4 -d2 r4 d3_2 -r0 -f1 r0 -f1_2 -d4 r3_2 d4 f1_2 -f4 d0 r2 -d0 -r2 f4 -f2 -d2 -r0 d2 r0 f2 f0 r3 f0_2 -r3 f0 -d0 -f0 -r2 f0 d0 -f0 r2 f0 -d3 -f0 r1 f0_2 -r1 -f0 -f0 -r4 -f4 -r1 f4 r4 f0 -r0 -f2 r0_2 f2 -r0 -d0 -f4 -d3 f4_2 -d1 -f4 d0 -r3 -f1 -d3 r3 f1 -f1 r2_2 -f1 r2_2 f1_2 r1 d1 -r1 f2_2 -r1 f2_2 r1 -d0 -f2 d3_2 f2 d0 r3 -d3 -r3 -r2 f0_2 d3_2 f0_2 r2 -f1 r0_2 d3_2 r0_2 f1 -f1 -d3 r0_2 d3 r0_2 f1 -d0 -f2 -d1 f0_2 d1 f0_2 f2 d0 -d0 -r3 d1 r4_2 -d1 r4_2 r3 d0 -f2 -d1 f0_2 d1 f0_2 f2 -f2 d3 f4_2 -d3 f4_2 f2 -f3 -d3 r0_2 d3 r0_2 f3 -d2 -f3 -d2 f0_2 d2 f0_2 f3 d2 -d0 -r1 d1 r4_2 -d1 r4_2 r1 d0 d1 r2_2 d1 r2_2 -f3 r1 f3_2 -r1 -f3 -f2 r3 f2_2 -r3 -f2 f1_2 -d2 f1_2 d2 -f0 -d3 r1_2 d3 r1_2 f0 -d1 f2_2 d1 f2_2 -d1 -r4 -f1_2 d1_2 f1_2 d1_2 r4 d1 -r0 -d3_2 f1_2 d3_2 f1_2 r0 -d2 f2 -r1 f2_2 r1 f2 d2 -f3_2 -d1 f4_2 d1 f4_2 f3_2 -d1 -r2 -d2_2 f3 d2_2 -f3 r2 d1 -d1 -f3 -r2 f3_2 r2 -f3 d1 -r4 -f1_2 r4 -d1 -r4 f1_2 r4 d1 -d1 -r3_2 -d1 -r4_2 d1 r3_2 d1 r4_2 -r0 -d3_2 r0 -d1 -r0 d3_2 r0 d1 r4_2 d3 r4_2 -d3 -d3 -f4 -d2 f4 d3 -f4 d2 f4 -d3 -f3_2 d3 f4 -d3 f3_2 d3 -f4 -d2 -r4 -d2_2 -f1_2 d2_2 f1_2 r4 d2 -f2 r3 f2 -r4 -f2 -r3 f2 r4 -d1 -f3_2 d1 f4 -d1 f3_2 d1 -f4 -f1 r3 f1 -r4 -f1 -r3 f1 r4 -d1 -f1 r3 f1 -r4 -f1 -r3 f1 r4 d1 -d2_2 -r0 -d1_2 -f2_2 d1_2 f2_2 r0 d2_2 -d1 -f4 -d1 -f1_2 d1 f4 -d1 f1_2 d1_2 -d1 -r4_2 -f1 r2 f1 r4_2 -f1 -r2 f1 d1 -d1 -f4_2 d1 -f0_2 -d1 f4_2 d1 f0_2 -f0 r2 f0 -r0_2 -f0 -r2 f0 r0_2 -f4 r1 -f4 -r0_2 f4 -r1 -f4 r0_2 f4_2 -d1 -r4_2 d3 -r0_2 -d3 r4_2 d3 r0_2 -d3 d1", " ")
	// pathx := convertPath("wreath", xxx)
	// // writePath("../../tmp", 337, pathx)
	// fmt.Println(pathx)
	// return

	randRand = rand.New(rand.NewSource(time.Now().UnixNano()))
	pid := flag.Int("problem_id", -1, "")
	csvFile := flag.String("path_dir", "", "")
	timeout := flag.String("timeout", "300s", "")
	maxdepth := flag.Int("depth", 20, "")
	limit := flag.Int("limit", 1000000, "")
	reverse := flag.Bool("reverse", false, "")

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

	info = appendPattern(ddf.ptype, info)

	moves = initReverseMoves(info, ddf.ptype)

	//------------------------------------------------------------
	// 距離テーブルを作成
	N := len(strings.Split(ddf.initial, ";"))
	dmap = makeDistanceMap(N, moves)
	//------------------------------------------------------------

	// {
	// 	// check moves
	// 	for m := range moves {
	// 		fmt.Print(m, " ")
	// 	}
	// 	fmt.Println()

	// 	for _, m := range []string{"r", "-r", "l", "-l"} {
	// 		for i := 2; i <= 50; i++ {
	// 			move := fmt.Sprintf("%s_%d", m, i)
	// 			state1 := applyMove(move, ddf.solution, moves)
	// 			path := convertPath("wreath", []string{move})
	// 			state0 := ddf.solution
	// 			for _, e := range path {
	// 				state0 = applyMove(e, state0, moves)
	// 			}

	// 			fmt.Println(m, move, path, state0 == state1)
	// 			fmt.Println("ST0", state0)
	// 			fmt.Println("ST1", state1)
	// 			if state0 != state1 {
	// 				return
	// 			}
	// 		}
	// 	}

	// 	return
	// }

	make_movelist()

	fmt.Println("MoveList", movelist)

	// ret := toByte("A;A;A;A;B;B;B;B;C;C;C;C;D;D;D;D;E;E;E;E;F;F;F;x")
	// fmt.Println(ret)
	// ret = toByte("N0;N1;N2;N3;N4;N5;N6;N7;N8;N9;N10;N11;N12;N13;N14;N15;N16;N17;N18;N19;N20;N21;N22;N23")
	// fmt.Println(ret)
	// ret = applyMoveByte("r", ret, moves)
	// fmt.Println(ret)
	// return

	fmt.Println(ddf, timeout)

	solpat := strings.Split(ddf.solution, ";")
	solLen := len(solpat)
	maxLength = solLen

	mask := make([]string, solLen)
	for i := 0; i < solLen; i++ {
		mask[i] = "."
	}
	newpath := []string{}

	fmt.Println(ddf.solution, len(newpath))

	solState := strings.Split(ddf.solution, ";")

	prev_mask := make([]string, len(mask))
	copy(prev_mask, mask)
	// fmt.Println(prev_mask)

	// fmt.Println("start loop")
	// fstate := ddf.initial
	// for i := 0; i < 300; i++ {
	// 	for j := 0; j < 100 && fstate[0] != 'B'; j++ {
	// 		fstate = applyMove("l", fstate, moves)
	// 		newpath = append(newpath, "l")
	// 		fmt.Println(fstate, "l")
	// 	}
	// 	for j := 0; j < 100 && fstate[0] == 'B'; j++ {
	// 		fstate = applyMove("r", fstate, moves)
	// 		newpath = append(newpath, "r")
	// 		fmt.Println(fstate, "r")
	// 	}
	// }
	// fmt.Println(len(newpath))

	const offset = 100

	c := make([]int, solLen)
	idx := make([]int, solLen)
	for i := 0; i < solLen; i++ {
		// if i < 16 {
		// 	c[i] = (i + 4) / 4 * 4
		// if i < 8 {
		// 	c[i] = (i + 8) / 8 * 8
		// } else if i < 24 {
		// 	c[i] = (i + 4) / 4 * 4
		// } else if i < 24 {
		// 	c[i] = (i + 3) / 3 * 3
		// } else if solLen*1/4 > i {
		// 	c[i] = (i + 2) / 2 * 2
		// } else {
		c[i] = i + 1
		// }
		idx[i] = solLen - 1 - i
	}

	// rand.Seed(10)

	// return
	if s := strings.Split(ddf.ptype, "/"); strings.Contains(s[0], "cube") {
		n, _ := strconv.Atoi(s[1])
		idx, c = makeCubeIndex(n)
		makeCubeStatePattern(n)
		cubeState.flg = false
	}

	fmt.Println("c = ", c)
	fmt.Println("idx = ", idx)

	// if ddf.ptype == "cube_3/3/3" {
	// 	idx = []int{
	// 		4, 49, 40, 13, 22, 31,
	// 		0, 36, 29,
	// 		2, 20, 27,
	// 		6, 9, 38,
	// 		8, 11, 18,
	// 		15, 44, 45,
	// 		17, 47, 24,
	// 		35, 42, 51,
	// 		26, 33, 53,
	// 		1, 28,
	// 		3, 37,
	// 		5, 19,
	// 		7, 10,
	// 		43, 48,
	// 		34, 52,
	// 		25, 50,
	// 		16, 46,
	// 		39, 41, 12, 14, 21, 23, 30, 32,
	// 	}
	// }
	// fmt.Println(idx)
	// return

	if ddf.ptype == "globe_3/33" {
		for i := 0; i < solLen; i += 4 {
			for j := 0; j < 4; j++ {
				idx[i+j] = i/4 + j*66
			}
		}
	}
	if ddf.ptype == "globe_6/10" {
		for i := 0; i < solLen; i += 7 {
			for j := 0; j < 7; j++ {
				idx[i+j] = i/7 + j*20
			}
		}
	}

	// newpath = strings.Split("-d0_2 -f0 r0 f0 -f0 -d0_2 f0 -d0_2 f0 -r0_2 -d0_2 -r0 -d0_2 -r0_2 -r0 -d0 -f0 r0 f0 r0 d0 -f5 r0_2 d0_2 -r5 -d5 r5 -d0_2 r0 f5 r0 d4 r4 -d5 -f3_2 d5 -f1 -r2_2 -d1 -r1 -d5 -r2_2 d5 -r4 -f3 r4 f3 d2 -f3 f3 d1 -f3 -f5 d1 f5 f2 -r3 d2 r3 -r2 -d2 r2 -f2 -d4_2 f2 -d0_2 -f1_2 -d0_2 -f1 -d2_2 f1 -d3 -f1 d3 f1 f1 d1 -f1 -d0 -r4_2 -f0 -r4_2 f0 d0 -f0_2 r2 -f0_2 -r2 -d2_2 f0 -d2 -f0 -r1_2 -f5_2 -r1_2 -f5_2 -r0 -f1 r0 f1 r0 -d3 -r0 f3 -d0_2 -f3 -d0_2 -f4 -d5_2 -f1 -d5_2 f4 -d0 -f5_2 -r4 -f5_2 r4 d0 f5 d3 -f5 r2 -d0 -r2 d0 -f4 r1 -d0 -r1 f4 d0 -d0 -f3 -r0 -f3 d3 r0 -f3_2 d0 r5 d3 -r5 -f1 -d0_2 f1 -d0_2 -f0 r4 -f0_2 -r4 -f0 -d0 -r5 f3 -r5_2 -f3 -r5 d0 -f2 r2_2 -d0 r2 d0 -r2_2 f2 -d4 f0 -d4 r1 f0 -r1 -f0_2 -r5 f1 -r5_2 -f1 -r5 -d0 d2 r0 -f3 -r0_2 f3 r0 d0 -f5 -d0 r2 d0 -r2 f5 -d4 -f5 -r1 -f5_2 r1 -f5 -d0 f0 r3 -f0_2 -r3 f0 d0 -r3 d2 -r5_2 -d2 -r5_2 r3 -d2 -r2 -d2 -f5_2 d2 -f5_2 r2 -d2 -r1 -d2 -f5_2 d2 -f5_2 r1 r0 -f3 -r0_2 f3 r0 -f3 d3 f3 -d0 -f3 -d3 f3 d0 -d2 -r2 -d3 -r0_2 d3 -r0_2 r2 -d0 -f0 r2 f0 r1 -f0 -r2 f0 -r1 d0 -f4 -d1 -f0_2 d1 -f0_2 f4 -r0 -f4 d1 -r0 -d1 f4 -r0_2 -d1 -r2 -d4 -r0_2 d4 -r0_2 r2 -d0 -f1 f5_2 d4 -f5_2 -d4 f1 d0 f0 -d4 -f0_2 -d1 f0 f0 d5 -r0 -d3_2 r0 -d5 -f0 -f0 d3 f0 -r0 -f0 -d3 f0 r0 d1 -f0 d4 -f0_2 d1 -f0 f1_2 d0_2 -r5 d1 r5 -d0_2 -f1_2 -d3 -r0 d2 -r0_2 d3 -r0 d2_2 -r0 d3 -r0_2 d2 -r0 -d0 d4 f0 -d1 -f0_2 -d4 f0 d0 r5 d4 -r5_2 d1 r5 -d2 r5 d3 -r5_2 d2 r5 -d0 -f5 -d3 -f5_2 -d2 -f5 d0 d4 r5 d1 -r5_2 d4 r5 -d1 -d3 -r0_2 -d3_2 -r0_2 -d1 r0_2 d4 d1 -r0_2 d4 -f0_2 -d1_2 -f0_2 d2 -f0_2 d3 -f0_2 -d1 -r0_2 -d4 -r0_2 d1 -f0 r2 f0 r0_2 -f0 -r2 f0 -r0_2 -d1 f0_2 -d4 r0_2 -d1 -r0_2 d1 -f0_2 -f1 -r3 -d1 r3 d1 f1 -r3_2 -d3_2 -r3_2 -d3_2 -f1_2 d4 -f1_2 -d4 -f3 -r2 -f3_2 r2 -f3 -r1_2 -d1 -r1_2 d1 -r1_2 d3 -r1_2 -d3 -f1 r4 d4 -r4 -d4 f1 -f2_2 -d2 -f2_2 d2 -f0 d3 -f4_2 -d3 -f4_2 f0 -d1_2 -r1_2 -d1_2 -r1_2 r0 d1 -r1_2 -d1 -r1_2 -r0 -f5 -d4 -f3_2 d4 -f3_2 f5 r5 -f4 r1 -f4_2 -r1 -f4 -r5 -r0 d2 -r2_2 -d2 -r2_2 r0 -r2_2 d4 -r2_2 -d4 -r0 -d3 -f4_2 d3 -f4_2 r0 -r1_2 -d2 -r1_2 d2 -r2_2 d1 -r2_2 -d1 -f0 d2 -r2_2 -d2 -r2_2 f0 -r2_2 -d3_2 -r2_2 -d3_2 f0_2 d2_2 -r4_2 -d2_2 -r4_2 -f0_2 -r5 r2 -f4 -r2_2 f4 r5 r2 -r1 d4_2 -f1 -d4_2 f1 r1 -d4 -r4 d0 r4 d4 -r4 -d0 r4 f1 -d4 d5 r1 d4 -r1 -d5 -f1 -f2 r2 f2 -r2 d2 -r2 -d2 r2 -d1 r5 -d3 -r5 d1 r5 d3 -r5 -r3 f1 r3 -f5 r3 -f1 -r3 f5 -d2 -f5 -d4 f5 d2 -f5 d4 f5 d3_2 -f2_2 d3 -f2_2 d3 -d1 f5 d2 -f5 d1 f5 -d2 -f5 -f0 -r1 -f1 r1 f0 -r1 f1 r1 -d1 r5_2 d4 f2_2 -d4 -f2_2 -r5_2 d1 f0_2 r1_2 f0_2 -d4 -f0_2 -r1_2 -f0_2 d4 -d4 f0 -d4 r2_2 d4 -r2_2 -f0 d4", " ")

	for i := 0; i < solLen; i++ {
		// if c[i] > 100 {
		// 	cubeState.flg = true
		// }
		sindex := []int16(nil)
		state := ddf.initial
		for _, e := range newpath {
			state, _ = applyMove(e, state, sindex, moves)
		}
		if validCheck(state, ddf.solution, ddf.numWild) == true {
			break
		}

		// nextPos := (i + offset) % solLen
		// nextChr := solState[nextPos]
		// nextValue := strings.ToLower(nextChr)
		// mask[nextPos] = nextValue
		// maskstr := strings.Join(mask, ";")

		// fmt.Println(mask, c)

		// マスクパターンを生成する（idxを使って開ける場所を決める）
		for j := 0; j < solLen; j++ {
			pos := idx[j]
			if c[i] > j {
				mask[pos] = solState[pos]
			} else {
				mask[pos] = "."
			}
		}

		// nextPos := solLen - 1 - i
		// nextChr := solState[nextPos]
		// mask[nextPos] = nextChr
		maskstr := strings.Join(mask, ";")

		// fmt.Println("next target value = ", nextChr)

		var initial string
		if *reverse {
			state := maskstr
			sindex = make([]int16, solLen)
			for i := 0; i < solLen; i++ {
				sindex[i] = int16(i)
			}
			// fmt.Println("SINDEX = ", sindex)
			for i := len(paths) - 1; i >= 0; i-- {
				e := paths[i]
				if e[0] == '-' {
					e = e[1:]
				} else {
					e = "-" + e
				}
				state, sindex = applyMove(e, state, sindex, moves)
			}
			// fmt.Println("STATE ======> ", state)
			for _, e := range newpath {
				state, sindex = applyMove(e, state, sindex, moves)
			}
			initial = state
			// fmt.Println("---->", sindex)

		} else {
			// マスクパターンを動かして、スタートを作成する
			curstate := make([]string, len(mask))
			copy(curstate, prev_mask)
			m := make(map[string]int)
			s := mask
			t := prev_mask
			sol := strings.Split(state, ";")
			sel := make(map[string][]int)
			for i := 0; i < solLen; i++ {
				if s[i] != t[i] {
					if s[i] == sol[i] {
						curstate[i] = sol[i]
					} else {
						m[s[i]]++
					}
				} else if t[i] == "." {
					sel[sol[i]] = append(sel[sol[i]], i)
				}
			}

			num := 100
			switch ddf.ptype {
			case "wreath_100/100":
				num = 100
			case "wreath_33/33":
				num = 33
			case "wreath_21/21":
				num = 21
			}

			for e := range sel {
				sort.Slice(sel[e], func(i, j int) bool {
					pos0 := sel[e][i]
					pos1 := sel[e][j]
					if pos0 <= num {
						pos0 = min(pos0, num+1-sel[e][i])
					}
					if pos1 <= num {
						pos1 = min(pos1, num+1-sel[e][j])
					}
					// pos0 := min(abs(0-sel[e][i]), abs(25-sel[e][i]))
					// pos1 := min(abs(0-sel[e][j]), abs(25-sel[e][j]))
					return pos0 < pos1
				})

				// rand.Shuffle(len(sel[e]), func(i, j int) {
				// 	if sel[e][i] < 100 && sel[e][j] < 100 {
				// 		sel[e][i], sel[e][j] = sel[e][j], sel[e][i]
				// 	}
				// })
			}
			if strings.Contains(ddf.ptype, "wreath") {
				sort.Slice(sel["A"], func(i, j int) bool {
					return sel["A"][i] > sel["A"][j]
				})
			}

			// s = strings.Split(ddf.solution, ";")
			// s[101] = "here"
			// fmt.Println(s)
			// return
			for e := range m {
				for i := 0; i < m[e]; i++ {
					pos := sel[e][i]
					curstate[pos] = sol[pos]
					// fmt.Println(e, m, sel[e][i])
				}
			}
			// fmt.Println(curstate)
			// for i := 0; i < solLen; i++ {
			// 	cnt := m[sol[i]]
			// 	if cnt != 0 {
			// 		curstate[i] = sol[i]
			// 		m[sol[i]]--
			// 	}
			// }
			initial = strings.Join(curstate, ";")
		}

		//--------------------
		fmt.Println("START :", state)
		fmt.Println("TARGET:", ddf.solution)
		fmt.Println("INIT  :", initial)
		fmt.Println("MASK  :", maskstr)

		initial_byte := toInt16(initial)
		target_byte := toInt16(maskstr)

		// fmt.Println(initial_byte)
		// fmt.Println(target_byte)
		fmt.Println("distance = ", calcDistance(initial_byte, target_byte))

		startTime := time.Now()
		cashed = make(map[[20]byte][]string)
		cashed[hash(target_byte)] = []string{}

		hashed_state := hash(initial_byte)

		skip_flag := false
		if *reverse == false {
			skip_flag = true
			s0 := strings.Split(state, ";")
			s1 := strings.Split(ddf.solution, ";")
			for i := 0; i < solLen; i++ {
				if mask[i] == "." {
					continue
				}
				if s0[i] != s1[i] {
					skip_flag = false
				}
			}
		}

		if _, flg := match(initial_byte); flg || skip_flag {
			fmt.Println("Already match.")
		} else {
			bsf(initial_byte, target_byte, nil, 20, []string{})
			fmt.Println("Cash Size = ", len(cashed))
		}

		// if hashval, ok := match(initial_byte, target_byte, nextPos); ok {
		// 	fmt.Println(cashed[hashval])
		// }

		ok := false

		fmt.Println(sindex)
		if skip_flag {
			fmt.Println("Already match-----------------skip")
			fmt.Println(": time = ", time.Since(startTime))
			find = []string{}
			ok = true
		} else if ret_state, flg := match(initial_byte); flg {
			path := cashed[ret_state]
			find = []string{}
			for i := len(path) - 1; i >= 0; i-- {
				e := path[i]
				if e[0] == '-' {
					e = e[1:]
				} else {
					e = "-" + e
				}
				find = append(find, e)
			}
			ok = true
			fmt.Println("Cashed")
			fmt.Println(": time = ", time.Since(startTime))
		} else {
			fmt.Println("Current = ", newpath)
			for depth := 1; depth < *maxdepth; depth++ {
				fmt.Print("Depth .... ", depth)
				used = make(map[[20]byte]bool)
				ng = make(map[[20]byte]bool)

				used[hashed_state] = true
				ok = dfs(initial_byte, target_byte, sindex, depth, []string{})
				fmt.Println(": time = ", time.Since(startTime))
				if ok {
					break
				}
			}
		}

		if ok {
			fmt.Println(ok, find, len(find))
			newpath = append(newpath, find...)
		} else {
			fmt.Println("Failed....")
			return
		}

		state = ddf.initial
		for _, e := range newpath {
			state, _ = applyMove(e, state, nil, moves)
		}
		fmt.Println(" ----->", state)

		copy(prev_mask, mask)
	}

	fmt.Println(newpath)
	newpath = convertPath("wreath", newpath)
	fmt.Println(newpath)
	newpath = shrink_path(newpath)
	fmt.Println(newpath)

	fmt.Println("[Check] check new path")
	state := ddf.initial
	fmt.Println(state)
	for _, path := range newpath {
		state, _ = applyMove(path, state, nil, moves)
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

}
