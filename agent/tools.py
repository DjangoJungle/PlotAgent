def is_comma_separated_line(line):
    """
    检查一行是否是逗号分隔的格式（至少包含两个逗号）。

    :param line: 输入的字符串
    :return: 如果是逗号分隔的格式，返回True，否则返回False
    """
    return line.count(',') >= 2


def extract_comma_separated_tables(file_path):
    """
    从文件中提取出逗号分隔的矩阵部分，并保存为多个CSV文件（如果有多个表格）。

    :param file_path: 输入的文本文件路径
    """
    with open(file_path, 'r', encoding='utf-8') as file:
        lines = file.readlines()

    table_lines = []
    in_table = False
    table_count = 0
    column_count = 0

    for line in lines:
        # 检查是否是表格开始的行
        if is_comma_separated_line(line):
            current_column_count = line.count(',') + 1
            if not in_table:
                # 开始新的表格
                in_table = True
                column_count = current_column_count
                table_lines.append(line)
            else:
                # 在已有表格中检查列数一致性
                if current_column_count == column_count:
                    table_lines.append(line)
                else:
                    # 遇到列数不一致的行，认为表格结束
                    save_table(table_lines)
                    table_lines = [line]
                    table_count += 1
                    column_count = current_column_count
        else:
            if in_table:
                # 如果已经进入表格，遇到非表格行则认为表格结束
                save_table(table_lines)
                table_lines = []
                in_table = False
                table_count += 1

    # 保存最后的表格
    if table_lines:
        save_table(table_lines)


def save_table(table_lines):
    """
    将提取出的表格数据保存为CSV文件。

    :param table_lines: 表格数据的行列表
    """
    with open("processed_data.csv", 'w', encoding='utf-8') as file:
        for line in table_lines:
            file.write(line)