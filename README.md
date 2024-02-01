
## K-moves
k-moves.py
k-moves-all.sh

## make submission
make_sub.py

## check solutions
check-solution.py

## 全探索
brute-force.py

brute forceで検索できているやつはワイドルカードなしでは最短なので、brute forceで見つかるやつはそのまま採用
k-movesは、一旦shortest_pathの制限を小さめで処理して全部やり、可能はレベルで深さを深くして探索を繰り返すと吉

dfsアプローチはbrute forceでやっているので、これはなし

## k-movesを書き換えて、両方から探索するバージョン
bidirect-k-moves.py 
　
## BFSを構築するバージョン
bsf.py


### rubik-solve.py
3x3のルービックキューブをソルバーを使って解くための前後の処理を行うPythonスクリプト

### rubik4-solve.py
4x4のルービックキューブをソルバーを使って解くための前後処理を行うPythonスクリプト

### santa-to-rubik.py

## cube-check.py
改造したRCubeを使って33x33のルービックキューブを解くための前後処理を行うPythonスクリプト
途中で止めて別途RCubeを動かし、再度実行する必要あり。
シンボリックリンクしたファイルで、データを受け渡す暫定版

### search-shortest-path.py
不明

###　globe-lower-calc_8_25.py
globeの下半分をパターンを使って求める処理。a-star, ida-starを使って、上半分を求めて、これで後半をうめることでglobe_3/33, globe_8/25を解く

### merge_sub.py
複数のサブをマージする

### compare.py
２つのサブを比較し、2つ目に設定したサブのスコアが1つ目より高い部分を抜き出す

### view.py
指定したサブより、フォルダにある結果がどれだけ向上しているかを表示




