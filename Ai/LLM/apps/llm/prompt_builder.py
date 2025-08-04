from typing import Any, List, Dict, Optional, Type
from pydantic import BaseModel
from langchain.memory import ConversationBufferMemory, ConversationSummaryBufferMemory
from langchain.output_parsers import PydanticOutputParser
from apps.llm.schema import PromptSchema
from langchain.schema import HumanMessage, SystemMessage
from apps.utils.logging import app_logger
 


class PromptBuilder:

    # create response schema as format_instruction
    def get_format_instructions(
        self, pydantic_model: Optional[Type[BaseModel]] = None
    ) -> str:
        if pydantic_model:
            parser = PydanticOutputParser(pydantic_object=pydantic_model)
            return parser.get_format_instructions()
        return ""

    @staticmethod
    def get_conversation_history(conversion_history: List[Dict], llm_model: Any) -> str:
        try:
            if not conversion_history:
                return "Empty conversation History"
            if len(conversion_history) < 5:
                memory = ConversationBufferMemory(llm=llm_model)
            else:
                memory = ConversationSummaryBufferMemory(
                    llm=llm_model, max_token_limit=1000
                )
            for message in conversion_history:
                memory.save_context(
                    {"input": message["user"]}, {"output": message["system"]}
                )
            prompt_with_history = memory.load_memory_variables({})["history"]
            app_logger.info("Prompt with history: %s", prompt_with_history)
            return prompt_with_history or "Empty conversation History"
        except Exception as e:
            app_logger.error(f"Error getting conversation history: {e}")
            return "Empty conversation History"

    def create_messages(
        self,
        prompt_schema: PromptSchema,
    ) -> List:
        if not prompt_schema.system_template:
            raise ValueError("No system template provided")
        if not prompt_schema.template_params:
            raise ValueError("No template parameters provided")
        messages = []
        if prompt_schema.system_template:
            system_content = prompt_schema.system_template.format(
                **prompt_schema.template_params
            )
            messages.append(SystemMessage(content=system_content))
        if prompt_schema.human_template:
            human_content = prompt_schema.human_template.format(
                **prompt_schema.template_params
            )
            messages.append(HumanMessage(content=human_content))
        return messages

    def generate_prompt(
        self,
        prompt_schema: PromptSchema,
    ):
        try:
            template_params = prompt_schema.template_params or {}
            if "conversion" in template_params and prompt_schema.llm_model:
                history = self.get_conversation_history(
                    template_params["conversion"], llm_model=prompt_schema.llm_model
                )
                template_params["history"] = history
            if prompt_schema.pydantic_model:
                template_params["format_instructions"] = self.get_format_instructions(
                    prompt_schema.pydantic_model
                )
            return self.create_messages(prompt_schema=prompt_schema)
        except Exception as e:
            app_logger.error(f"Error generating prompt: {e}")
            raise Exception("Error Generating Prompt")
