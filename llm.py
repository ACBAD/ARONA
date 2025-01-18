import json
from typing import Literal
from openai import OpenAI

# deepseek文档: https://api-docs.deepseek.com/zh-cn

client = OpenAI(api_key="sk-e7c39b8d1fe74e15a4ec85a2bd3a2a0a", base_url="https://api.deepseek.com")


def simple_request(user_prompt: str,
                   system_prompt: str = '',
                   model_type: Literal['deepseek-chat', 'deepseek-coder'] = 'deepseek-chat',
                   content_only: bool = True):
    if system_prompt:
        messages = [{"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}]
    else:
        messages = [{"role": "user", "content": user_prompt}]
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
                    model_type: Literal['deepseek-chat', 'deepseek-coder'] = 'deepseek-chat') -> dict:
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
        messages=messages,
        response_format={
            'type': 'json_object'
        }
    )
    return json.loads(response.choices[0].message.content)


def nl2shell_request(raw_call: str):
    pass


if __name__ == '__main__':
    # noinspection SpellCheckingInspection
    print(nl2json_request('稀有度★★，所属组织千禧科学学院，主要关系研讨会，身高156 cm，'
                          '生日3月14日，日语配音春花兰，中文配音小敢，别名邮箱,没包人,半包人,管账婆，年龄16，'
                          '爱好计算，角色设计Hwansang，角色原画Hwansang，日文名早瀬 ユウカ，'
                          '英文名Hayase Yuuka，韩文名하야세 유우카，繁中译名早瀬 優香',
                          {'所属组织': '夏莱', '身高': '145cm', '英文名': 'Arona'},
                          '所属组织夏莱，主要关系什亭之匣，身高145 cm，日语配音小原好美，'
                          '中文配音Sakula小舞，别名蓝色恶魔，角色设计HWANSANG，'
                          '角色原画HWANSANG，日文名アロナ，英文名Arona，韩文名아로나，繁中译名彩奈'))
