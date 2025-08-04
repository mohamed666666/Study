from enum import Enum



class AIModelType(str, Enum):
    gpt_model = "GPT Model"
    gpt_4o_mini_model = "GPT 4o Mini"
    llama_model = "LLamaModel 3.2"
    deep_seek_model = "DeepSeek Model"
