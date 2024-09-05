"""
This code is the tool registration part. By registering the tool, the model can call the tool.
This code provides extended functionality to the model, enabling it to call and interact with a variety of utilities
through defined interfaces.
"""

import copy
import inspect
from pprint import pformat
import traceback
from types import GenericAlias
from typing import get_origin, Annotated
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# （可视化）设置中文字体
plt.rcParams['font.sans-serif'] = 'simhei'
plt.rcParams['axes.unicode_minus'] = False


_TOOL_HOOKS = {}
_TOOL_DESCRIPTIONS = {}


def register_tool(func: callable):
    tool_name = func.__name__
    tool_description = inspect.getdoc(func).strip()
    python_params = inspect.signature(func).parameters
    tool_params = []
    for name, param in python_params.items():
        annotation = param.annotation
        if annotation is inspect.Parameter.empty:
            raise TypeError(f"Parameter `{name}` missing type annotation")
        if get_origin(annotation) != Annotated:
            raise TypeError(f"Annotation type for `{name}` must be typing.Annotated")

        typ, (description, required) = annotation.__origin__, annotation.__metadata__
        typ: str = str(typ) if isinstance(typ, GenericAlias) else typ.__name__
        if not isinstance(description, str):
            raise TypeError(f"Description for `{name}` must be a string")
        if not isinstance(required, bool):
            raise TypeError(f"Required for `{name}` must be a bool")

        tool_params.append({
            "name": name,
            "description": description,
            "type": typ,
            "required": required
        })
    tool_def = {
        "name": tool_name,
        "description": tool_description,
        "params": tool_params
    }
    print("[registered tool] " + pformat(tool_def))
    _TOOL_HOOKS[tool_name] = func
    _TOOL_DESCRIPTIONS[tool_name] = tool_def

    return func


def dispatch_tool(tool_name: str, tool_params: dict) -> str:
    if tool_name not in _TOOL_HOOKS:
        return f"Tool `{tool_name}` not found. Please use a provided tool."
    tool_call = _TOOL_HOOKS[tool_name]
    try:
        ret = tool_call(**tool_params)
    except:
        ret = traceback.format_exc()
    return str(ret)


def get_tools() -> dict:
    return copy.deepcopy(_TOOL_DESCRIPTIONS)


# Tool Definitions


@register_tool
def get_weather(
        city_name: Annotated[str, 'The name of the city to be queried', True],
) -> str:
    """
    Get the current weather for `city_name`
    """

    if not isinstance(city_name, str):
        raise TypeError("City name must be a string")

    key_selection = {
        "current_condition": ["temp_C", "FeelsLikeC", "humidity", "weatherDesc", "observation_time"],
    }
    import requests
    try:
        resp = requests.get(f"https://wttr.in/{city_name}?format=j1")
        resp.raise_for_status()
        resp = resp.json()
        ret = {k: {_v: resp[k][0][_v] for _v in v} for k, v in key_selection.items()}
    except:
        import traceback
        ret = "Error encountered while fetching weather data!\n" + traceback.format_exc()

    return str(ret)


import pandas as pd
import matplotlib.pyplot as plt
import streamlit as st

# 工具函数定义

@register_tool
def extract_and_save_tables(file_name: Annotated[str, 'The name of the text file containing tables', True]) -> str:
    """
    从文本文件中提取逗号分隔的表格并保存为CSV文件，随后可视化表格内容。
    """
    def is_comma_separated_line(line):
        return line.count(',') >= 2

    def save_table(table_lines):
        output_file = "extracted_table.csv"
        with open(output_file, 'w', encoding='utf-8') as file:
            for line in table_lines:
                file.write(line)
        return output_file

    file_path = f"./{file_name}"
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            lines = file.readlines()

        table_lines = []
        in_table = False
        column_count = 0

        for line in lines:
            if is_comma_separated_line(line):
                current_column_count = line.count(',') + 1
                if not in_table:
                    in_table = True
                    column_count = current_column_count
                    table_lines.append(line)
                else:
                    if current_column_count == column_count:
                        table_lines.append(line)
                    else:
                        break
            else:
                if in_table:
                    break

        if table_lines:
            output_file = save_table(table_lines)
            df = pd.read_csv(output_file, index_col=0)
            st.table(df)  # 可视化表格
            return f"表格已提取并保存为 `{output_file}`。"
        else:
            return "文件中未找到有效表格。"

    except Exception as e:
        return f"处理文件时发生错误: {e}"


@register_tool
def append_average(file_name: Annotated[str, 'The name of the csv file containing data', True]) -> str:
    """
    向表格中添加 '平均值' 列，计算每行的平均值并可视化表格。

    参数:
    - file_name: CSV 文件的名称，包含要处理的数据。

    作用:
    - 计算每一行的数值列的平均值，并添加到 '平均值' 列。如果该列已存在，则会先删除旧的列，再添加新的 '平均值' 列。
    """
    file_path = f"./{file_name}"
    df = pd.read_csv(file_path, index_col=0)

    if '平均值' in df.columns:
        df.drop('平均值', axis=1, inplace=True)

    df['平均值'] = df.mean(axis=1)
    df.to_csv(file_path, header=True)

    st.table(df)  # 可视化表格
    return "平均值列已成功添加并保存。"


@register_tool
def append_max(file_name: Annotated[str, 'The name of the csv file containing data', True]) -> str:
    """
    向表格中添加 '最大值' 列，计算每行的最大值并可视化表格。

    参数:
    - file_name: CSV 文件的名称，包含要处理的数据。

    作用:
    - 计算每一行的数值列的最大值，并添加到 '最大值' 列。
    """
    file_path = f"./{file_name}"
    df = pd.read_csv(file_path, index_col=0)
    df['最大值'] = df.max(axis=1)
    df.to_csv(file_path, header=True)

    st.table(df)  # 可视化表格
    return "最大值列已成功添加并保存。"


@register_tool
def append_min(file_name: Annotated[str, 'The name of the csv file containing data', True]) -> str:
    """
    向表格中添加 '最小值' 列，计算每行的最小值并可视化表格。

    参数:
    - file_name: CSV 文件的名称，包含要处理的数据。

    作用:
    - 计算每一行的数值列的最小值，并添加到 '最小值' 列。
    """
    file_path = f"./{file_name}"
    df = pd.read_csv(file_path, index_col=0)
    df['最小值'] = df.min(axis=1)
    df.to_csv(file_path, header=True)

    st.table(df)  # 可视化表格
    return "最小值列已成功添加并保存。"


@register_tool
def delete_row(file_name: Annotated[str, 'The name of the csv file containing data', True],
               row_name: Annotated[str, 'The name of the row being deleted', True]) -> str:
    """
    删除指定名称的行并可视化表格。

    参数:
    - file_name: CSV 文件的名称，包含要处理的数据。
    - row_name: 要删除的行的名称（行索引）。

    作用:
    - 从表格中删除指定名称的行，并更新表格。
    """
    file_path = f"./{file_name}"
    df = pd.read_csv(file_path, index_col=0)
    if row_name not in df.index:
        return "无效的删除要求，未找到指定行。"

    df.drop(row_name, inplace=True)
    df.to_csv(file_path)

    st.table(df)  # 可视化表格
    return f"行 '{row_name}' 的数据已成功删除。"


@register_tool
def delete_column(file_name: Annotated[str, 'The name of the csv file containing data', True],
                  column_name: Annotated[str, 'The name of the column being deleted', True]) -> str:
    """
    删除指定名称的列并可视化表格。

    参数:
    - file_name: CSV 文件的名称，包含要处理的数据。
    - column_name: 要删除的列的名称（列标题）。

    作用:
    - 从表格中删除指定名称的列，并更新表格。
    """
    file_path = f"./{file_name}"
    df = pd.read_csv(file_path, index_col=0)

    if column_name not in df.columns:
        return "无效的删除要求，未找到指定列。"

    df.drop(column_name, axis=1, inplace=True)
    df['平均值'] = df.mean(axis=1)
    df['最大值'] = df.max(axis=1)
    df['最小值'] = df.min(axis=1)
    df.to_csv(file_path)

    st.table(df)  # 可视化表格
    return f"列 '{column_name}' 的数据已成功删除，并重新计算统计列。"


@register_tool
def append_row(file_name: Annotated[str, 'The name of the csv file containing data', True],
               row_name: Annotated[str, 'The name of the row being added', True],
               row_data: Annotated[list, 'The new row data', True]) -> str:
    """
    添加新行并可视化表格。

    参数:
    - file_name: CSV 文件的名称，包含要处理的数据。
    - row_name: 新行的名称（行索引）。
    - row_data: 新行的数据（应与表格的列数匹配）。

    作用:
    - 向表格中添加新行，并更新表格。如果数据不足，使用 None 填充。
    """
    file_path = f"./{file_name}"
    df = pd.read_csv(file_path, index_col=0)

    if row_name in df.index:
        return f"行 '{row_name}' 的数据已存在，无法添加重复数据。"

    # 如果 row_data 列数不足，使用 None 填充
    if len(row_data) < len(df.columns):
        row_data += [None] * (len(df.columns) - len(row_data))
    # 如果 row_data 列数多于 df.columns，裁剪掉多余的列
    elif len(row_data) > len(df.columns):
        row_data = row_data[:len(df.columns)]

    new_row = pd.DataFrame([row_data], columns=df.columns, index=[row_name])
    df = pd.concat([df, new_row])

    # 计算新的统计数据
    df['平均值'] = df.mean(axis=1)
    df['最大值'] = df.max(axis=1)
    df['最小值'] = df.min(axis=1)

    # 保存更新后的数据
    df.to_csv(file_path)

    # 可视化表格
    st.table(df)
    return f"行 '{row_name}' 的数据已成功添加。"


@register_tool
def append_column(file_name: Annotated[str, 'The name of the csv file containing data', True],
                  column_name: Annotated[str, 'The name of the column being added', True],
                  column_data: Annotated[list, 'The new column data', True]) -> str:
    """
    添加新列并可视化表格。

    参数:
    - file_name: CSV 文件的名称，包含要处理的数据。
    - column_name: 新列的名称（列标题）。
    - column_data: 新列的数据（应与表格的行数匹配）。

    作用:
    - 向表格中添加新列，并更新表格。
    """
    file_path = f"./{file_name}"
    df = pd.read_csv(file_path, index_col=0)

    if column_name in df.columns:
        return f"列 '{column_name}' 的数据已存在，无法添加重复数据。"

    df[column_name] = column_data
    df['平均值'] = df.mean(axis=1)
    df['最大值'] = df.max(axis=1)
    df['最小值'] = df.min(axis=1)
    df.to_csv(file_path)

    st.table(df)  # 可视化表格
    return f"列 '{column_name}' 的数据已成功添加。"


@register_tool
def update(file_name: Annotated[str, 'The name of the csv file containing data', True],
           column_name: Annotated[str, 'The name of the column being changed', True],
           row_name: Annotated[str, 'The name of the row being changed', True],
           value: Annotated[float, 'The new value', True]) -> str:
    """
    更新指定行和列的单元格数据并可视化表格。

    参数:
    - file_name: CSV 文件的名称，包含要处理的数据。
    - column_name: 要更新的列的名称（列标题）。
    - row_name: 要更新的行的名称（行索引）。
    - value: 要设置的新值。

    作用:
    - 更新表格中指定行和列的单元格数据，并更新表格。
    """
    file_path = f"./{file_name}"
    df = pd.read_csv(file_path, index_col=0)

    if row_name not in df.index or column_name not in df.columns:
        return "无效的更新请求，未找到指定的行或列。"

    df.loc[row_name, column_name] = value
    df['平均值'] = df.mean(axis=1)
    df['最大值'] = df.max(axis=1)
    df['最小值'] = df.min(axis=1)
    df.to_csv(file_path)

    st.table(df)  # 可视化表格
    return f"行 '{row_name}'，列 '{column_name}' 的数据已更新为 {value}。"


import matplotlib.pyplot as plt
import pandas as pd
import streamlit as st

@register_tool
def pie_chart(file_name: Annotated[str, 'The name of the csv file containing data', True],
              column_name: Annotated[str, 'The name of the column for the pie chart', True]) -> str:
    """
    绘制指定列的各行数据比例饼状图，并将图片保存到本地，然后在 Streamlit 中显示。

    参数:
    - file_name: CSV 文件的名称，包含要处理的数据。
    - column_name: 要绘制的列的名称。

    作用:
    - 根据指定列的数据，绘制各行数据比例的饼状图，并保存为 PNG 图片。
    """
    file_path = f"./{file_name}"
    df = pd.read_csv(file_path, index_col=0)

    if column_name not in df.columns:
        return f"列 '{column_name}' 的数据未找到。"

    fig, ax = plt.subplots()  # 创建子图
    ax.pie(df[column_name], labels=df.index, autopct="%.1f%%")
    ax.set_title(f"{column_name} 各行数据比例")
    ax.axis('equal')

    # 保存图片到本地
    image_file = f"pie_chart.png"
    fig.savefig(image_file)

    return f"列 '{column_name}' 的数据比例饼状图已保存为 {image_file}。"


@register_tool
def line_chart(file_name: Annotated[str, 'The name of the csv file containing data', True],
               row_name: Annotated[str, 'The name of the row for the line chart', True]) -> str:
    """
    绘制指定行的数据变化趋势图，并将图片保存到本地，然后在 Streamlit 中显示。

    参数:
    - file_name: CSV 文件的名称，包含要处理的数据。
    - row_name: 要绘制的行的名称。

    作用:
    - 根据指定行的数据，绘制各列数据的变化趋势折线图，并保存为 PNG 图片。
    """
    file_path = f"./{file_name}"
    df = pd.read_csv(file_path, index_col=0)

    if row_name not in df.index:
        return f"行 '{row_name}' 的数据未找到。"

    data = df.loc[row_name, df.columns.difference(['平均值', '最大值', '最小值'])]

    fig, ax = plt.subplots()  # 创建子图
    ax.plot(data, marker='o', linestyle='-', linewidth=2, color='blue')
    ax.set_xlabel("列名")
    ax.set_ylabel("值")
    ax.set_title(f"行 '{row_name}' 的数据变化趋势")

    # 保存图片到本地
    image_file = f"line_chart.png"
    fig.savefig(image_file)

    return f"行 '{row_name}' 的数据变化趋势图已保存为 {image_file}。"



if __name__ == "__main__":
    # print(dispatch_tool("get_shell", {"query": "pwd"}))
    print(get_tools())
