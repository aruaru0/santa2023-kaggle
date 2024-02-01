if [ $# -eq 0 ]; then
    echo "No argument was specified."
    exit 1
fi

# cube 2x2
# seq  0 29 | xargs -I {} python3  bidirect-k-moves.py --problem_id {} --csv_file $1 --limit 100000
# # cube3x3
#seq  30 149 | xargs -I {} python3 bidirect-k-moves.py --problem_id {} --csv_file $1 --limit 1000000
# # cube4x4
# seq 150 209 | xargs -I {} python3 bidirect-k-moves.py --problem_id {} --csv_file $1 --limit 100000
# wreath
# seq 284 329 | xargs -I {} python3 bidirect-k-moves.py --problem_id {} --csv_file $1 --limit 100000
# seq 330 337 | xargs -I {} python3 bidirect-k-moves.py --problem_id {} --csv_file $1 --limit 100000
# # globe
# seq 338 397 | xargs -I {} python3  bidirect-k-moves.py --problem_id {} --csv_file $1 --limit 200000
# # cubes 
# seq 210 283 | xargs -I {} python3  bidirect-k-moves.py --problem_id {} --csv_file $1 --limit 200000



# repeat 3; seq 330 337 | xargs -I {} python3 bidirect-k-moves.py --problem_id {} --csv_file submission_840450.csv --limit=100000 or 1000000

#--------- bsf.py
#seq 330 337 | xargs -I {} python3 bsf.py --problem_id {} --limit=3000000 --csv_file $1
seq 30 149 | xargs -I {} python3 bsf.py --problem_id {} --limit=3000000 --csv_file $1
seq 150 209 | xargs -I {} python3 bsf.py --problem_id {} --limit=3000000 --csv_file $1
seq 210 280 | xargs -I {} python3 bsf.py --problem_id {} --limit=3000000 --csv_file $2
seq 210 276 | xargs -I {} python3 bsf.py --problem_id {} --limit=3000000 --csv_file $2
seq 277 280 | xargs -I {} python3 bsf.py --problem_id {} --limit=3000000 --csv_file $2
seq 281 283 | xargs -I {} python3 bsf.py --problem_id {} --limit=100000 --csv_file $2

seq 330 337 | xargs -I {} python3 bsf.py --problem_id {} --limit=3000000 --csv_file $2
seq 338 397 | xargs -I {} python3 bsf.py --problem_id {} --limit=100000 --csv_file $2


python3 bsf-random.py --problem_id 368 --limit 300000 --csv_file submission_820219.csv --step 50 --prob 0.5
python3 bsf-random.py --problem_id 281 --limit 200000 --csv_file submission_820219.csv --step 10000  --prob 0.5 
python3 bsf-random.py --problem_id 282 --limit 200000 --csv_file submission_820219.csv --step 10000  --prob 0.5 
python3 bsf-random.py --problem_id 283 --limit 200000 --csv_file submission_820219.csv --step 10000  --prob 0.5 
seq 30 149 | xargs -I {} python3 bsf-random.py --problem_id {} --limit 1000000 --csv_file submission_820219.csv --step 20  --prob 0.5
seq 150 209 | xargs -I {} python3 bsf-random.py --problem_id {} --limit 1000000 --csv_file submission_820219.csv --step 100  --prob 0.5
seq 200 209 | xargs -I {} python3 bsf-random.py --problem_id {} --limit 1000000 --csv_file submission_820219.csv --step 100  --prob 0.5

seq 329 337 | xargs -I {} python3 bsf-random.py --problem_id {} --limit 3000000 --csv_file submission_820219.csv --step 100  --prob 1.0
seq 368 372 |  xargs -I {} python3 bsf-random.py --problem_id {} --limit 3000000 --csv_file submission_820219.csv --step 100  --prob 1
seq 331 337 | xargs -I {} python3 bsf-random.py --problem_id {}  --limit 5000000 --csv_file submission_820219.csv --step -1 --prob 1
repeat 5; python3 bsf-random.py --problem_id 334  --limit 5000000 --csv_file submission_820219.csv --step -1 --prob 0.5
repeat 5; python3 bsf-random.py --problem_id 335  --limit 5000000 --csv_file submission_820219.csv --step -1 --prob 0.5
repeat 5; python3 bsf-random.py --problem_id 336  --limit 5000000 --csv_file submission_820219.csv --step -1 --prob 0.5
repeat 5; python3 bsf-random.py --problem_id 337  --limit 5000000 --csv_file submission_820219.csv --step -1 --prob 0.5
seq 353 367 | xargs -I {} python3 bsf-random.py --problem_id {}  --limit 5000000 --csv_file submission_820219.csv --step -1 --prob 1


repeat 100; python3 bsf-random.py --problem_id 336 --limit 5000000 --csv_file submission_823159.csv --step 1000 --prob -1

repeat 100; python3 bsf-random.py --problem_id 333  --limit 5000000 --csv_file submission_820104.csv --step -1000 --prob -1

repeat 100; python3 bsf-random.py --problem_id 334  --limit 5000000 --csv_file submission_820104.csv --step -1000 --prob -1

repeat 100; seq 334 337 | xargs -I {} python3 bsf-random.py --problem_id {}  --limit 6000000 --csv_file submission_816433.csv --step -1000 --prob -1
repeat 100; seq  367 338| xargs -I {} python3 bsf-random.py --problem_id {}  --limit 5000000 --csv_file submission_816433.csv --step -1000 --prob -1
repeat 100; seq 280 200 | xargs -I {} python3 bsf-random.py --problem_id {}  --limit 6000000 --csv_file submission_816433.csv --step -1000 --prob -1

repeat 100; seq 329 337 | xargs -I {} python3 bsf-random.py --problem_id {}  --limit 11000000 --csv_file submission_816433.csv --step -1000 --prob -1

 seq 200 280 | xargs -I {} python3  bidirect-k-moves.py --problem_id {} --csv_file $1 --limit 200000

repeat 100; seq 334 337 | xargs -I {}  ./main  --problem_id {} --path_dir ../sol_2dir_k --limit 5000000 --step -100 --prob -1
repeat 100; seq 338 347 | xargs -I {}  ./main  --problem_id {} --path_dir ../sol_2dir_k --limit 5000000 --step -100 --prob -1

repeat 100; seq 244 200 | xargs -I {}  time ./main2  --problem_id {} --path_dir ../sol_2dir_k --limit 2000000 --step -1 --prob 1 --separate_tbl "1,2,3,4"
repeat 100; seq 30 149 | xargs -I {}  time ./main2  --problem_id {} --path_dir ../sol_2dir_k --limit 1000000 --step -100 --prob -1 --separate_tbl "1,2,3,4"
repeat 100; seq 368 382 | xargs -I {}  time ./main2  --problem_id {} --path_dir ../sol_2dir_k --limit 1000000 --step -1 --prob 1 --separate_tbl "1,2,3,4"

# 2024.1.3 - 
repeat 100; seq 338 367 | xargs -I {}  time ./main2 --problem_id {} --path_dir ../sol_2dir_k --limit 5000000 --step -100 --prob -1 --separate_tbl "1,2,3,4"

repeat 100; seq 368 387 | xargs -I {}  time ./main2 --problem_id {} --path_dir ../sol_2dir_k --limit 5000000 --step -100 --prob -1 --separate_tbl "1,1,2,3,5"

repeat 100; seq 388 397 | xargs -I {}  time ./main2 --problem_id {} --path_dir ../sol_2dir_k --limit 5000000 --step -100 --prob -1 --separate_tbl "1,2,3,5,7"

repeat 100; seq 235 244 | xargs -I {}  time ./main2 --problem_id {} --path_dir ../sol_2dir_k --limit 5000000 --step -1 --prob 1 --separate_tbl "1,1,2,3,5"

repeat 100; seq 368 372 | xargs -I {}  time ./main2 --problem_id {} --path_dir ../sol_2dir_k --limit 15000000 --step -1 --prob -1

repeat 100; seq 373 387 | xargs -I {}  time ./main2 --problem_id {} --path_dir ../sol_2dir_k --limit 10000000 --step -1 --prob 1

repeat 100; seq 397 397 | xargs -I {}  time ./main2 --problem_id {} --path_dir ../sol_2dir_k --limit 5000000 --step -100 --prob -1 --separate_tbl "1,10"

seq 0 397 | xargs -I {}  time ./main2 --problem_id {} --path_dir ../sol_2dir_k --limit 1000000 --step -1 --prob 1


seq 388 397 | xargs -I {}  time ./main2 --problem_id {} --path_dir ../sol_2dir_k --limit 100000 --step -100 --prob -1 --separate_tbl "100"


time ./main2 --problem_id 283 --path_dir ../sol_2dir_k --limit 100000 --step -100 --prob -1 --separate_tbl "100"

repeat 10; seq 209 200 | xargs -I {}  time ./main2 --problem_id {} --path_dir ../sol_2dir_k --limit 3000000 --step -100 --prob -1 --separate_tbl "1,2,4"
seq 338 347 | xargs -I {} time python3  bidirect-k-moves.py --problem_id {} --csv_file submission_810774.csv --limit 1000000000

seq 330 337 | xargs -P 8 -I {} go run a-star.go --problem_id {} --path_dir ../../sol_2dir_k --limit 20000000

seq 30 150 | xargs -I {} go run a-star.go --problem_id {} --path_dir ../../sol_2dir_k --limit 10000000 --step 15 --timeout "300s"

#id:235 1229 -> 193
#id:236 1884 -> 196
#id:237 1130 -> 184
#id:238 1198 -> 176
#id:239 1605 -> 181
#id:282 139497 -> 84611
repeat 10; seq 235 239 | xargs -I {}  time ./main2 --problem_id {} --path_dir ../sol_2dir_k --limit 3000000 --step -100 --prob -1 --separate_tbl "1,2,4"
repeat 10; seq 235 239 |  xargs -I {} go run a-star.go --problem_id {} --path_dir ../../sol_2dir_k --limit 10000000 --step 8 --timeout "300s"

# repeat 10; seq 282 282 | xargs -I {}  time ./main2 --problem_id {} --path_dir ../sol_2dir_k --limit 1000000 --step -100 --prob 1 --separate_tbl "100"
# repeat 10; seq 282 282 |  xargs -I {} go run a-star.go --problem_id {} --path_dir ../../sol_2dir_k --limit 10000000 --step 6 --timeout "300s"
# repeat 10; seq 282 282 | xargs -I {} python3 bidirect-k-moves.py --problem_id {} --csv_file submission_840450.csv --limit=100000 or 1000000
repeat 10; seq 281 281 | xargs -I {}  time ./main2  --path_dir ../sol_2dir_k --limit 100000 --step -100 --prob 1 --separate_tbl "100"  --problem_id {}
repeat 10; seq 283 283 | xargs -I {}  time ./main3 --problem_id {} --path_dir ../sol_2dir_k --limit 100000 --step -100 --prob 1 --separate_tbl "100" 
repeat 10; seq 281 283 | xargs -I {}  time ./main3 --problem_id {} --path_dir ../sol_2dir_k --limit 100000 --step -100 --prob 1 --separate_tbl "200" 


repeat 10; seq 389 389 | xargs -I {}  time ./main3 --problem_id {} --path_dir ../sol_2dir_k --limit 1000000 --step -100 --prob 1 --separate_tbl "200" 

seq 330 337 | xargs -I {} ./a-star --problem_id {} --path_dir ../../sol_2dir_k --limit 20000000 --step 17


seq 353 347 | xargs -I {}  time ./main3 --problem_id {} --path_dir ../sol_2dir_k --limit 1000000 --step -100 --prob 1 --separate_tbl "20" 

./a-star --problem_id 338 --path_dir ../../sol_2dir_k --limit 20000000 --step 2

# id:132 31 -> 29
# id:218 169 -> 167
# id:248 347 -> 345
# id:255 3279 -> 3263
# id:257 587 -> 585
# id:261 537 -> 533
# id:262 952 -> 948
# id:263 953 -> 945
# id:264 968 -> 962
# id:266 957 -> 949
# id:267 1329 -> 1327
# id:268 1345 -> 1341
# id:269 1324 -> 1320
# id:270 1305 -> 1297
# id:271 1327 -> 1323
# id:272 1948 -> 1946
# id:274 2018 -> 2002
# id:275 2005 -> 2001
# id:276 2099 -> 2087
# id:277 14399 -> 14339
# id:278 14947 -> 14913
# id:279 14973 -> 14905
# id:280 14584 -> 14558
# id:281 80613 -> 80405

seq 329 333 | xargs -I {} ./a-star --problem_id {} --path_dir ../../sol_2dir_k --limit 20000000 --step 18 --timeout "5s"
seq 388 397 | xargs -I {}  time ./main2 --problem_id {} --path_dir ../sol_2dir_k --limit 1000000 --step -100 --prob -1 --separate_tbl "200"

# globe_3/4
repeat 100; seq 368 372 |  xargs -I {} time ./main2 --problem_id {} --path_dir ../sol_2dir_k --limit 10000000 --step -100 --prob -1 --separate_tbl "10,25,49,77,100"

# globe_6/4
repeat 100; seq 282 377 |  xargs -I {} time ./main3 --problem_id {} --path_dir ../sol_2dir_k --limit 3000000 --step -100  --prob 0.1  --separate_tbl "1"

# ALL check　
seq 200 276 |  xargs -I {} python3 path-merger.py --problem_id {} --limit 3000000  *.csv data/submission_e*.csv sub_RESULT/sub*.csv
#267 error.....
seq 0 397 |  xargs -I {} python3 path-merger.py --problem_id {} --limit 500000  *.csv data/submission_e*.csv sub_RESULT/sub*.csv


seq 361 361 | xargs -I {} go run a-star.go --problem_id {}  --path_dir ../../sol_2dir_k --limit 10000000
seq 338 342 | xargs -I {} ./main2 --problem_id {} --path_dir ../sol_2dir_k --limit 3000000 --step -1 --prob 1 

repeat 10 ; seq 348 382 | xargs -I {} ./main2 --path_dir ../sol_colab --limit 5000000 --step -1 --prob 1 --problem_id {}
repeat 10 ; seq 338 382 | xargs -I {} ./main2 --path_dir ../sol_2dir_k --limit 5000000 --step -1 --prob 1 --problem_id {}
repeat 10 ; seq 383 387 | xargs -I {} ./main2 --path_dir ../sol_2dir_k --limit 5000000 --step -1 --prob 1 --problem_id {}
repeat 10 ; seq 336 336 | xargs -I {} ./main2 --path_dir ../sol_2dir_k --limit 5000000 --step -1 --prob 1 --problem_id {}


repeat 10 ; seq 330 330 | xargs -I {} ./main2 --path_dir ../tmp --limit 5000000 --step -1 --prob 1 --problem_id {}
repeat 10 ; seq 337 337 | xargs -I {} ./main2 --path_dir ../tmp --limit 5000000 --step -1 --prob 1 --problem_id {}


go run a-star.go --path_dir ../../sol_2dir_k --limit 10000000 --problem_id 388

repeat 10; seq 383 387 | xargs -I {} go run a-star.go --path_dir ../../sol_2dir_k --limit 10000000 --problem_id {}
seq 384 384  | xargs -I {} ./main2 --path_dir ../tmp --limit 5000000 --step -1 --prob 1 --problem_id {}
repeat 10; seq 388 397 | xargs -I {} ./main2  --path_dir ../sol_2dir_k --limit 500000 --step -100 --prob -1 --separate_tbl "200,500"   --problem_id {}
repeat 10; seq 388 397 | xargs -I {} ./main2  --path_dir ../sol_2dir_k --limit 1000000 --step -100 --prob -1 --separate_tbl "100"   --problem_id {}

seq 389 390 |xargs -I {} go run a-star.go --path_dir ../../sol_sample --problem_id {} --limit 10000000 --timeout "1800s"
seq 396 397 |xargs -I {} go run a-star.go --path_dir ../../sol_sample --problem_id {} --limit 10000000 --timeout "1800s"


go run a-star.go --path_dir ../../sol_sample --problem_id 345 --limit 20000000 --timeout "1800s"
repeat 3; seq 388 397 | xargs -I {} ./main2  --path_dir ../sol_2dir_k --limit 1000000 --step -10 --prob -1 --problem_id {}

repeat 3; seq 388 390 | xargs -I {} ./main2  --path_dir ../sol_2dir_k --limit 1000000 --step -1 --prob 1 --problem_id {}
repeat 3; seq 392 394 | xargs -I {} ./main2  --path_dir ../sol_2dir_k --limit 1000000 --step -1 --prob 1 --problem_id {}
repeat 3; seq 396 397 | xargs -I {} ./main2  --path_dir ../sol_2dir_k --limit 1000000 --step -1 --prob 1 --problem_id {}
repeat 3; seq 388 390 | xargs -I {} ./main2  --path_dir ../sol_2dir_k --limit 1000000 --step -10 --prob -1 --problem_id {}
repeat 3; seq 392 394 | xargs -I {} ./main2  --path_dir ../sol_2dir_k --limit 1000000 --step -10 --prob -1 --problem_id {}
repeat 3; seq 396 397 | xargs -I {} ./main2  --path_dir ../sol_2dir_k --limit 1000000 --step -10 --prob -1 --problem_id {}
repeat 3; seq 388 390 | xargs -I {} ./main2  --path_dir ../sol_2dir_k --limit 1000000 --step -1 --prob 1 --problem_id {}
repeat 3; seq 392 394 | xargs -I {} ./main2  --path_dir ../sol_2dir_k --limit 1000000 --step -1 --prob 1 --problem_id {}
repeat 3; seq 396 397 | xargs -I {} ./main2  --path_dir ../sol_2dir_k --limit 1000000 --step -1 --prob 1 --problem_id {}

# id: 388 : globe_3/33 : 26178 -> 8430 (17748)
# id: 389 : globe_3/33 : 32342 -> 8409 (23933)
# id: 390 : globe_3/33 : 24047 -> 7745 (16302)
# id: 391 : globe_3/33 : 28175 -> 28087 (88)
# id: 392 : globe_33/3 : 22043 -> 8532 (13511)
# id: 393 : globe_33/3 : 29070 -> 8968 (20102)
# id: 394 : globe_33/3 : 28451 -> 8111 (20340)
# id: 395 : globe_33/3 : 28712 -> 28702 (10)
# id: 396 : globe_8/25 : 25828 -> 10145 (15683)
# id: 397 : globe_8/25 : 20473 -> 9782 (10691)
seq 388 397 | xargs -I {} ./main2  --path_dir ../sol_2dir_k --limit 3000000 --step 100 --prob -1 --problem_id {}
./main2  --path_dir ../sol_2dir_k --limit 3000000 --step 100 --prob -1 --problem_id 283

go run ida-star.go --path_dir ../../sol_sample --reverse --problem_id 393
go run ida-star.go --path_dir ../../sol_sample --reverse --problem_id 394


seq 388 397| xargs -P 4 -I {} ./main2  --path_dir ../sols --limit 100000 --step 50 --prob -1 --problem_id {}
seq 388 397| xargs -P 2 -I {} ./main2  --path_dir ../sols --limit 1000000 --step 100 --prob -1 --problem_id {}
seq 388 397| xargs -P 2 -I {} ./main2  --path_dir ../sols --limit 1000000 --step 50 --prob -1 --problem_id {}
seq 396 397| xargs -P 2 -I {} ./main2  --path_dir ../sol_2dir_k --limit 1000000 --step 50 --prob -1 --problem_id {}

./main2  --path_dir ../sols --limit 1000000 --step 50 --prob 1 --problem_id 394
./main2  --path_dir ../sols --limit 1000000 --step 50 --prob 1 --problem_id 394
./main2  --path_dir ../sols --limit 1000000 --step 50 --prob 1 --problem_id 391
./main2  --path_dir ../sols --limit 1000000 --step 50 --prob 1 --problem_id 391
./main2  --path_dir ../sols --limit 1000000 --step 50 --prob 1 --problem_id 388
./main2  --path_dir ../sols --limit 1000000 --step 50 --prob 1 --problem_id 395

# sol0 でチェックしている394 391 388のサイズを確認する（午前中）

seq 210 283 | xargs -I {} ./main2  --path_dir ../sol_2dir_k --limit 100000 --step -1 --prob -1 --problem_id {}

repeat 100; seq 388 397| xargs -P 4 -I {} ./main2  --path_dir ../sol_2dir_k --limit 100000 --step 50 --prob -1 --problem_id {}