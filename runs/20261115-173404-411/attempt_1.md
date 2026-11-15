# Introduction to RAG (Retrieval-Augmented Generation)

## What is RAG?

**Retrieval-Augmented Generation (RAG)** is a method that helps a large language model (LLM) answer questions more accurately.  
An **LLM** is a computer program that writes text by predicting the most likely next word, using patterns it learned from a very large amount of training text. The LLM’s knowledge is frozen at training time. It does not know about newer events or about private documents it never saw. Because it only guesses the next word, the LLM can give confident but wrong answers. This problem is called hallucination.

RAG solves this by adding a step before the LLM writes. The system first **retrieves** (finds) relevant information from an external knowledge source, such as a set of policy documents or a collection of lecture notes. The retrieved text is then **added to the prompt** (the input given to the LLM) together with the user’s question. The LLM reads both the question and the retrieved text and then **generates** (writes) an answer.

## Why do we need it?

- The LLM cannot learn new facts after training. RAG lets the LLM use up-to-date or private information without retraining the model.  
- By answering from supplied text, RAG can reduce hallucination. The source text can be shown, so users can check the answer. Hallucination is not removed completely, but it becomes less common.  
- Updating a knowledge base is easier than fine-tuning the whole model. Fine-tuning changes the model by training it more, while RAG only changes the documents that are stored for retrieval.  
- Many real-world tools need accurate, current answers: help-bots that use company policies, search over course notes, customer support systems, and question answering over internal documents.  

## How does it work?

RAG works in two main phases: **preparation** and **answering**.

### Preparation (done ahead of time)

1. **Chunking** – Documents are split into small pieces called *chunks*.  
2. **Embedding** – Each chunk is converted into an *embedding*, a list of numbers that represents its meaning. Texts with similar meaning get similar numbers.  
3. **Vector database** – Embeddings are stored in a *vector database*, which can quickly find the most similar items.

### Answering (run for each user question)

1. **Query embedding** – The user’s question is turned into an embedding using the same method as the chunks.  
2. **Retrieval** – The system searches the vector database for the most similar chunks. This step is called retrieval.  
3. **Prompt construction** – The retrieved chunks are added to the prompt together with the question. This is called augmentation, but we simply say “added to the prompt”.  
4. **Generation** – The LLM reads the prompt and writes the answer.  

RAG does not change the model itself. It only changes the input given to the model. The quality of the retrieved chunks limits answer quality: if the wrong chunks are retrieved, the answer can be wrong.

The **context window** is the limit on how much text an LLM can read at one time. Because of this limit, only a few relevant chunks are retrieved instead of all documents.

### Analogy

Think of RAG like an open-book exam. The student = the LLM. The book = the documents stored in the vector database. Finding the right page = retrieval. Writing the answer = generation. The student is not retrained; they only read the page that the teacher points to before answering.

## A Simple Example

*Imaginary scenario at BrightFuture College.*

**Student:** Ananya, a second-year computer science student.  
**Question:** “What is the deadline for submitting the semester project?”  

**Documents stored:**  

- **Chunk 1:** “The semester project deadline for all departments is 15 March 2025.”  
- **Chunk 2:** “Mid-term exams will be held on 10 February 2025.”  
- **Chunk 3:** “Library hours are 8 am to 8 pm on weekdays.”  

**Step 1 – Retrieval:**  
Ananya’s question is turned into an embedding. The system searches the vector database and finds Chunk 1 as the most similar piece of text.  

**Step 2 – Prompt construction:**  
The prompt now contains:  

```
Question: What is the deadline for submitting the semester project?
Relevant text: The semester project deadline for all departments is 15 March 2025.
```

**Step 3 – Generation:**  
The LLM reads the prompt and writes:  

**Answer:** “The deadline for submitting the semester project is 15 March 2025.”

The answer uses only the fact from Chunk 1. No extra information is added.

## Recap

- **RAG** adds a retrieval step before an LLM generates an answer.  
- Retrieval uses **chunks**, **embeddings**, and a **vector database** to find relevant text.  
- The retrieved text is **added to the prompt** so the LLM can read it together with the question.  
- RAG lets the LLM use up-to-date or private information without retraining.  
- Retrieval quality limits answer quality; wrong chunks can cause wrong answers.  
- The open-book exam analogy shows how the LLM (student) relies on external text (book) to answer.
