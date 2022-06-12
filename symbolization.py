# -*- coding: utf-8 -*-
import os
import shutil
import zipfile


MANUAL_MODE = 1
# "symbolicatecrash" 文件的位置
g_symbolicatecrash_path = "~/symbolization/symbolicatecrash"


# 将字符串统一为utf-8且小写
def pure_str(str):
    new_str = str.strip().lower()
    if isinstance(new_str, unicode):
        new_str = new_str.encode('utf-8')
    return new_str


# 两个字符串是否相待，不区分大小写,且会忽略前后空格
def is_equal_strs(str1, str2):
    pure_str1 = pure_str(str1)
    pure_str2 = pure_str(str2)
    res = pure_str1 == pure_str2
    return res


# 是否包含某个字符串
def contains_str(ori_str, a_str):
    ori_str_low = pure_str(ori_str)
    a_str_low = pure_str(a_str)
    if a_str_low in ori_str_low:
        return True
    else:
        return False


def NORMAL_LOG(text):
    if isinstance(text, unicode):
        text = text.encode('utf-8')
    print text


def copy_symbol_to_target_folder(target_folder):
    desktop_path = os.path.join(os.path.join(os.path.expanduser('~')), 'Desktop')
    # Note: If add '/' at begining of the 'symbolicatecrash', the join will failed and return the second parameter.0
    symbol_path = os.path.join(desktop_path, g_symbolicatecrash_path)
    dst_path = os.path.join(target_folder, "symbolicatecrash")
    shutil.copy(symbol_path, dst_path)


def delete_symbol(target_folder):
    dst_path = os.path.join(target_folder, u"symbolicatecrash")
    os.remove(dst_path)


def get_dsym_file_path(target_folder):
    dsym_file_path = u""
    for file in os.listdir(target_folder):
        if contains_str(file, u".dSYM"):
            dsym_file_path = os.path.join(target_folder, file)
    if not dsym_file_path:
        NORMAL_LOG(u"无dsym文件:{}".format(dsym_file_path))
        exit(2)
    return dsym_file_path


def add_quote_for_path(path):
    return u"\"%s\"" % path


def resolve_crash_files(target_folder, before_iOS15):
    copy_symbol_to_target_folder(target_folder)
    dsym_file_path = get_dsym_file_path(target_folder)
    cmd_export_env = ""
    symbol_script_path = ""
    if MANUAL_MODE:
        cmd_export_env = u"export DEVELOPER_DIR=/Applications/Xcode.app/Contents/Developer"
        symbol_script_path = u"/Applications/Xcode.app/Contents/SharedFrameworks/CoreSymbolicationDT.framework/Versions/A/Resources/CrashSymbolicator.py"
    else:
        # Jenkines 上有多个 XCode 版本，路径有所差异。
        cmd_export_env = u"export DEVELOPER_DIR=/Applications/Xcode-13.app/Contents/Developer"
        symbol_script_path = u"/Applications/Xcode-13.app/Contents/SharedFrameworks/CoreSymbolicationDT.framework/Versions/A/Resources/CrashSymbolicator.py"
    file_list = []
    result_dir_name = "result"
    result_dir_path = os.path.join(target_folder, result_dir_name)
    if not os.path.exists(result_dir_path) or not os.path.isdir(result_dir_path):
        os.mkdir(result_dir_path)
    for filename in os.listdir(target_folder):
        file_list.append(filename)
    has_failure = False
    for filename in file_list:
        filename_pure = os.path.splitext(filename)[0]
        extend = os.path.splitext(filename)[-1]
        file_path = add_quote_for_path(os.path.join(target_folder, filename))
        if is_equal_strs(extend, u".crash") or is_equal_strs(extend, u".ips"):
            result_file_path = os.path.join(result_dir_path, '%s_symboled.crash' % filename_pure)
            NORMAL_LOG(u"symbol {}".format(filename))
            NORMAL_LOG(u"before_iOS15 {}".format(before_iOS15))
            if before_iOS15 == "Y":
                symbol_cmd = u"cd {0};{1};./symbolicatecrash " \
                         u"{2} {3} > {4};".format(target_folder, cmd_export_env, file_path,
                                                               dsym_file_path, result_file_path)
            else:
                symbol_cmd = u"cd {0}; python3 {4} -d {1} -o {2} -p {3}".format(target_folder, dsym_file_path, result_file_path, file_path, symbol_script_path)
            print('symbol_cmd: %s' % symbol_cmd)
            if os.system(symbol_cmd) != 0:
                has_failure = True
    delete_symbol(target_folder)
    if has_failure:
        exit(2)


def decompress():
    zFile = zipfile.ZipFile('./symbol.zip', "r")
    for fileM in zFile.namelist():
        zFile.extract(fileM)
    zFile.close();


def main():
    target_folder = ""
    before_iOS15 = "N"
    if MANUAL_MODE:
        target_folder = raw_input('请输入crash所有文件夹(其中需要包含dsym文件):')
        before_iOS15 = raw_input('OS < 15.0:(Y/N):')
    else:
        before_iOS15 = os.getenv("Before_iOS15")
        target_folder = "./"
        decompress()
    target_folder = target_folder.strip()
    resolve_crash_files(target_folder, before_iOS15)


if __name__ == '__main__':
    main()


