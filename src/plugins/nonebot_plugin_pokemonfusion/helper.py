import difflib
import random
from io import BytesIO
from typing import Any, Optional
from typing import Dict

import ujson as json
from PIL import Image
from nonebot import logger

from src.resource import TemporaryResource
from src.service import OmegaRequests
from .config import pokemon_local_resource_config, sources, configs


def _load_config(file: TemporaryResource) -> Optional[Dict[str, Any]]:
    """从文件读取求签事件"""
    if file.is_file:
        logger.debug(f'loading fortune event form {file}')
        with file.open('r', encoding='utf8') as f:
            eat_config = json.loads(f.read())
        return eat_config
    else:
        return None


pokemon_json = _load_config(pokemon_local_resource_config.pokemons)


def string_similar(s1, s2):
    return difflib.SequenceMatcher(None, s1, s2).quick_ratio()


def get_3_similar_names(mylist, name):
    new_list = mylist.copy()
    similarity_list = [string_similar(i, name) for i in new_list]
    sorted_list = sorted(similarity_list, reverse=True)
    result_list = []
    for i in range(3):
        result_list.append(new_list[similarity_list.index(sorted_list[0])])
        similarity_list.remove(sorted_list[0])
        sorted_list.pop(0)
        new_list.remove(result_list[i])
    return result_list


def res2_bytes_io(res):
    if configs["enable_transparent"]:
        return BytesIO(res.content)
    else:
        im = Image.open(BytesIO(res.content)).convert("RGBA")
        p = Image.new('RGBA', im.size, (255, 255, 255))
        p.paste(im, (0, 0), mask=im)
        new_im = BytesIO()
        p.save(new_im, format="png")
        return new_im


async def get_image(fusion_id):
    head_id = fusion_id.split(".")[0]
    fusion_url = sources[configs["source"]]["custom"].format(n=head_id) + fusion_id
    logger.info(fusion_url)
    res = await OmegaRequests(timeout=10).get(url=fusion_url)
    if res.status_code != 404:
        return res2_bytes_io(res)
    else:
        fallback_fusion_url = sources[configs["source"]]["autogen"] + head_id + "/" + fusion_id
        res = await OmegaRequests(timeout=10).get(url=fallback_fusion_url)
        if res.status_code != 404:
            return res2_bytes_io(res)
        else:
            res_finally = await OmegaRequests(timeout=10).get(
                url="https://infinitefusion.gitlab.io/pokemon/question.png")
            return res2_bytes_io(res_finally)


async def pokemon_prompt_handle(pokemons: str):
    msgs = []
    fusion_ids = []
    pokemon_list = pokemons.split("+")
    if len(pokemon_list) == 2:
        for pokemon in pokemon_list:
            if pokemon not in pokemon_json:
                msgs.append(
                    f"未找到 {pokemon}！尝试以下结果：{'、'.join(get_3_similar_names(list(pokemon_list), pokemon))} ")
        if False not in [name in pokemon_json for name in pokemon_list]:
            fusion_ids = [f"{pokemon_json[pokemon_list[0]]}.{pokemon_json[pokemon_list[1]]}.png",
                          f"{pokemon_json[pokemon_list[1]]}.{pokemon_json[pokemon_list[0]]}.png"]
    elif len(pokemon_list) == 1 and pokemon_list != ['']:
        pokemon = pokemon_list[0]
        if pokemon not in pokemon_json:
            msgs = f"未找到 {pokemon}！尝试以下结果：{'、'.join(get_3_similar_names(list(pokemon_list), pokemon))} "
        else:
            a = random.randint(1, 420)
            fusion_ids = [f"{pokemon_json[pokemon]}.{a}.png", f"{a}.{pokemon_json[pokemon]}.png"]
    elif pokemon_list == ['']:
        a = random.randint(1, 420)
        b = random.randint(1, 420)
        fusion_ids = [f"{b}.{a}.png", f"{a}.{b}.png"]
    try:
        msgs = [fusion_id for fusion_id in fusion_ids]
    except:
        pass
    return msgs


__all__ = [
    get_image,
    pokemon_prompt_handle
]
