from __future__ import annotations

from importlib import import_module
from typing import Any, Tuple

from fvcore.common.config import CfgNode as _CfgNode

MODULE_KEY = 'module'
CLASS_KEY = 'class'
EXTRALIBS_KEY = 'extralibs'
NAME_KEY = 'name'
RM_KEY = 'rm_keys'
EVAL_VALUE_KEY = 'eval_value'

NOT_EVAL_KEYWORDS = [
    MODULE_KEY,
    CLASS_KEY,
    EXTRALIBS_KEY,
    NAME_KEY,
    RM_KEY,
]


class CfgNode(_CfgNode):
    def __init__(self, *args, **kwargs):
        super(CfgNode, self).__init__(*args, **kwargs)
        self.__dict__[EVAL_VALUE_KEY] = None

    @staticmethod
    def _eval(config: Any, global_context: dict, local_context: dict, eval_all: bool = False) -> Any:
        if isinstance(config, dict):
            for key, value in config.items():
                if eval_all or key not in NOT_EVAL_KEYWORDS:
                    config[key] = CfgNode._eval(value, global_context, local_context)

            if MODULE_KEY in config and CLASS_KEY in config:
                module = config[MODULE_KEY]
                class_ = config[CLASS_KEY]
                config_kwargs = config.get(class_, {})
                return getattr(import_module(module), class_)(**config_kwargs)

        elif isinstance(config, list):
            config = list(map(lambda ele: CfgNode._eval(ele, global_context, local_context), config))

        elif isinstance(config, str):
            config = eval(config, global_context, local_context)

        return config

    def eval(self) -> Tuple[Any, dict]:
        # If config was evaluated, return evaluated value
        if self.__dict__[EVAL_VALUE_KEY] is not None:
            return self.__dict__[EVAL_VALUE_KEY]

        config = org_config = self.clone()
        extralibs = {}

        # Generate extra libs
        for alias, lib_info in config.pop(EXTRALIBS_KEY, {}).items():
            if isinstance(lib_info, dict):
                module = lib_info[MODULE_KEY]
                name = lib_info[NAME_KEY]
                lib = getattr(import_module(module), name)
            else:
                lib = import_module(lib_info)

            extralibs[alias] = lib

        # Eval config
        config = CfgNode._eval(config, extralibs, org_config)

        # Remove unnecessary keys
        if isinstance(config, dict):
            for rm_key in config.pop(RM_KEY, []):
                del config[rm_key]

        # Save evaluated config and freeze config
        self.__dict__[EVAL_VALUE_KEY] = config
        self.freeze()

        return config, extralibs

    def __delitem__(self, name: str) -> None:
        name_parts = name.split('.')
        dic = self

        for name_part in name_parts[:-1]:
            dic = dic[name_part]

        super(CfgNode, dic).__delitem__(name_parts[-1])

    def get(self, name: str, default: Any = None) -> Any:
        name_parts = name.split('.')
        dic = self

        for name_part in name_parts[:-1]:
            dic = dic.get(name_part, CfgNode())

        return super(CfgNode, dic).get(name_parts[-1], default)

    def state_dict(self) -> str:
        return self.dump(sort_keys=False)

    @classmethod
    def load_yaml_with_base(cls, filename: str, allow_unsafe: bool = False) -> CfgNode:
        cfg = super(CfgNode, cls).load_yaml_with_base(filename, allow_unsafe)
        return cls(cfg)


global_cfg = CfgNode(new_allowed=True)
