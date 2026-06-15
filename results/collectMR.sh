export CLASSPATH=$CLASSPATH:/home/tzl/0DDMT/SIR/MT-and-DD/src
subject=$1  #pt 7 pt2 10 replace 32 shedule 9  schedule2 10
n=$2

mr_list="MR1 MR2 MR3"

for mr in $mr_list; do
    trg="${subject}-${mr}.txt"
    
    if [ -e "$trg" ]; then
        rm "$trg"
    fi
    
    a=0
    
    echo "Processing $mr..." >&2
    
    i=1
    while [ $i -le $n ]; do
        echo "version$i" >> "$trg"
        
        ddir="../rawResults/DDMT/$subject/v$i/$mr"
        
        if [ -d "$ddir" ]; then
            for file in "$ddir"/*; do
                if [ -f "$file" ]; then
                    fname=${file##*/}
                    data=$(java ResultAnalyzer "$file")
                    echo "tc:$fname" >> "$trg"
                    echo "data:$data" >> "$trg"
                    a=$(($a+1))
                fi
            done
        else
            echo "Warning: $ddir does not exist" >&2
        fi
        
        i=$(($i+1))
    done
    
    echo "Total tcs:$a" >> "$trg"
done

echo "Done!" >&2
