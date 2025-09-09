from Path import path
from typing import Callable


DEFAULT_DATA_PATH = '/Users/duuta/ocr-flaves/ghana_invoice_samples/'      


DEFAULT_MODELS = {
    'llava': {
        'name': "llava",
        'url': "http://localhost:11434",
        'tag': 'LLaVA',
         
    },  
    'bakllava':{
        'name': 'bakllava',
        'url': 'http://localhost:11435',
        'tag': 'baKLLaVA'
    }
}

