# Introduction to **RAG** ( Retrieval-Augmented Generation )

## What is **RAG** ?

**RAG** stands for Retrieval-Augmented Generation.  
It is a method that helps a large language model (**LLM**) give better answers.  

An **LLM** is a computer program that writes text by predicting the most likely next word.  
It learns this ability from a huge amount of training text.  

The **LLM**’s knowledge is frozen at training time.  
It does not know about newer events or about private documents it never saw.  

Because the **LLM** only guesses the next word, it can give confident but wrong answers.  
This problem is called **hallucination**.  

**RAG** adds a step before the **LLM** answers.  
First, the system searches an external knowledge source for relevant information.  
Then it gives that information to the **LLM** together with the user’s question.

## Why do we need it ?

The **LLM** alone cannot know about recent events or secret files.  
**RAG** lets the **LLM** use up-to-date or private information without retraining the model.  

Retraining an **LLM** is expensive and takes a long time.  
**RAG** only changes the input that the **LLM** receives, not the model itself.  

When the **LLM** works with retrieved text, hallucination is reduced.  
The answer can be checked against the source text that was shown.  
However, hallucination is not eliminated completely.  

If the retrieval step finds the wrong pieces of text, the final answer may still be wrong.  
Therefore, the quality of retrieval directly limits answer quality.  

Typical uses of **RAG** include:  

- Help-bots that answer from company policy documents.  
- Searching course notes for students.  
- Customer support that uses internal manuals.  
- Question answering over private research papers.  

## How does it work ?

**RAG** has two main phases: preparation and answering.  

### Preparation (done ahead of time)

All documents are split into small pieces called **chunks**.  
Each **chunk** is turned into an **embedding**, a list of numbers that represents its meaning.  
Texts with similar meaning get similar numbers.  

All embeddings are stored in a **vector database**, a storage system that can quickly find items whose numbers are similar, meaning their meanings are similar.  

### Answering (done when a user asks a question)

The user’s question is also turned into an **embedding** with the same method.  
The **vector database** searches for the most similar **chunks**. This search is called **retrieval**.  

The retrieved **chunks** are **added to the prompt** – the text that is given to the **LLM** as input – together with the question.  
Finally, the **LLM** writes the answer. This part is called **generation**.  

The **context window** is the limit on how much text an **LLM** can read at one time.  
Because of this limit, only a few relevant **chunks** are added to the prompt instead of all documents.  

Think of **RAG** like an open-book exam.  
The student is the **LLM**.  
The book is the collection of documents.  
Finding the right page is **retrieval**.  
Writing the answer is **generation**.  
The student is not retrained; they only use the book during the exam.

## A Simple Example

Imagine **BrightFuture College** has a digital handbook called *StudentGuide*.  
A student named **Anita** asks the system:

**Question:** “What is the deadline to submit the final project for the Data Science course?”

**Preparation (already done):**  

- The handbook is split into **chunks**, each about 150 words.  
- Each **chunk** gets an **embedding** and is stored in the **vector database**.  

**Answering:**  

1. The question is turned into an **embedding**.  
2. The **vector database** retrieves the two most similar **chunks**:  

   **Chunk 1:** “Data Science – Project Guidelines. The final project must be submitted by 15 September. Late submissions will get a penalty.”  

   **Chunk 2:** “Course Calendar. Mid-term exam on 30 August. Final project deadline on 15 September.”  

3. The two **chunks** are **added to the prompt** together with Anita’s question.  

4. The **LLM** reads the prompt and **generates**:  

   **Answer:** “The deadline to submit the final project for the Data Science course is 15 September.”  

The answer uses only facts that appear in the retrieved **chunks**.  
No extra information is added.  

If the retrieval step had returned a wrong **chunk**, the answer could have been incorrect.  
That shows why good retrieval is essential.

## Recap

- **RAG** adds a retrieval step before an **LLM** generates an answer.  
- Retrieval finds relevant text from external sources and **adds it to the prompt**.  
- The **LLM**’s knowledge stays frozen; it only uses the retrieved text at answer time.  
- **RAG** lets the system use up-to-date or private information without costly retraining.  
- Hallucination is reduced because answers can be checked against the retrieved sources.  
- The quality of retrieved **chunks** directly affects the correctness of the final answer.
