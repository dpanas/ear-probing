import pandas as pd

from functools import partial

def get_subject_frame_( dictionary):
    df = None
    for key in dictionary.keys():
        try:
            values_ = [x[0] for x in dictionary[ key].values()]
        except TypeError:
            values_ = dictionary[ key].values()
        df_ = pd.DataFrame(
            values_, 
            index= dictionary[ key].keys(), columns= [ key]
        )
        if df is not None:
            df = df.merge( df_, how= 'outer', left_index= True, right_index= True)
        else:
            df = df_
    return df.sort_index().sort_index( axis= 1)

def make_frame_subjects( NEP, suffix, ground_truth= False):
    df = get_subject_frame_( NEP.subjects_answers)
    # nice indexing:
    model_ = NEP.model.strip('-turbo')
    mi = pd.MultiIndex.from_tuples(
        zip([ f'{model_}-{suffix}']*len(df.columns),df.columns),names=['model','subject']
    )
    df.columns = mi
    
    if ground_truth:
        dft = get_subject_frame_( NEP.subjects).fillna(0)
        # nice indexing:
        mi = pd.MultiIndex.from_tuples(
            zip(['true']*len(dft.columns),dft.columns), names=['model','subject']
        )
        dft.columns = mi
        return dft.merge( df, left_index= True, right_index= True)
    return df
    
def entailed(suffix, row):
    if (not row['a_is_num']) or (not row['b_is_num']):
        return ''
    else:
        if row['a'] > row['b']:
            return 'more'
        elif row['a'] == row['b']:
            return 'same'
        else:
            return 'less'

def get_a_b_rel_( df, col_name):
    df_ = pd.DataFrame()
    for ii, name in enumerate(['a','b','rel']):
        df_[ name] = df[ col_name].apply( lambda x: x[ ii])
    return df_

def make_frame_entailed( NEP, suffix, ground_truth= False):
    dfb = pd.DataFrame(
        NEP.probes_truth.items(), columns= ['probe','true']
    ).merge( pd.DataFrame(
        NEP.probes_answers.items(), columns= ['probe','ans']
    ), on= 'probe').set_index( 'probe').sort_index()
    
    df = get_a_b_rel_( dfb, 'ans')
    for which in ['a','b']:
        df[f'{which}_is_num'] = df.apply( lambda x: (type(x[ which])==int), axis=1)
    entailed_ = partial( entailed, suffix)
    df['rel_ent'] = df.apply( entailed_, axis= 1)
    # nice indexing:
    model_ = NEP.model.strip('-turbo')
    mi = pd.MultiIndex.from_tuples( 
        zip( [f'{model_}-{suffix}'] * len(df.columns), df.columns), names= ['model','answer']
    )
    df.columns = mi
    
    if ground_truth:
        dft = get_a_b_rel_( dfb, 'true')
        # nice indexing:
        mi = pd.MultiIndex.from_tuples( 
            zip( ['true']* len(dft.columns), dft.columns), names= ['model','answer']
        )
        dft.columns = mi
        return dft.merge( df, left_index= True, right_index= True)
    return df
 
def same_ans_for_models( df, model1, model2, which= ['a','b','rel']):
    cond = (df[ model1][ 'a'] == df[ model1][ 'a'])
    for answer in which:
        cond = cond & ( df[ model1][ answer] == df[ model2][ answer])
    return cond

def same_ent( df, model):
    return df[ model]['rel'] == df[model]['rel_ent']