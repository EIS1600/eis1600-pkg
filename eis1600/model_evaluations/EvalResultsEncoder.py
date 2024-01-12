import json
from numpy import floating, integer, ndarray


class EvalResultsEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, integer):
            return int(obj)
        if isinstance(obj, floating):
            return float(obj)
        if isinstance(obj, ndarray):
            return obj.tolist()
        return super(EvalResultsEncoder, self).default(obj)
