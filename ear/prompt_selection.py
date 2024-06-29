fact_dict = {
    'mask':{
        'v0' : {
            'fact_1' : 'A {thing} usually has <mask> {elements}.',
            'fact_2' : 'A typical {thing_a} has a number of {elements_a} that is <mask> than the number of {elements_b} that a typical {thing_b} has.'
        },
        'v1' : {
            'fact_1' : 'A typical {thing} usually has <mask> {elements}.',
            'fact_2' : 'A typical {thing_a} has a number of {elements_a} that is <mask> to/than the number of {elements_b} a {thing_b} has.'
        },
    },
    'qa': {
        'v0' : {
            'fact_1' : 'A typical {thing} has how many {elements}?',
            'fact_2' : 'A typical {thing_a} has more, equal or fewer number of {elements_a} than the number of {elements_b} that a {thing_b} has?'
        },
        'v1' : {
            'fact_1' : 'How many {elements} does a typical {thing} have?',
            'fact_2' : 'Is the number of {elements_a} a typical {thing_a} has more, equal to or fewer than the number {elements_b} that a {thing_b} has?'
        }
    }
}


PROMPT_NUMBER_MASK = """In the following sentence, replace the <mask> token with a suitable number.
{sentence}
"""
PROMPT_NUMBER_MASK_0 = """User: Replace the <mask> token in the following sentence with an appropriate number. {sentence}
Assistant:
"""
PROMPT_NUMBER_MASK_1 = """User: Replace the <mask> token in the following sentence with an appropriate number. A typical human usually has <mask> knees.
Assistant: A typical human usually has 2 knees.

User: Replace the <mask> token in the following sentence with an appropriate number. {sentence}
Assistant:
"""
PROMPT_NUMBER_MASK_2 = """User: Replace the <mask> token in the following sentence with an appropriate number. A typical human usually has <mask> knees.
Assistant: A typical human usually has 2 knees.

User: Replace the <mask> token in the following sentence with an appropriate number. A typical building usually has <mask> roof.
Assistant: A typical building usually has one roof.

User: Replace the <mask> token in the following sentence with an appropriate number. {sentence}
Assistant:
"""
PROMPT_NUMBER_MASK_2_1 = """User: Replace the <mask> token in the following sentence with an appropriate number. A human usually has <mask> knees.
Assistant: A human usually has 2 knees.

User: Replace the <mask> token in the following sentence with an appropriate number. A typical building has at least <mask> door.
Assistant: A typical building has at least one door.

User: Replace the <mask> token in the following sentence with an appropriate number. {sentence}
Assistant:
"""

PROMPT_NUMBER_QA= """{sentence}"""
PROMPT_NUMBER_QA_0 = """You are a helpful assistant and you need to answer commonsense knowledge queries about numbers. 
Please answer the following question with a single token: {sentence}."""


PROMPT_RELATIONSHIP_MASK = """In the following sentence, replace the <mask> token with an appropriate quantifier adjective.
{sentence}
"""
PROMPT_RELATIONSHIP_MASK_0 = """User: Replace the <mask> token in the following sentence with an appropriate quantifier adjective. {sentence}
Assistant:
"""
PROMPT_RELATIONSHIP_MASK_1 = """User: Replace the <mask> token in the following sentence with an appropriate quantifier adjective. A typical human has a number of knees that is <mask> to/than the number of doorknobs a typical door has.
Assistant: A typical human has a number of knees that is larger to/than the number of doorknobs a typical door has.

User: Replace the <mask> token in the following sentence with an appropriate quantifier adjective. {sentence}
Assistant:
"""
PROMPT_RELATIONSHIP_MASK_2 = """User: Replace the <mask> token in the following sentence with an appropriate quantifier adjective. A typical human has a number of knees that is <mask> to/than the number of doorknobs a typical door has.
Assistant: A typical human has a number of knees that is larger to/than the number of doorknobs a typical door has.

User: Replace the <mask> token in the following sentence with an appropriate quantifier adjective. A typical cat has a number of tails that is <mask> to/than the number of roofs a typical building.
Assistant: A typical cat has a number of tails that is equal to/than the number of roofs a typical building.

User: Replace the <mask> token in the following sentence with an appropriate quantifier adjective. {sentence}
Assistant:
"""

PROMPT_RELATIONSHIP_QA = """{sentence}"""
PROMPT_RELATIONSHIP_QA_0 = """You are a helpful assistant and you need to answer commonsense knowledge queries about numerical comparisons.
Please answer the following question with a single token: {sentence}."""

prompt_dict = {
    'mask':{
        '0shot-v0' : {
            'prompt_1': PROMPT_NUMBER_MASK,
            'prompt_2': PROMPT_RELATIONSHIP_MASK
        },
        '0shot-v1' : {
            'prompt_1': PROMPT_NUMBER_MASK_0,
            'prompt_2' : PROMPT_RELATIONSHIP_MASK_0
        },
        '1shot-v1' : {
            'prompt_1': PROMPT_NUMBER_MASK_1,
            'prompt_2' : PROMPT_RELATIONSHIP_MASK_1
        },
        '2shot-v1' : {
            'prompt_1': PROMPT_NUMBER_MASK_2,
            'prompt_2' : PROMPT_RELATIONSHIP_MASK_2
        },
    },
    'qa':{
        '0shot-v0' : {
            'prompt_1' : PROMPT_NUMBER_QA,
            'prompt_2' : PROMPT_RELATIONSHIP_QA,
        },
        '0shot-v1' : {
            'prompt_1' : PROMPT_NUMBER_QA_0,
            'prompt_2' : PROMPT_RELATIONSHIP_QA_0,
        }
    }
}
