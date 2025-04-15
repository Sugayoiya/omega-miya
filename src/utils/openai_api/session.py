"""
@Author         : Ailitonia
@Date           : 2025/2/13 11:18:42
@FileName       : session.py
@Project        : omega-miya
@Description    : 基于 openai API 的服务
@GitHub         : https://github.com/Ailitonia
@Software       : PyCharm 
"""

from typing import TYPE_CHECKING, Any, Literal, Self, overload

import ujson as json

from .api import BaseOpenAIClient
from .helpers import encode_local_audio, encode_local_file, encode_local_image, encode_bytes_image
from .models import Message, MessageContent

if TYPE_CHECKING:
    from pydantic import BaseModel
    from src.resource import BaseResource


class ChatSession:
    """对话会话基类"""

    def __init__(
            self,
            service_name: str,
            model_name: str,
            *,
            default_user_name: str | None = None,
            init_system_message: str | None = None,
            init_assistant_message: str | None = None,
            use_developer_message: bool = False,
            max_messages: int = 20,
    ) -> None:
        self.client = BaseOpenAIClient.init_from_config(service_name=service_name, model_name=model_name)
        self.default_user_name = default_user_name
        self.model = model_name
        self.message = Message(max_messages=max_messages)
        if init_system_message is not None:
            self.message.set_prefix_content(
                system_text=init_system_message,
                assistant_text=init_assistant_message,
                use_developer=use_developer_message,
            )

    @classmethod
    def init_default_from_config(
            cls,
            *,
            default_user_name: str | None = None,
            init_system_message: str | None = None,
            init_assistant_message: str | None = None,
            use_developer_message: bool = False,
    ) -> Self:
        """从配置文件中初始化, 使用第一个可用配置项"""
        if not (available_services := BaseOpenAIClient.get_available_services()):
            raise RuntimeError('no openai service has been config')
        return cls(
            *available_services[0],
            default_user_name=default_user_name,
            init_system_message=init_system_message,
            init_assistant_message=init_assistant_message,
            use_developer_message=use_developer_message,
        )

    def reset_chat(self) -> None:
        """重置会话到初始状态"""
        self.message.clear_chat_messages()

    async def add_chat_audio(
            self,
            audio: 'BaseResource',
            *,
            user_name: str | None = None,
    ) -> None:
        """向会话 Message 序列中添加本地音频"""
        audio_data, format_ = await encode_local_audio(audio)
        self.message.add_content(MessageContent.user(name=user_name).add_audio(audio_data, format_=format_))

    async def add_chat_file(
            self,
            file: 'BaseResource | None' = None,
            file_id: str | None = None,
            filename: str | None = None,
            *,
            user_name: str | None = None,
    ) -> None:
        """向会话 Message 序列中添加文件, 本地文件优先"""
        if not any((file, file_id, filename)):
            raise ValueError('None of any "file", "file_id", "filename"')

        if file is not None:
            file_data = await encode_local_file(file)
            message_content = MessageContent.user(name=user_name).add_file(file_data=file_data)
        else:
            message_content = MessageContent.user(name=user_name).add_file(file_id=file_id, filename=filename)

        self.message.add_content(message_content)

    async def add_chat_image(
            self,
            image: 'BaseResource | str',
            *,
            user_name: str | None = None,
            detail: Literal['low', 'high', 'auto'] | None = None,
            encoding_web_image: bool = True,
    ) -> None:
        """向会话 Message 序列中添加图片

        :param image: 图片文件或图片 url
        :param user_name: An optional name for the participant.
        :param detail: What level of detail to use when processing and understanding the image
        :param encoding_web_image: 是否编码网络图片
        """
        if isinstance(image, str):
            if encoding_web_image:
                image_url = await encode_bytes_image(await self.client.get_any_resource_as_bytes(url=image))
            else:
                image_url = image
        else:
            image_url = await encode_local_image(image)
        self.message.add_content(MessageContent.user(name=user_name).add_image(image_url, detail=detail))

    async def simple_chat(self, **kwargs) -> str:
        """使用现有 Message 序列发起对话, 返回响应对话内容"""
        result = await self.client.create_chat_completion(
            model=self.model,
            message=self.message,
            **kwargs,
        )

        reply_message = result.choices[0].message
        self.message.add_content(reply_message)
        return reply_message.plain_text

    async def chat(
            self,
            text: str,
            *,
            user_name: str | None = None,
            **kwargs,
    ) -> str:
        """用户发起对话, 返回响应对话内容"""
        user_name = user_name if user_name is not None else self.default_user_name
        self.message.add_content(MessageContent.user(name=user_name).set_plain_text(text))

        return await self.simple_chat(**kwargs)

    @overload
    async def chat_query_json[T: 'BaseModel'](
            self,
            text: str,
            model_type: type[T],
            *,
            user_name: str | None = None,
            **kwargs,
    ) -> T:
        ...

    @overload
    async def chat_query_json[T: 'BaseModel'](
            self,
            text: str,
            model_type: None,
            *,
            user_name: str | None = None,
            **kwargs,
    ) -> Any:
        ...

    async def chat_query_json[T: 'BaseModel'](
            self,
            text: str,
            model_type: type[T] | None = None,
            *,
            user_name: str | None = None,
            **kwargs,
    ) -> T | Any:
        """用户发起对话, 指定 JSON 响应, 并尝试解析响应返回值, 若提供了 `model_type` 则尝试解析到该模型"""
        user_name = user_name if user_name is not None else self.default_user_name
        self.message.add_content(MessageContent.user(name=user_name).set_plain_text(text))

        reply_text = await self.simple_chat(
            response_format={'type': 'json_object'},
            **kwargs,
        )

        # 处理被标注的消息格式
        json_text = reply_text.removeprefix('```json').removesuffix('```').strip()
        return model_type.model_validate_json(json_text) if model_type is not None else json.loads(json_text)

    async def chat_query_schema[T: 'BaseModel'](
            self,
            text: str,
            model_type: type[T],
            *,
            user_name: str | None = None,
            **kwargs,
    ) -> T:
        """用户发起对话, 指定结构化响应, 并解析响应返回值"""
        user_name = user_name if user_name is not None else self.default_user_name
        self.message.add_content(MessageContent.user(name=user_name).set_plain_text(text))

        reply_text = await self.simple_chat(
            response_format={
                'type': 'json_schema',
                'json_schema': {
                    'name': model_type.__name__,
                    'schema': model_type.model_json_schema(mode='serialization'),
                    'strict': True,
                }
            },
            **kwargs,
        )

        # 处理被标注的消息格式
        return model_type.model_validate_json(reply_text.removeprefix('```json').removesuffix('```').strip())


__all__ = [
    'ChatSession',
]
