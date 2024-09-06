# TableAgent

> 2024-09-05

## 1. 任务简介

### 1.1 任务目标

使用大语言模型（LLM）进行数据分析和可视化，通过自然语言与 LLM 交互生成 Python 代码，分析和可视化文本中的数据。

### 1.2 任务概述

1. 数据处理：设计合适的 prompt，指示 LLM 生成输出，读取文本文件，去除表头表尾，另存为一个新CSV 文件。
2. 数据分析：读取预处理后的 CSV 文件，设计合适的 prompt，指示 LLM 生成 Python 代码，对单个 CSV 文件进行增删改查以及数据可视化。
   1. 计算近 10 年各地区的人口均值、最大值和最小值，按列添加到表的最后。
   2. 以饼状图的形式，可视化近 10 年各地区的平均人口比例。
   3. 以折线图的形式，可视化近 10 年浙江省的人口变化趋势。
3. 仅使用本地大语言模型。



## 2. 具体实现

### 2.1 模型选取

项目选用了 **ChatGLM3** 模型，这是一款由清华大学和智谱AI联合开发的开源大规模语言模型，专注于中文自然语言处理任务，具备高效的推理性能和生成能力。同时该模型支持本地化部署，可以在无网络的环境中完成所有分析与可视化任务。

### 2.2 处理过程

有四个主要文件：

- **`main.py`**: 用于启动 `Streamlit` 应用，初始化页面配置，并处理与用户的交互。它是整个应用的入口，负责渲染页面布局、侧边栏、工具调用输入框等用户界面组件，并与其他模块协作完成工具调用和数据处理。

- **`demo_tool.py`**: 负责处理与工具调用相关的逻辑，通过与用户的输入进行互动，调用注册的工具，并实时展示工具的执行结果。

- **`client.py`**: 负责加载模型，通过流式生成的方式逐步返回对话生成结果。
- **`tool_registry.py`**: 负责管理和注册项目中的工具，并提供接口来调用这些工具。通过该文件，所有工具可以被动态注册和调度，提供了 `dispatch_tool` 方法，用于根据工具名和参数调用具体工具，并返回执行结果。

此外，使用了 `tool_chain`，其原理是将多个步骤的指令串联在一起，通过每一步生成的代码和数据输出作为下一个步骤的输入。这个工具链能够高效地将自然语言指令转化为具体的 Python 代码，实现自动化的数据处理与分析任务。每个步骤都会在执行过程中验证输出结果的正确性，确保生成的代码符合预期，并可以根据需要调整 Prompt 以优化生成的代码。

`TOOL_PROMPT`在`conversation.py`中定义如下：

![image-20240906150821117](assets/image-20240906150821117.png)

与如下的工具描述进行连接，提示agent其任务以及可以调用的工具列表及其属性。相当于整体上的`system_prompt`如下：

![image-20240906151058099](assets/image-20240906151058099.png)

### 2.3 tool_functions定义



### 2.4 用户交互

用户交互界面通过`streamlit`进行搭建，其初始界面如下：

![image-20240906153817792](assets/image-20240906153817792.png)

设置了表格数据展示、饼状图展示、折线图展示三个组件，上图未尚未生成时的状态，下图为生成后的状态：

| ![image-20240906154128777](assets/image-20240906154128777.png) | ![image-20240905211759885](assets/image-20240905211759885.png) | ![image-20240905212637264](assets/image-20240905212637264.png) |
| ------------------------------------------------------------ | ------------------------------------------------------------ | ------------------------------------------------------------ |



## 3. 部署指南

克隆本项目github代码：

```powershell
git clone https://github.com/DjangoJungle/PlotAgent
cd PlotAgent
```

创建虚拟环境：

```text
conda create -n chatglm python=3.11
conda activate chatglm
```

安装依赖：

```text
pip install -r requirements.txt
```

下载模型：

```
git clone https://www.modelscope.cn/ZhipuAI/chatglm3-6b.git
```

根据模型下载的路径更改`client.py`中的`MODEL_PATH`参数

运行模型：

```
cd PlotAgent/composite_demo
streamlit run main.py
```

> 整个过程的环境配置较为复杂，在最后的附录附上一个可运行的anaconda环境供参考
>
> 且如果配置不够且需要较流畅运行，需要对部分代码加上量化操作



## 4. 执行效果

* 表头表尾去除：

  | ![image-20240905190058535](assets/image-20240905190058535.png) | ![image-20240905190114072](assets/image-20240905190114072.png) |
  | ------------------------------------------------------------ | ------------------------------------------------------------ |

* 平均值计算并添加

  | ![image-20240905192248986](assets/image-20240905192248986.png) | ![image-20240905192324317](assets/image-20240905192324317.png) |
  | ------------------------------------------------------------ | ------------------------------------------------------------ |

* 最大、最小值添加

  | ![image-20240905193730947](assets/image-20240905193730947.png) | ![image-20240905193743009](assets/image-20240905193743009.png) |
  | ------------------------------------------------------------ | ------------------------------------------------------------ |

* 删除行、列

  | ![image-20240905200319083](assets/image-20240905200319083.png) | ![image-20240905200336148](assets/image-20240905200336148.png) | ![image-20240905200355278](assets/image-20240905200355278.png) |
  | ------------------------------------------------------------ | ------------------------------------------------------------ | ------------------------------------------------------------ |

* 增加行、列

  | ![image-20240905201921918](assets/image-20240905201921918.png) | ![image-20240905201933274](assets/image-20240905201933274.png) |
  | ------------------------------------------------------------ | ------------------------------------------------------------ |

* 查询数据

  | ![image-20240906152122076](assets/image-20240906152122076.png) |
  | ------------------------------------------------------------ |

* 更新数据

  | ![image-20240905205451660](assets/image-20240905205451660.png) | ![image-20240905205501924](assets/image-20240905205501924.png) |
  | ------------------------------------------------------------ | ------------------------------------------------------------ |

* 画饼状图

  | ![image-20240905211739077](assets/image-20240905211739077.png) | ![image-20240905211759885](assets/image-20240905211759885.png) |
  | ------------------------------------------------------------ | ------------------------------------------------------------ |

* 画折线图

  | ![](assets/image-20240905212649348.png) | ![image-20240905212637264](assets/image-20240905212637264.png) |
  | --------------------------------------- | ------------------------------------------------------------ |
  
  
  
  ## 附：anaconda环境参考
  
  ```
  # packages in environment at D:\anaconda3\envs\chatglm3:
  #
  # Name                    Version                   Build  Channel
  accelerate                0.24.0                   pypi_0    pypi
  altair                    5.4.1                    pypi_0    pypi
  attrs                     24.2.0                   pypi_0    pypi
  blinker                   1.8.2                    pypi_0    pypi
  bzip2                     1.0.8                h2bbff1b_6
  ca-certificates           2024.7.2             haa95532_0
  cachetools                5.5.0                    pypi_0    pypi
  certifi                   2024.8.30                pypi_0    pypi
  charset-normalizer        3.3.2                    pypi_0    pypi
  click                     8.1.7                    pypi_0    pypi
  contourpy                 1.3.0                    pypi_0    pypi
  cpm-kernels               1.0.11                   pypi_0    pypi
  cycler                    0.12.1                   pypi_0    pypi
  filelock                  3.15.4                   pypi_0    pypi
  fonttools                 4.53.1                   pypi_0    pypi
  fsspec                    2024.6.1                 pypi_0    pypi
  gitdb                     4.0.11                   pypi_0    pypi
  gitpython                 3.1.43                   pypi_0    pypi
  huggingface-hub           0.19.4                   pypi_0    pypi
  idna                      3.8                      pypi_0    pypi
  intel-openmp              2021.4.0                 pypi_0    pypi
  ipykernel                 6.29.5                   pypi_0    pypi
  ipython                   8.27.0                   pypi_0    pypi
  jinja2                    3.1.4                    pypi_0    pypi
  jsonschema                4.23.0                   pypi_0    pypi
  jsonschema-specifications 2023.12.1                pypi_0    pypi
  jupyter-client            8.6.2                    pypi_0    pypi
  kiwisolver                1.4.7                    pypi_0    pypi
  libffi                    3.4.4                hd77b12b_1
  markdown-it-py            3.0.0                    pypi_0    pypi
  markupsafe                2.1.5                    pypi_0    pypi
  matplotlib                3.9.2                    pypi_0    pypi
  mdurl                     0.1.2                    pypi_0    pypi
  mkl                       2021.4.0                 pypi_0    pypi
  mpmath                    1.3.0                    pypi_0    pypi
  narwhals                  1.6.2                    pypi_0    pypi
  networkx                  3.3                      pypi_0    pypi
  numpy                     2.1.1                    pypi_0    pypi
  openssl                   3.0.14               h827c3e9_0
  packaging                 24.1                     pypi_0    pypi
  pandas                    2.2.2                    pypi_0    pypi
  pillow                    10.4.0                   pypi_0    pypi
  pip                       24.2            py311haa95532_0
  prompt-toolkit            3.0.47                   pypi_0    pypi
  protobuf                  5.28.0                   pypi_0    pypi
  pyarrow                   17.0.0                   pypi_0    pypi
  pydeck                    0.9.1                    pypi_0    pypi
  pyparsing                 3.1.4                    pypi_0    pypi
  python                    3.11.9               he1021f5_0
  pytz                      2024.1                   pypi_0    pypi
  pyyaml                    6.0.2                    pypi_0    pypi
  referencing               0.35.1                   pypi_0    pypi
  regex                     2024.7.24                pypi_0    pypi
  requests                  2.32.3                   pypi_0    pypi
  rich                      13.8.0                   pypi_0    pypi
  rpds-py                   0.20.0                   pypi_0    pypi
  safetensors               0.4.4                    pypi_0    pypi
  sentencepiece             0.2.0                    pypi_0    pypi
  setuptools                72.1.0          py311haa95532_0
  smmap                     5.0.1                    pypi_0    pypi
  sqlite                    3.45.3               h2bbff1b_0
  streamlit                 1.38.0                   pypi_0    pypi
  sympy                     1.13.2                   pypi_0    pypi
  tbb                       2021.13.1                pypi_0    pypi
  tenacity                  8.5.0                    pypi_0    pypi
  tk                        8.6.14               h0416ee5_0
  tokenizers                0.19.1                   pypi_0    pypi
  toml                      0.10.2                   pypi_0    pypi
  torch                     2.3.1+cu121              pypi_0    pypi
  tqdm                      4.66.5                   pypi_0    pypi
  traitlets                 5.14.3                   pypi_0    pypi
  transformers              4.40.0                   pypi_0    pypi
  typing-extensions         4.12.2                   pypi_0    pypi
  tzdata                    2024.1                   pypi_0    pypi
  urllib3                   2.2.2                    pypi_0    pypi
  vc                        14.40                h2eaa2aa_0
  vs2015_runtime            14.40.33807          h98bb1dd_0
  watchdog                  4.0.2                    pypi_0    pypi
  wheel                     0.43.0          py311haa95532_0
  xz                        5.4.6                h8cc25b3_1
  zlib                      1.2.13               h8cc25b3_1
  ```
  
  
  
  