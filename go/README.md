

infoフォルダが必要（csvファイルをGoで読みやすいように加工したデータ）

既に作成したパスを圧縮するためのツール
./main.go
other/main2.go ハッシュなどを使い省メモリ化
other2/main3.go　さらに省メモリ化したが、バグあり？

A-star（initial - solutionの両方から探索を行う）
a-star/a-star.go
a-star-globe_1_8/a-star.go ： globe-1-8専用
a-star-globe_1_16 : 最新（a-starで溶けるものは、ほぼ、これで解ける）
a-star-globe_xx/ 実験用のコード

IDA* ：　bsfによる探索と、IDA*(IDDFS)を組み合わせたもの
ida-star-ring/ wearthを解くためにカスタム
ida-star2/  cube_6x6x6までと、whearthを解けたバージョン（何度か実行する必要あり）解けないこともある
ida_star-globe, ida_star-globe-xx/ globe用のルールなどを追加したバージョン

※--reverseオプションをつけないとRubik CubeとGlobeは解けないので注意
