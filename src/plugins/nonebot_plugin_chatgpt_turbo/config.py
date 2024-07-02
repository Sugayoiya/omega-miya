from typing import Optional

from pydantic import Extra, BaseModel


class Config(BaseModel, extra=Extra.ignore):
    api_key: Optional[str] = ""  # （必填）OpenAI官方或者是支持OneAPI的大模型中转服务商提供的KEY
    api_url: Optional[str] = ""  # （可选）大模型中转服务商提供的中转地址，使用OpenAI官方服务不需要填写
    api_model: Optional[str] = "gpt-4o"  # （可选）使用的语言大模型，使用识图功能请填写合适的大模型名称
    enable_private_chat: bool = True  # 是否开启私聊对话
    # chatgpt_turbo_public: bool = True  # 是否开启群聊对话


class ConfigError(Exception):
    pass
