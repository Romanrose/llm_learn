T=c-pliang@ad12a3ca-hn01.cloud.together.ai

rsync -arvz lecture_08*.py $T:spring2025-lectures || exit 1
ssh $T "ssh ad12a3ca-04 'cd spring2025-lectures && . main/bin/activate && python lecture_08.py | tee var/traces/lecture_08_stdout.txt'"
ssh $T "ssh ad12a3ca-04 'cd spring2025-lectures && . main/bin/activate && python execute.py -m lecture_08.py'"
rsync -arvz $T:spring2025-lectures/var/traces var || exit 1
