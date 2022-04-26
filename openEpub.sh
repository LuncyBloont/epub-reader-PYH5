file=$(realpath "$1")
echo $file
cd $(dirname $0)
echo $(dirname $0)

python epub.py $file
read a