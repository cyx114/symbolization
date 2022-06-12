# 将文件命名为与上传文件一致
mv crashlog $crashlog

# 清空结果文件夹
{ rm -r result } || { echo "Result folder does not exist" }

python "./script/symbolization.py"

# 执行完成后，删除多余临时文件
for file in ./*
do
if [ -d "$file" ] && [ "$file" != "./result" ] && [ "$file" != "./script" ]
then
rm -r "$file"
elif [ -f "$file" ]
then
rm "$file"
fi
done
{ rm .DS_Store } || { echo ".DS_Store does not exist" }