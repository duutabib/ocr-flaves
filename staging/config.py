
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

DOCUMENT_INDICATORS = {

            'invoice': [
                r'invoice', 
                r'bill to' | r'customer', 
                r'invoice number', 
                r'date',
                r'items',
                r'purchase order',
                r'subtotal', 
                r'tax',
                r'grand total' | r'Grand Total', 
            ],

            'receipt': [
                r'receipt', 
                r'date',
                r'payment', 
                r'amount paid', 
                r'paid by',
                r'paid to', 
            ],

            #'purchase order': [
                #r'purchase order', 
                #r'po', 
                #r'purchase order number', 
                #r'date',
                #r'customer',
                #r'items',
                #r'total', 
                #r'subtotal', 
                #r'tax',
            #],

            #'bill of materials': [
                #r'bill of materials', 
                #r'bill of materials number', 
                #r'date',
                #r'customer',
                #r'items',
                #r'total', 
                #r'subtotal', 
                #r'tax',
            #],

            #'deposit slip': [
                #r'deposit slip', 
                #r'deposit slip number', 
                #r'date',
                #r'customer',
                #r'items',
                #r'total', 
                #r'subtotal', 
                #r'tax',
            #],

            #'credit/debit memo': [
                #r'credit/debit memo', 
                #r'credit/debit memo number', 
                #r'date',
                #r'customer',
                #r'items',
                #r'total', 
                #r'subtotal', 
                #r'tax',
            #],

            #'petty cash voucher': [
                #r'petty cash voucher', 
                #r'petty cash voucher number', 
                #r'date',
                #r'customer',
                #r'items',
                #r'total', 
                #r'subtotal', 
                #r'tax',
            #],

        }
