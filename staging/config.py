
DEFAULT_DATA_PATH = '/Users/duuta/ocr-flaves/data/'

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
    },

    'internvl':{
        'name': 'internvl',
        'url': 'http://localhost:11436',
        'tag': 'internVL'
    }
}

# Document indicators
DOCUMENT_INDICATORS = {

            'invoice': [
                r'vendor_name', 
                r'vendor_email',
                r'vendor_phone',
                r'bill to|customer', 
                r'invoice number', 
                r'date',
                r'items',
                r'purchase order',
                r'subtotal', 
                r'tax_amount',
                r'grand total|Grand Total|total_amount', 
                r'currency',
            ],

            'receipt': [
                r'receipt', 
                r'date',
                r'payment', 
                r'amount paid', 
                r'paid by',
                r'paid to', 
            ],

        }
