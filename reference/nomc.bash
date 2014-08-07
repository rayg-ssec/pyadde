#!/bin/bash


# word 1   = 1
# word 2   = server ip address
# word 3   = port (must put a 1 here)
# word 4   = transaction type   AGET or ADIR
# word 5   = server ip address
# word 6   = port
# word 7   = 0 or client ip address
# word 8   = USER ID
# word 9   = project number 
# word 10-12  = 0 or password
# word 13  = transaction type   AGET or ADIR
# word 14  = either 0 or 122
# word 15  = start of keywords or 122
# .
# .
# .
# word 45  = start of keywords if 14 and 15 were 122

# 96 byte trailer has status returned


create_stream()
{
# word 1   = 1
int=1
printf "0: %.8x" $int | xxd -r -g0 

# word 2   = server ip address
int=1921688101
printf "0: %.8x" $int | xxd -r -g0 

# word 3   = 1
int=1
printf "0: %.8x" $int | xxd -r -g0 

# word 4   = transaction type   AGET or ADIR
type=AGET
printf %s $type

# word 5   = client ip address
int=1921688101
printf "0: %.8x" $int | xxd -r -g0 

# word 6   = port
int=112
printf "0: %.8x" $int | xxd -r -g0 

# word 7   = 0
int=0
printf "0: %.8x" $int | xxd -r -g0

# word 8   = USER ID
ID=$USER_ID
printf %s $ID

# word 9   = project number 
int=$PROJ
printf "0: %.8x" $int | xxd -r -g0

# word 10-12  = 0 or password
int=0
printf "0: %.8x" $int | xxd -r -g0
printf "0: %.8x" $int | xxd -r -g0
printf "0: %.8x" $int | xxd -r -g0
#printf %s PASS
#printf %s WORD
#printf %s HERE

# word 13  = transaction type   AGET or ADIR
type=AGET
printf %s $type

# word 14  = either 0 or 122
int=122
printf "0: %.8x" $int | xxd -r -g0

# word 15  = start of keywords or 122
int=122
printf "0: %.8x" $int | xxd -r -g0


# Word 16-44 all 0
i=16
while [[ $i -le 44 ]]; do
   int=0
   printf "0: %.8x" $int | xxd -r -g0
   i=$((i+1))
done

keywords="$group $descriptor $pos $location_type $lat $lon X $line $ele \
STYPE=VISR \
BAND=$band \
LMAG=$LMAG EMAG=$EMAG \
TRACE=0 \
TIME=$start_time $end_time I \
SPAC=1 \
UNIT=BRIT \
AUX=YES \
NAV= \
DAY=$day \
DOC=NO \
VERSION=1"

IFS='%'
printf '%s\n' $keywords
}


#################
#
#  START MAIN
#
#################

USER_ID=ROBO
PROJ=6999

if [[ -z $1 ]]; then
   echo Usage
   echo "server_name dataset dest_area <keywords>"
   echo keywords
   echo LAT=
   echo LON=
   echo MAG=
   echo DAY=
   echo TIME=
   echo lsize=
   echo esize=
   echo LTYPE=EC
   exit 1
fi 
server=${1}
dataset=${2}
dest_area=${3}
group=$(echo $dataset|awk -F"/" '{print $1 }')
descriptorandpos=$(echo $dataset|awk -F"/" '{print $2 }')

descriptor=${descriptorandpos%.*}
pos=$(echo $descriptorandpos|awk -F"." '{print $2}')

shift;shift;shift
echo $@
while [[ -n $1 ]]; do
eval $1
shift
done


band=$(printf "%2.2s" ${BAND})
day=$DAY
start_time=${time:-X}
start_time=${TIME:-$start_time}
end_time=${etime:-$start_time}
line=${lsize:-99999}
ele=${esize:-99999}
lat=${lat:-X}
lat=${LAT:-$lat}
lon=${lon:-X}
lon=${LON:-$lon}
LMAG=${mag}
LMAG=${MAG:-$LMAG}
EMAG=${EMAG:-$LMAG}
EMAG=${emag:-$LMAG}
location_type=${LTYPE:-X}
location_type=${ltype:-$location_type}



echo keywords="$group $descriptor $pos $location_type $lat $lon X $line $ele STYPE=VISR BAND=$band EMAG=$EMAG LMAG=$LMAG TRACE=0 TIME=$start_time $end_time I SPAC=1 UNIT=BRIT AUX=YES NAV= DAY=$day DOC=NO VERSION=1"
>$dest_area
#create_stream >stream.out
create_stream |nc $server 112 |dd of=$dest_area skip=4 bs=1


