import argparse
import os
import re


def transform_postfix(dir_path, postfix='raw', dir_included=False):
    old_file_list = os.listdir(dir_path)  # 当前文件夹下所有文件名称

    num = [re.findall('\d+', i) for i in old_file_list]  # 避免字典序给投影顺序带来的困扰，对所有文件的数字补 0
    replenish = max(len(i[0]) for i in num)  # 补 0 的个数

    for old_name in old_file_list:
        has_postfix = old_name.find('.')  # 找第一个 .
        if has_postfix == -1:  # 文件没有后缀
            new_name = str(old_name).rjust(replenish, '0') + '.' + postfix
        else:  # 文件有后缀，或者多个后缀
            new_name = str(old_name[: has_postfix]).rjust(replenish, '0') + '.' + postfix

        old_dir = os.path.join(dir_path, old_name)
        new_dir = os.path.join(dir_path, new_name)

        if not os.path.isdir(old_dir) and not dir_included:  # 默认忽略文件夹
            os.rename(old_dir, new_dir)

    print('All Done!')


if __name__ == '__main__':
    # dir_path = input('Absolute transform image path:')  # 文件夹路径，父目录
    # transform_postfix(dir_path, 'raw')

    # 命令行形式传参
    parser = argparse.ArgumentParser()
    parser.add_argument(  # 文件夹路径
        '-d', '--dir', nargs='+', help='Absolute transform image path')
    parser.add_argument(  # 后缀
        '-p', '--postfix', help='File postfix, default is \'raw\', use \'null\' to set no postfix', default='raw')

    args = parser.parse_args()
    if args.postfix == 'null':  # 去除后缀
        args.postfix = ''
    transform_postfix(args.dir[0], args.postfix)
