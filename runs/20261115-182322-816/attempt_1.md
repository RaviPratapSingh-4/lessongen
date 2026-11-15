# Introduction to **Retrieval-Augmented Generation**  

## What is Retrieval-Augmented Generation?  
Retrieval-Augmented Generation, abbreviated **RAG**, is a method that adds external information to a large language model before it answers a question. An **LLM** (large language model) is a computer program that writes text by predicting the most likely next word, using patterns it learned from a very large amount of training text. The LLM’s knowledge is frozen at training time. It does not know about newer events or about private documents it never saw. Because it cannot see new data, the LLM can give confident but wrong answers. This problem is called **hallucination**.  

RAG solves this by retrieving relevant information from an external knowledge source and giving that information to the LLM together with the user’s question. The LLM then generates an answer based on both the question and the retrieved text.  

## Why do we need it?  
The LLM alone cannot answer questions about recent news, company policies, or personal files that were not part of its training data. Updating the LLM by retraining it is costly and slow. RAG lets an LLM use up-to-date or private information without retraining the model. By providing the LLM with actual source text, RAG can reduce hallucination because the answer can be checked against the supplied documents. It does not remove hallucination completely, but it makes errors easier to spot.  

RAG also keeps the model unchanged. It only changes the input given to the model. This means we can add, delete, or modify documents without touching the LLM itself. Retrieval quality limits answer quality: if the wrong chunks are retrieved, the answer can be wrong.  

Typical uses include help-bots that answer from policy documents, searching course notes, customer support, and question answering over internal documents.  

## How does it work?  
RAG has two main phases: preparation and answering.  

RAG works by retraining the model's weights every time a user asks a question.

**Preparation step** (done ahead of time): Documents are split into small pieces called **chunks**. Each chunk is converted into an **embedding**, a list of numbers that represents its meaning. Texts with similar meaning get similar numbers. These embeddings are stored in a **vector database**, which can quickly find the most similar items.  

**Answering step**: The user’s question is converted into an embedding with the same method, and the most similar chunks are found. This is called **retrieval**. The retrieved chunks are placed in the prompt together with the question (this is called **augmentation**). The LLM then writes the answer (this is called **generation**).  

The context window is the limit on how much text an LLM can read at one time. This is why only a few relevant chunks are retrieved instead of all documents.  

Think of RAG like an open-book exam. The student = the LLM, the book = the documents, finding the right page = retrieval, writing the answer = generation. The student is not retrained; they simply read the right page before answering.  

## A Simple Example  
Imagine **College of Bright Futures**. A student named **Anita** asks a help-bot:  

**Question:** “What is the deadline for submitting the final project in the Data Science course?”  

The system has three stored chunks:  

1. *Chunk A:* “Data Science course – project proposal due 10 March.”  
2. *Chunk B:* “Data Science course – final project submission deadline 30 April.”  
3. *Chunk C:* “Data Science course – mid-term exam on 15 April.”  

When Anita’s question is turned into an embedding, the vector database finds Chunk B as the most similar. Chunk B is **added to the prompt** together with the question. The prompt now contains:  

- Question: “What is the deadline for submitting the final project in the Data Science course?”  
- Retrieved text: “Data Science course – final project submission deadline 30 April.”  

The LLM reads this prompt and generates the answer:  

**Answer:** “The final project must be submitted by 30 April.”  

The answer uses only the fact from the retrieved chunk. No extra information is added.  

## Recap  
- **RAG** adds external text to an LLM before it answers.  
- It lets the model use up-to-date or private data without retraining.  
- Retrieval finds the most similar document chunks using embeddings stored in a vector database.  
- The retrieved chunks are **added to the prompt** with the question, then the LLM generates the answer.  
- RAG can lower hallucination, but answer quality still depends on retrieval quality.  

---
