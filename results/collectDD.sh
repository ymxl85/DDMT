export CLASSPATH=$CLASSPATH:/home/tzl/0DDMT/SIR/MT-and-DD/src
subject=$1  #pt 7 pt2 10 replace 32 shedule 9  schedule2 10
n=$2




    trg="${subject}-dd.txt"
    
    if [ -e "$trg" ]; then
        rm "$trg"
    fi
    
    a=0
    
    i=1
    while [ $i -le $n ]; do
        echo "version$i" >> "$trg"
        
        ddir="../rawResults/DD/$subject/v$i"
        
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


echo "Done!" >&2
