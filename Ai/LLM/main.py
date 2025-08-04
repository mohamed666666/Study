from llm_clean.presentation.api.api import LLM ,Prompt ,AIModelType,settings


llm = LLM(AIModelType.gpt_4o_mini_model,settings(temperature=0.5,max_tokens=100,top_p=1.0,presence_penalty=0.0,frequency_penalty=0.0,stop=None,extra={}))
prompt = Prompt(prompt="Hello, how are you?", role="user")
response = llm.get_response(prompt)
print(response)