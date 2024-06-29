"""
Tools for filling in prompt templates and extracting relevant bits of answers
(note that is all under assumption of prompting for numbers and numerical entailment).
"""

valid_numeral_words = [
    'single','one','two','three','four','five','six','seven','eight','nine','ten','none','zero'
]
valid_numerals = [
    '1','1','2','3','4','5','6','7','8','9','10','0','0'
]
num_dict = dict(zip(valid_numeral_words,valid_numerals))

safe_to_replace = [
    'A:','Answer:','User 0:','User 1:','User:', 'Assistant:', 'Question 2:',
]

def fill_query_template( query_template, **kwargs):
    return query_template.format( **kwargs)

def unmask_( masked_line, filled_line, mask_string= '<mask>'):
    """
    For the masked-prompting type of querying, where the model is expected to fill in
    the <mask> token with an appropriate answer. Note it is not as simple as knowing
    which token in the sequence was the <mask>, as LLMs do not always stick to just
    replacing the token... Below works in most cases for ChatGPT.
    """
    line_ = masked_line.split()
    response_ = filled_line.split()
    if len( line_) == len( response_):
        try:
            unmasked = [x for x,y in zip(line_,response_) if x!=y]
            assert len(unmasked) == 1
            return unmasked[0]
        except AssertionError:
            return unmasked

            
def extract_( query, answer):
    """
    For the question-answering type of querying, some attempts at high-level heuristics after 
    seeing some of Mistral's answers...
    """
    if len(answer.split()) == 1:
        return answer, None
    else:
        return answer, answer

def extract_relevant( query, answer, query_type):
    """
    Depending on `query_type` attempt to extract the relevant part of the answer.
    """
    
    if query_type == 'mask':
        return unmask_( query, answer)
    elif query_type == 'qa':
        return extract_( query, answer)
    else:
        raise Exception('Unsupported query type {query_type}. Choose `mask` or `qa`.')

        
def clean_token( token):
    return token.strip('*<>[]#,.;()"').strip()

def convert_to_number_( token):
    try:
        num = int( token)
    except ValueError:
        try: 
            num = int( num_dict[ token])
        except KeyError:
            num = token
    return num

def convert_to_number( guess):
    """
    Attempt to convert the passed string token to a supported integer.
    """
    guess = convert_to_number_(clean_token( guess))
    return guess

def convert_to_relation( guess):
    """
    Attempt to standardise the relation string to (`more`,`same`,`less`).
    """
    guess = clean_token( guess)
    return (
        guess.replace('fewer','less').replace('smaller','less').replace('lesser','less').replace('half','less').replace('few','less')
        .replace('equal','same').replace('identical','same').replace('matching','same')
        .replace('larger','more').replace('greater','more').replace('higher','more').replace('double','more')
    )

def try_set_difference( query, answer, preamble):
    q_tokens = [clean_token(x) for x in set(query.split())]
    a_tokens = [clean_token(x) for x in set(answer.split())]
    p_tokens = [clean_token(x) for x in set(preamble.split())]
    return (
        set( a_tokens) - set( q_tokens) - set( p_tokens) 
        - set(['actually','should','think','opposite','sentence','sorry','misunderstood'])
    )

def last_ditch( guess, query_subject):
    if query_subject == 'num':
        poss = [
            convert_to_number_(x) for x in guess.split()
        ]
        poss = [x for x in poss if type(x)==int]
        if len( set(poss))==1:
            guess = poss[0]
        return guess
    elif query_subject == 'rel':
        poss = set(guess.split()) & set(['more','less','same'])
        if len(poss)==1:
            guess = list(poss)[0]
        return guess

def canonise( token, query_subject):
    if query_subject == 'num':
        token_ = convert_to_number( token)
    elif query_subject == 'rel':
        token_ = convert_to_relation( token)
    return token_

def canonise_sentence( sentence, query_subject):
    return [ canonise( x, query_subject) for x in sentence.split()]

def keep_rel( clean_tokens):
    return sorted( set( clean_tokens) & set(['less','same','more']))

def extract_convert( query, answer, query_type, query_subject, preamble= '', elems= '', mode= 'lenient'):
    
    # first replace if repeated instruction and / or query etc.
    answer = answer.strip('\n').lower()
    for str_ in [preamble, query] + safe_to_replace:
        answer = answer.replace( str_.lower(), '')
    query = query.lower()
    
    #print(answer)
    
    # this is tricky (thanks for nothing, Mistral) - sometimes the Explanation
    # mentions additional numbers.. so the answers look wrong by our parsing
    # thing is, sometimes it's correct reasoning - e.g. sharks have 5 fins, two dorsal, ... 
    # sometimes it's incorrect reasoning - e.g. humans have 2 pedals per foot and that is 4 in total
    if mode == 'lenient':
        try:
            answer = answer.split('Explanation:')[0]
            if query_subject == 'rel':
                answer = answer.replace('numerous','more').replace('zero','less')                
        except IndexError:
            pass
    if len(answer.split())==1:
        return canonise( answer, query_subject)
    else:        
        query = query.replace('to/than','than')
        answer = answer.replace('to/than','than')
        
        if query_type == 'mask':
            line_ = query.strip('.').split()
            response_ = answer.strip('.').split()
            
            try:
                assert len( line_) == len( response_)
                unmasked = [(x,y) for x,y in zip(line_,response_) if x!=y]
                assert len(unmasked) == 1
                assert unmasked[0][0]=='<mask>'
                # only in the unmasking setting we can replace 'no' with '0' so it's not in the num_dict  
                # otherwise we'd run into problems with the other parsing route, of set of canonised tokens!
                unmasked_ = unmasked[0][1].replace('no','0')
                return canonise( unmasked_, query_subject)
            except AssertionError:
                pass
        
        
        if query_subject == 'num':   
            canonised_tokens = canonise_sentence( answer, query_subject)
            new_answer = '|'.join( [str(x) for x in set( canonised_tokens) if type(x)==int])
            try:
                return int( new_answer)
            except ValueError:
                
                xtra = ''
                if mode != 'lenient':
                    xtra = f' {elems}'
                    
                negations = [
                    f'{x}{xtra}' for x in [
                        'don\'t have', 'do not have', 'doesn\'t have', 'does not have',
                        'has no','have no', 'does not have any'
                    ]
                ]
                cond_ = ( 
                    any([ x in answer for x in negations])
                     or 'does not make sense' in answer or 'doesn\'t make sense' in answer
                )
                
                if new_answer == '':
                    if cond_:
                        return 0
                elif '|' in new_answer and mode == 'lenient':
                    if cond_:
                        return 0
                    
                    for sent in answer.split('.'):
                        out = sorted( set(
                            [x for x in canonise_sentence( answer.split('.')[0], query_subject) if type(x) == int]
                        ))
                        if len(out)==1:
                            return out[0]
                return new_answer
        elif query_subject == 'rel':
            set_ = keep_rel( canonise_sentence( answer, query_subject))
            if len( set_) == 0:
                return ''
            elif len( set_) == 1:
                return set_[0]
            else:
                sents = [x for x in answer.split('.')] 
                if query_type == 'mask':
                    sents = [x for x in sents if '<mask>' not in x]
                elif query_type == 'qa':
                    # in QA sometimes the first sentence is the single-token answer, 
                    # but then there are bs. explanations (without 'Explanation' string)
                    if len( sents[0].strip().split()) == 1:
                        sents = sents[:1]
                if mode != 'lenient':
                    sents = [x for x in sents if elems in x]
                set_ = []
                for sent in sents:
                    set_.extend( keep_rel( canonise_sentence( sent, query_subject)))
                set_ = sorted( set( set_))
                return '|'.join( set_)
            
            

       
            
    
    
    