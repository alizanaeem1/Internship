from langchain_core.prompts import ChatPromptTemplate


def is_related(previous_question, current_question, llm):

    prompt = ChatPromptTemplate.from_template("""
You are an AI assistant.

Determine whether the current question depends on the previous question.

Rules:

- Reply YES if the current question is a follow-up.
- Reply YES if it contains omitted references such as:
  it, its, this, that, these, those,
  they, them,
  who, where, when, why, how,
  requirements, benefits, purpose,
  responsibilities, process, procedure,
  risks, controls, examples, applications.

- Reply NO if the user starts a completely new topic.

Examples

Previous:
What is DOT?

Current:
Who enforces it?

YES

------------------------

Previous:
What is DOT?

Current:
Requirements

YES

------------------------

Previous:
Explain HIRA.

Current:
Who performs it?

YES

------------------------

Previous:
What is ISO 9001?

Current:
Benefits

YES

------------------------

Previous:
What is DOT?

Current:
Explain Machine Learning.

NO

------------------------

Previous:
{previous_question}

Current:
{current_question}

Reply ONLY with YES or NO.
""")

    chain = prompt | llm

    response = chain.invoke(
        {
            "previous_question": previous_question,
            "current_question": current_question,
        }
    )

    return response.content.strip().upper() == "YES"


from langchain_core.prompts import ChatPromptTemplate


def extract_topic(question, llm):

    prompt = ChatPromptTemplate.from_template("""
You are an AI assistant.

Your task is to extract ONLY the main topic or entity from the user's question.

Rules:

- Return only the main topic/entity.
- Do not explain.
- Do not answer the question.
- Do not include labels such as "Topic:" or "Entity:".
- Do not include quotes or punctuation.
- Do not add extra words.
- Preserve the original capitalization and wording.
- Never translate, abbreviate, or expand the topic.
- If the input already consists only of the topic/entity, return it unchanged.
- If multiple entities exist, return the primary entity.
- If no clear entity exists, return the original question.

Examples

Question:
DOT

Output:
DOT

Question:
ISO 9001

Output:
ISO 9001

Question:
HIRA

Output:
HIRA

Question:
Machine Learning

Output:
Machine Learning

Question:
What is DOT?

Output:
DOT

Question:
What are the requirements of DOT?

Output:
DOT

Question:
Who enforces DOT?

Output:
DOT

Question:
Explain HIRA.

Output:
HIRA

Question:
Who performs HIRA?

Output:
HIRA

Question:
Tell me about ISO 9001.

Output:
ISO 9001

Question:
What are the benefits of ISO 9001?

Output:
ISO 9001

Question:
Describe Lockout Tagout.

Output:
Lockout Tagout

Question:
Why is Lockout Tagout important?

Output:
Lockout Tagout

Question:
What is Machine Learning?

Output:
Machine Learning

Question:
Advantages of Machine Learning

Output:
Machine Learning

Question:
{question}

Output:
""")

    chain = prompt | llm

    response = chain.invoke(
        {
            "question": question,
        }
    )

    return response.content.strip()


def rewrite_question(previous_context, current_question, llm):

    prompt = ChatPromptTemplate.from_template("""
You are an intelligent query rewriting assistant for a Retrieval-Augmented Generation (RAG) system.

Your task is to rewrite the current question into a complete standalone question for semantic document retrieval.

You are given:

- Previous Topic
- Current Question

The previous topic is the main entity currently being discussed.

Rules:

1. Use the Previous Topic whenever the Current Question is incomplete.

2. Resolve references such as:
- it
- its
- they
- them
- this
- that
- who
- where
- when
- why
- how
- requirements
- benefits
- purpose
- responsibilities
- risks
- controls
- examples
- applications
- process
- procedure
- scope
- steps

3. If the Current Question consists of only one or two words (for example: "Benefits", "Requirements", "Purpose", "Responsibilities", "Examples", "Steps", "Risks", "Controls", "Scope"), rewrite it as a complete natural question using the Previous Topic.

4. Never remove the Previous Topic.

5. Never invent a different topic.

6. Never answer the question.

7. Return ONLY the rewritten question.

8. If the Current Question consists of only one or two words such as:

- Benefits
- Requirements
- Purpose
- Responsibilities
- Scope
- Risks
- Controls
- Examples
- Steps
- Process
- Procedure
- Advantages
- Disadvantages
- Causes
- Effects

convert it into a complete natural question using the Previous Topic.

9. If the Current Question is incomplete or contains omitted references such as:

- it
- its
- this
- that
- these
- those
- they
- them
- who
- where
- when
- why
- how

rewrite it by explicitly including the Previous Topic.

10. If the Current Question is already complete and independent, return it unchanged.

Examples

Previous Topic:
DOT

Current Question:
Benefits

Output:
What are the benefits of DOT?

--------------------------------

Previous Topic:
DOT

Current Question:
Examples

Output:
What are examples of DOT?

--------------------------------

Previous Topic:
ISO 9001

Current Question:
Scope

Output:
What is the scope of ISO 9001?

--------------------------------

Previous Topic:
HIRA

Current Question:
Steps

Output:
What are the steps of HIRA?

--------------------------------

Previous Topic:
Lockout Tagout

Current Question:
Risks

Output:
What are the risks of Lockout Tagout?

--------------------------------

Previous Topic:
DOT

Current Question:
Who enforces it?

Output:
Who enforces DOT?

--------------------------------

Previous Topic:
DOT

Current Question:
Who is affected?

Output:
Who is affected by DOT?

--------------------------------

Previous Topic:
DOT

Current Question:
What are the responsibilities?

Output:
What are the responsibilities of DOT?

--------------------------------

Previous Topic:
DOT

Current Question:
Why?

Output:
Why is DOT important?

--------------------------------

Previous Topic:
DOT

Current Question:
How?

Output:
How does DOT work?

--------------------------------

Previous Topic:
Hazard Identification

Current Question:
Who performs it?

Output:
Who performs Hazard Identification?

--------------------------------

Previous Topic:
Machine Learning

Current Question:
Advantages

Output:
What are the advantages of Machine Learning?

--------------------------------

Previous Topic:
{previous_context}

Current Question:
{current_question}

Think step by step.

First identify the Previous Topic.

Then determine whether the Current Question is complete or incomplete.

If it is incomplete, rewrite it by explicitly including the Previous Topic.

If it is already complete, return it unchanged.

Return ONLY the rewritten question.

Rewritten Question:

""")

    chain = prompt | llm

    response = chain.invoke(
        {
            "previous_context": previous_context,
            "current_question": current_question,
        }
    )

    return response.content.strip()