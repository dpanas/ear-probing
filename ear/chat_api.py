import openai

from .utilities import from_text
from .prompt_selection import PROMPT_NUMBER_MASK, PROMPT_RELATIONSHIP_MASK

openai.api_key = from_text('../../../tru-ll.txt')[0][0]

valid_numeral_words = [
    'one','two','three','four','five','six','seven','eight','nine','ten','no','zero'
]
valid_numerals = [
    '1','2','3','4','5','6','7','8','9','10','0','0'
]
num_dict = dict(zip(valid_numeral_words,valid_numerals))


def get_chat_answer( 
    prompt, model, 
    temperature= 0, max_tokens= 64, frequency_penalty= 0 , presence_penalty= 0, **kwargs
):
    """
    Wrapper around OpenAIs API, defaulting some params for convenience, e.g. temperature to 0 for
    reproducibility, tokens limited to a feasible answer length etc, and returning the text response
    without the meta-data.
    """
    response_full = openai.ChatCompletion.create(
        model= model, temperature= temperature, max_tokens= max_tokens, 
        frequency_penalty= frequency_penalty, presence_penalty= presence_penalty,
        messages= [{"role":"user", "content": prompt}]
    )
    return response_full.choices[0].message['content']

def get_model_answer(
    prompts, pipeline, **kwargs
):    
    if "batch_size" not in kwargs:
        kwargs["batch_size"] = 1

    if "max_new_tokens" not in kwargs:
        kwargs["max_new_tokens"] = 64

    kwargs.update({
        "pad_token_id": pipeline.tokenizer.eos_token_id,
        "eos_token_id": pipeline.tokenizer.eos_token_id,
        "temperature":None,
        "top_p":None
    })

    outputs = pipeline( prompts, **kwargs)

    return [out[0]["generated_text"] for out in outputs]

def unmask_( masked_line, filled_line, mask_string= '<mask>'):
    line_ = masked_line.split()
    response_ = filled_line.split()
    
    try:        
        # we expect the mask to be simply replaced with appropriate word:
        assert len( response_) == len( line_)
        mask_pos = [ii for ii, tok in enumerate(line_) if tok == mask_string][0]
        guess = response_[ mask_pos]
        return guess, None
    except AssertionError:
        # however, sometimes Chat has less - or more - to say :P
        
        if len( response_) == 1:
            return response_[0], filled_line
        elif len(response_) < len( line_):
            return filled_line, filled_line
        try:
            # sometimes the response is longer, e.g. two part numeral (twenty two) or a hallucination:
            pre_mask, post_mask = masked_line.split( mask_string)
            for_guess = filled_line.split( pre_mask)[1] if pre_mask != '' else filled_line
            guess = for_guess.split( post_mask)[0] if post_mask != '' else for_guess
            return guess, filled_line
        except Exception as eek:
            # for numerical entailment, it sometimes rephrases the question? <sigh>
            try:
                # FIXME: a hack for now, since using a template
                pre_snip = ' '.join( pre_mask.split()[-3:])
                post_snip = ' '.join( post_mask.split()[:3])
                guess = filled_line.split( pre_snip)[1].split( post_snip)[0].strip()
                return guess, filled_line
            except Exception as eek:
                return None, filled_line
            
def get_chat_mask_guess( 
    line, prompt, model= "gpt-3.5-turbo", test_mode= False
):
    """
    Further wrapper specifically for *masked* prompting - assumes a single <mask> token that is
    to be filled by the API, .
    """
    prompt_ = prompt.format( sentence= line) 
    if test_mode:
        print(prompt_)
    response = get_chat_answer( prompt_, model= model)
    return unmask_( line, response, '<mask>')

def fill_in_1( fact_prompt, thing, elements):
    return fact_prompt.replace('{thing}',thing).replace('{elements}',elements)

def fill_in_2( fact_entailed, thing_a, thing_b, elements_a, elements_b):
    fact = fact_entailed.replace('{thing_a}',thing_a).replace('{thing_b}',thing_b)
    return fact.replace('{elements_a}',elements_a).replace('{elements_b}',elements_b)

def fill_query_template( query_template, **kwargs):
    return query_template.format( **kwargs)

def numerical_fact( 
    thing, elements, model= "gpt-3.5-turbo", 
    fact_prompt= None, prompt= None, test_mode= False
):
    prompt = prompt if prompt is not None else PROMPT_NUMBER_MASK
    fact_prompt = fact_prompt if fact_prompt is not None else 'A <thing> usually has <mask> <elements>.'
    fact = fill_in_1( fact_prompt, thing, elements)
    guess, exc = get_chat_mask_guess( fact, prompt, model= model, test_mode= test_mode)
    try:
        guess_ = guess.strip('*<>[]#')
        try:
            num = int( guess_)
        except ValueError:
            try:
                num = int( num_dict[ guess_])
            except KeyError:
                num = guess
        return num
    except Exception:
        return exc
        
def numerical_relationship( 
    thing_a, thing_b, elements_a, elements_b, model= "gpt-3.5-turbo", 
    fact_entailed= None, prompt= None, test_mode= False
):
    prompt = prompt if prompt is not None else PROMPT_RELATIONSHIP_MASK
    fact_entailed = fact_entailed if fact_entailed is not None else (
        f'A typical <thing_a> has a number of <elements_a> that is'
        + ' <mask> '
        + f'than the number of <elements_b> that a typical <thing_b> has.'
    )
    fact = fill_in_2( fact_entailed, thing_a, thing_b, elements_a, elements_b)
    return get_chat_mask_guess( fact, prompt, model= model, test_mode= test_mode)
    
def numerical_entailment( thing_a, thing_b, elements_a, elements_b, model= "gpt-3.5-turbo"):
    """
    *Provisional* function for eliciting very basic numerical entailment. Check for two 'atomic
    facts' in the numerical domain; extract values for numerical comparison (truth of the 
    numerical entailment) and get chat answer about the relationship.
    
    TODO: currently assuming 'valid' numbers & numerals between 0 - 10, consider more?
    TODO: prompts are hard-coded and may have clues in grammar!    
    """
    
    nums = [
        numerical_fact( thing_a, elements_a), numerical_fact( thing_b, elements_b)
    ]    
    
    guess_rel = numerical_relationship( thing_a, thing_b, elements_a, elements_b, model)
    return nums, guess_rel