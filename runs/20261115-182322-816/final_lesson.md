# Introduction to **Retrieval-Augmented Generation**

## What is Retrieval-Augmented Generation?  
**Retrieval-Augmented Generation** (RAG) is a method that gives a large language model extra information before it writes an answer. An **LLM** (large language model) is a computer program that writes text by predicting the most likely next word, using patterns it learned from a very large amount of training text. The LLM’s knowledge is frozen at training time. It does not know about newer events or about private documents it never saw. Because it cannot see new data, the LLM can give confident but wrong answers. This problem is called **hallucination**.  

RAG solves the problem by first retrieving relevant information from an external knowledge source and then giving that information to the LLM together with the user’s question. The LLM then generates an answer based on both the question and the retrieved text.

## Why do we need it?  
The LLM alone cannot answer questions about recent news, company policies, or personal files that were not part of its training data. Updating the LLM by retraining it is costly and slow. **RAG lets an LLM use up-to-date or private information without retraining the model**. By providing the LLM with actual source text, RAG can **reduce hallucination** because the answer can be checked against the supplied documents. It does not remove hallucination completely, but it makes errors easier to spot.  

RAG also keeps the model unchanged. It only changes the **input** given to the model. This means we can add, delete, or modify documents without touching the LLM itself. Retrieval quality limits answer quality: if the wrong chunks are retrieved, the answer can be wrong.  

Typical uses include help-bots that answer from policy documents, searching course notes, customer support, and question answering over internal documents.

## How does it work?  
RAG has two main phases: preparation and answering.

### Preparation (done ahead of time)  
1. **Chunking** – Documents are split into small pieces called **chunks**.  
2. **Embedding** – Each chunk is converted into an **embedding**, a list of numbers that represents its meaning. Texts with similar meaning get similar numbers.  
3. **Vector database** – Embeddings are stored in a **vector database**, which can quickly find the most similar items.

### Answering (done for each user question)  
1. **Question embedding** – The user’s question is converted into an embedding with the same method.  
2. **Retrieval** – The vector database finds the most similar chunks to the question embedding. This step is called **retrieval**.  
3. **Prompt creation** – The retrieved chunks are **added to the prompt**. A **prompt** is simply the text that is given to the LLM as input. The prompt now contains the original question plus the selected chunks.  
4. **Generation** – The LLM reads the prompt and writes the answer. This step is called **generation**.

The **context window** is the limit on how much text an LLM can read at one time. Because of this limit, only a few relevant chunks are added to the prompt instead of all documents.

Think of RAG like an open-book exam. The student = the LLM, the book = the documents, finding the right page = retrieval, writing the answer = generation. The student is not retrained; they simply read the right page before answering.

## A Simple Example  
Imagine **FutureTech College**. A student named **Ravi** asks a help-bot:

**Question:** “When does the semester-end exam start for the Mathematics 101 course?”

The system has three stored chunks:

1. *Chunk A:* “Mathematics 101 – lecture schedule runs from 1 January to 15 May.”  
2. *Chunk B:* “Mathematics 101 – semester-end exam starts on 20 May and ends on 22 May.”  
3. *Chunk C:* “Mathematics 101 – mid-term quiz held on 10 March.”

When Ravi’s question is turned into an embedding, the vector database finds **Chunk B** as the most similar. **Chunk B is added to the prompt** together with the question. The prompt now looks like:

- Question: “When does the semester-end exam start for the Mathematics 101 course?”  
- Retrieved text: “Mathematics 101 – semester-end exam starts on 20 May and ends on 22 May.”

The LLM reads this prompt and generates the answer:

**Answer:** “The semester-end exam for Mathematics 101 starts on 20 May.”

The answer uses only the fact from the retrieved chunk. No extra details are added.

### More detail on each step  
- **Chunk size** matters. If chunks are too large, they may exceed the context window; if too small, they may miss important context.  
- **Embedding quality** matters because similar meaning must produce similar numbers. Good embeddings help the vector database return the most relevant chunks.  
- **Number of retrieved chunks** is a design choice. Retrieving more chunks can give the LLM more information but also risks exceeding the context window or adding irrelevant text.  
- **Source citation** is possible because the system knows which chunk each piece of text came from. Showing the source helps users verify the answer and reduces the impact of hallucination.  

## Recap  
- **RAG** adds external text to an LLM before it answers.  
- It lets the model use up-to-date or private data without retraining.  
- Preparation splits documents into **chunks**, creates **embeddings**, and stores them in a **vector database**.  
- Answering converts the question to an embedding, **retrieves** similar chunks, **adds them to the prompt**, and the LLM **generates** the answer.  
- RAG can lower hallucination, but answer quality still depends on how well the right chunks are retrieved.
