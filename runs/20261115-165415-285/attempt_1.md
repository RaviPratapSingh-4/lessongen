# Introduction to RAG (Retrieval‑Augmented Generation)

## What is RAG?

RAG stands for **Retrieval‑Augmented Generation**.  
It is a way to help a large language model (LLM) answer questions more accurately.  

An **LLM** is a computer program that writes text by predicting the most likely next word. It learns this ability from a huge amount of training text. The LLM’s knowledge is **frozen at training time** – it cannot learn new events or see private documents that were not in its training data. Because of this, an LLM can sometimes give confident but wrong answers. This problem is called **hallucination**.

RAG solves part of this problem by **retrieving** relevant information from an external source before the LLM generates an answer. The retrieved text is **augmented** to the LLM’s prompt, so the model can use up‑to‑date or private information without being retrained.

## Why do we need it?

1. **Fresh information** – The LLM cannot know events after its training. RAG lets it use the latest news, recent research, or company policies that are stored outside the model.  
2. **Private data** – Companies may have confidential manuals that the LLM never saw. RAG can feed those documents at query time.  
3. **Reduced hallucination** – When the LLM answers from the supplied text, the answer can be checked against the source. This lowers, but does not completely remove, hallucination.  
4. **Easy updates** – Adding or changing documents is simpler than fine‑tuning the whole model. Fine‑tuning changes the model itself by additional training, while RAG only changes the external documents.  
5. **Practical uses** – Help‑bots that answer from policy manuals, student portals that search lecture notes, customer‑support agents that read product guides, and internal Q&A systems for companies.

## How does it work?

RAG has two main phases: **Preparation** and **Answering**.

### 1. Preparation (done ahead of time)

- **Chunking** – Large documents are split into small pieces called **chunks**.  
- **Embedding** – Each chunk is turned into an **embedding**, a list of numbers that captures its meaning. Texts with similar meaning receive similar numbers.  
- **Vector database** – All embeddings are stored in a **vector database**. This special database can quickly find items whose numbers are most similar.

### 2. Answering (run for each user question)

1. **Query embedding** – The user’s question is converted into an embedding using the same method as the chunks.  
2. **Retrieval** – The vector database searches for the most similar chunk embeddings. The found chunks are the **retrieved** information.  
3. **Augmentation** – The retrieved chunks are placed together with the original question to form a new prompt.  
4. **Generation** – The LLM receives this augmented prompt and writes the answer.  

RAG does **not** change the LLM itself; it only changes the input given to the model. The quality of the answer depends heavily on the **retrieval quality**. If the wrong chunks are retrieved, the answer may still be wrong.

The LLM can only read a limited amount of text at once. This limit is called the **context window**. Because of the context window, RAG retrieves only a few highly relevant chunks instead of feeding the entire document collection.

## A Simple Example

### Analogy: Open‑book exam

Imagine a student taking an open‑book exam. Instead of memorising every fact, the student can look up the textbook during the test. The textbook is the external knowledge source, and the act of looking up the right page is the retrieval step. The student then writes the answer using the found text. This is exactly what RAG does for an LLM.

### Worked example in an Indian college

**Student:** *Riya* is studying Computer Science at Delhi University. She wants to know:

> *“What are the steps to submit a project on the university’s online portal?”*

**Documents:** The university’s IT department has uploaded a PDF guide titled *“Online Project Submission – 2024”*. The guide contains several sections, including a step‑by‑step list.

**RAG process**

1. **Chunking** – The PDF is split into small chunks, each covering one or two steps.  
2. **Embedding** – Each chunk is turned into a numeric embedding and stored in a vector database.  
3. **Query embedding** – Riya’s question is transformed into an embedding.  
4. **Retrieval** – The database finds the three chunks most similar to the query:  
   - Chunk 1: “Log in to the portal using your university credentials.”  
   - Chunk 2: “Navigate to ‘Projects’ → ‘Submit New Project’.”  
   - Chunk 3: “Upload the PDF, confirm details, and click ‘Submit’.”  
5. **Augmentation** – The three chunks are placed together with Riya’s question as a single prompt.  
6. **Generation** – The LLM reads the prompt and writes:

> “First, log in to the university portal with your student ID and password. Next, go to the ‘Projects’ menu and select ‘Submit New Project’. Finally, upload your project PDF, verify the information, and click ‘Submit’.”

Because the answer comes from the retrieved chunks, Riya can also see the source text and verify it. If the guide is updated next year, only the PDF needs to be re‑chunked and re‑embedded; the LLM itself stays the same.

## Recap

- **RAG = Retrieval‑Augmented Generation** – adds external text to an LLM’s prompt.  
- **LLM** predicts next words; its knowledge is frozen and can hallucinate.  
- **Retrieval** finds relevant chunks from a vector database using embeddings.  
- **Augmentation** supplies those chunks to the LLM, allowing up‑to‑date or private answers.  
- **Benefits**: fresh data, private documents, lower hallucination, easy updates, many real‑world uses.  
- **Limits**: answer quality depends on retrieval quality; hallucination is reduced but not eliminated.
