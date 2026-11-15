# Introduction to RAG (Retrieval-Augmented Generation)

## What is RAG?

**RAG** stands for Retrieval-Augmented Generation.  
It is a way to help a large language model (LLM) answer questions.  

An **LLM** is a computer program that writes text by predicting the most likely next word.  
It learns this ability from a very large amount of training text.  

The LLM’s knowledge is frozen at training time.  
It cannot know newer events or private documents it never saw.  

Because the LLM only guesses the next word, it can give confident but wrong answers.  
This problem is called **hallucination**.  

RAG solves this by first retrieving relevant information from an external source.  
The retrieved information is then given to the LLM together with the question.  

## Why do we need it?

- The LLM cannot see up-to-date or private data on its own.  
- RAG lets the LLM use fresh or secret information without retraining the model.  
- By answering from supplied text, RAG can reduce hallucination.  
  The source text can be shown, so users can check the answer.  
- RAG does not change the LLM itself; it only changes what is fed to the model.  

Even with RAG, hallucination is not eliminated completely.  
If the wrong pieces of text are retrieved, the answer can still be wrong.  

## How does it work?

RAG has two main phases: preparation and answering.

### Preparation (done ahead of time)

1. **Chunking** – All documents are split into small pieces called *chunks*.  
2. **Embedding** – Each chunk is turned into an *embedding*.  
   An embedding is a list of numbers that represents the chunk’s meaning.  
   Texts with similar meaning get similar numbers.  
3. **Vector database** – All embeddings are stored in a *vector database*.  
   This database can quickly find the most similar items.

### Answering (run for each user question)

1. **Question embedding** – The user’s question is converted into an embedding using the same method as the chunks.  
2. **Retrieval** – The vector database finds the chunks whose embeddings are most similar to the question embedding. This step is called *retrieval*.  
3. **Prompt construction** – The retrieved chunks are *added to the prompt* together with the question. Adding extra information to the prompt is called *augmentation*.  
4. **Generation** – The LLM reads the prompt and writes the answer. This step is called *generation*.  

The LLM’s **context window** means the limit on how much text the model can read at once.  
Because of this limit, only a few relevant chunks are added instead of all documents.

Retrieval quality limits answer quality.  
If the wrong chunks are retrieved, the LLM may produce a wrong answer.  

RAG is different from **fine-tuning**.  
Fine-tuning means training the model again on new data.  
RAG supplies information at question time, and it is usually easier to update because you only change the documents.

Typical uses of RAG include:
- Help-bots that answer from policy documents  
- Searching course notes  
- Customer support  
- Question answering over internal documents  

## A Simple Example

*Imaginary scenario at BrightFuture College.*

**Student:** Ananya Patel, a second-year computer science student.  

**Question:** “What is the deadline to submit the final project for the Data Mining course?”

**Documents stored in the system:**

- **Chunk 1:** “Data Mining – Project guidelines. The final project must be submitted by 15 March 2025.”  
- **Chunk 2:** “Data Mining – Grading rubric. Projects are evaluated on originality and analysis.”  
- **Chunk 3:** “Data Mining – Lecture 5 notes. Covers clustering algorithms.”  

**Step 1 – Retrieval:**  
Ananya’s question is turned into an embedding.  
The vector database finds Chunk 1 as the most similar piece of text.  

**Step 2 – Prompt construction:**  
The system creates a prompt that contains:

```
Question: What is the deadline to submit the final project for the Data Mining course?
Relevant text: Data Mining – Project guidelines. The final project must be submitted by 15 March 2025.
```

**Step 3 – Generation:**  
The LLM reads the prompt and writes the answer.

**Final answer (uses ONLY facts from the retrieved chunk):**  
“The deadline to submit the final project for the Data Mining course is 15 March 2025.”

No extra information is added because the answer is taken directly from the retrieved chunk.

## Recap

- **LLM** predicts the next word using patterns from massive training data.  
- An LLM’s knowledge is frozen; it cannot see new or private information.  
- **RAG** first retrieves relevant text, then adds that text to the prompt with the question.  
- Retrieval uses **embeddings** stored in a **vector database**; similar meanings have similar numbers.  
- The **context window** limits how much text the LLM can read at once, so only a few chunks are added.  
- **Fine-tuning** means training the model again on new data, while RAG updates only the document store.  
- RAG can lower hallucination and give up-to-date answers, but quality still depends on good retrieval.
