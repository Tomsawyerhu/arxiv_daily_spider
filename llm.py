from openai import OpenAI

base_url = "your base_url"
api_key = "your api_key"


def make_model():
    _client = OpenAI(
        base_url=base_url,
        api_key=api_key,
    )
    return _client


gpt_client = make_model()


def generate(prompt, model_name="qwen-plus", timeout=100, retry=100, num_samples=1):
    temperature = 0.0 if num_samples == 1 else 0.4
    if isinstance(prompt, str):
        prompt = [{
            'role': 'user',
            'content': prompt
        }]
    for i in range(retry):
        completion = gpt_client.chat.completions.create(
            model=model_name,
            messages=prompt,
            max_tokens=8000,
            temperature=temperature,
            n=num_samples,
            timeout=timeout
        )
        if not completion.choices or len(completion.choices) == 0:
            continue
        else:
            texts = [x.message.content for x in completion.choices]
            return texts
    print("No reply from GPT")
    return ""