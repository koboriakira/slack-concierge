from openai import OpenAI


class TagAnalyzer:
    def analyze_tags(text: str) -> list[str]:
        return use_openai(text=text)

def analyze_tags(tags: str) -> list[str]:
    print("analyze_tags: " + tags)
    return tags.split(",")

def use_openai(text: str) -> list[str]:
    print("use_openai: " + text)
    client = OpenAI()
    messages = [
        {"role": "user", "content": f"次の文章を解析して、タグをつけてください。\n\n{text}"}
    ]
    tools = [
        {
            "type": "function",
            "function": {
                "name": "analyze_tags",
                "description": "タグをつける",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "tags": {
                            "type": "string",
                            "description": "タグのリスト。カンマ区切りで複数指定可能\n例) 文章術, プロレス, 資産運用",
                        },
                    },
                    "required": ["tags"],
                },
            }

        }
    ]
    response = client.chat.completions.create(
        model="gpt-4-turbo-preview",
        messages=messages,
        tools=tools,
        tool_choice="auto",
    )
    print(response)
    response_message = response.choices[0].message
    print(response_message)
    tool_calls = response_message.tool_calls
    print(tool_calls)

    if not tool_calls:
        return []

    # Step 3: call the function
    # Note: the JSON response may not always be valid; be sure to handle errors
    available_functions = {
        "analyze_tags": analyze_tags,
    }  # only one function in this example, but you can have multiple
    messages.append(response_message)  # extend conversation with assistant's reply
    # Step 4: send the info for each function call and function response to the model
    for tool_call in tool_calls:
        function_name = tool_call.function.name
        function_to_call = available_functions[function_name]
        import json
        function_args = json.loads(tool_call.function.arguments)
        function_response = function_to_call(
            tags=function_args.get("tags"),
        )
        return function_response
