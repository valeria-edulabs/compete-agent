from pprint import pprint

from langchain.tools import BaseTool
from typing import Optional, Type, Union

from langchain_experimental.tools import PythonAstREPLTool
from pydantic import BaseModel, PrivateAttr
import pandas as pd
import plotly.graph_objects as go
import ast

class PythonResult(BaseModel):
    type: str  # "plot", "table", "text"
    result: Union[str, pd.DataFrame, go.Figure]
    code: str

    class Config:
        arbitrary_types_allowed = True

class PythonToolWithResult(PythonAstREPLTool):
    _last_result: Optional[PythonResult] = PrivateAttr(default=None)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    @property
    def last_result(self):
        return self._last_result

    @last_result.setter
    def last_result(self, value):
        self._last_result = value

    def _run(self, query: str, run_manager=None) -> str:
        result = super()._run(query, run_manager)
        print(f"result type: {type(result)}")
        if isinstance(result, pd.DataFrame):
            result_type = "table"
        elif isinstance(result, go.Figure):
            result_type = "plot"
        else:
            result_type = "text"
        self.last_result = PythonResult(type=result_type, result=result, code=query)
        return result
