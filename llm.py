import json
import logging
from typing import Literal
from openai import OpenAI
from openai.types.chat.chat_completion_message import ChatCompletionMessage
import re
from setup_logger import setup

logger = setup('LLM')
logger.setLevel(logging.DEBUG)
# deepseek文档: https://api-docs.deepseek.com/zh-cn

# client = OpenAI(api_key="sk-e7c39b8d1fe74e15a4ec85a2bd3a2a0a", base_url="https://api.deepseek.com")
client = OpenAI(api_key="sk-b5d571e518da467aa4e991370f473fa1", base_url="https://dashscope.aliyuncs.com/compatible-mode/v1")
DS_OFFICAL_MODEL_TYPE = Literal['deepseek-chat', 'deepseek-coder']
ALI_MODEL_TYPE = Literal['deepseek-v3', 'deepseek-r1']


def simple_request(user_prompt: str,
                   system_prompt: str = '',
                   model_type: ALI_MODEL_TYPE = 'deepseek-v3',
                   content_only: bool = True):
    if isinstance(user_prompt, str):
        if system_prompt:
            messages = [{"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_prompt}]
        else:
            messages = [{"role": "user", "content": user_prompt}]
    elif isinstance(user_prompt, list) or isinstance(user_prompt, ChatCompletionMessage):
        messages = user_prompt
    else:
        return None
    response = client.chat.completions.create(
        model=model_type,
        messages=messages
    )
    if content_only:
        return response.choices[0].message.content
    return response


def nl2json_request(user_prompt: str,
                    example_json: dict,
                    example_prompt: str,
                    model_type: ALI_MODEL_TYPE = 'deepseek-v3') -> dict:
    system_prompt = f"""
根据样例的json输出，将用户输入格式化为json样例的格式，有以下规则，0 1 2为基本规则，必须保证实现，3 4 为进阶规则：
0. 一定要保证样例json的字段存在
1. 数据类型都自行判断
2. 用户输入不存在样例json对应的字段则将输出json的值置null
3. 若在样例输入和用户输出中都出现疑似json字段但样例json没有，那就没必要添加到你的输出
4. 出现多余的字段就追加到json尾部
样例输入: 
{example_prompt}
样例json输出:
{json.dumps(example_json)}
"""
    messages = [{"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}]
    response = client.chat.completions.create(
        model=model_type,
        messages=messages
    )
    return json.loads(response.choices[0].message.content)


def nl2shell_request(raw_call: str) -> str:
    script_nl = simple_request(f'请给出使用Windows PowerShell脚本 完成以下操作的所需脚本代码： {raw_call}',
                               '你是一个专业的Windows PowerShell运维工程师，善于使用PowerShell解决多种Windows系统操作问题',
                               'deepseek-v3')
    logger.debug(f'{script_nl = }')
    raw_script = simple_request(script_nl, f'你是一个专业的powershell代码审计工程师，'
                                           f'请你审计用户输入的代码，输出为一段完整的可直接执行的powershell代码',
                                'deepseek-v3')
    logger.debug(f'{raw_script = }')
    pattern = r'```powershell(.*?)```'
    match = re.search(pattern, raw_script, re.DOTALL)
    if match:
        return match.group(1).strip()
    return ''


if __name__ == '__main__':
    print(nl2shell_request('解压根目录下名为test.zip的文件'))
