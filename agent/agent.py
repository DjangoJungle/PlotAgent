import subprocess
import tools


def run_local_model(prompt, model_path):
    try:
        result = subprocess.run(
            ['../model/llama.cpp/llama-cli', '-m', model_path, '-p', prompt, ],  # 生成50个token
            capture_output=True, text=True
        )
        return result.stdout.strip()
    except Exception as e:
        return f"Error: {e}"


if __name__ == "__main__":
    model_path = "../model/starcoder2-15b-instruct-v0.1-Q4_K_M.gguf"  # 替换为你的模型路径

    # system_prompt = """You need to understand the intent of the user. If the user needs you to preprocess the tables or remove headers and footers, generate the following text: 'extract_comma_separated_tables('../data/年末常住人口.txt')'."""
    system_prompt = """
    You are required to strictly follow the instructions provided. Your task is to only generate a specific line of code if a condition is met.
    - If the user asks for table preprocessing or removing headers and footers, your output must be exactly:
    'extract_comma_separated_tables('../data/年末常住人口.txt')'
    - If the user's request is unrelated or unclear, do not generate any response. Simply respond with 'No action required.'

    Remember, only generate the specified code if the exact condition is met. Do not add any additional text or explanation.
    """

    context = system_prompt

    user_prompt = input("Your input >> ")
    context += f"  User: {user_prompt}"

    # 调用本地模型进行生成
    response = run_local_model(context, model_path)

    print("Response >>", response)

    # 处理模型的响应
    try:
        exec(response)
    except Exception as e:
        print(f"Invalid operation: {e}")
    # print("Response: >>", response)

    # context += response