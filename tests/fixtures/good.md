# Introduction to RAG

## What is RAG?

RAG stands for Retrieval-Augmented Generation. It is a method that helps an AI give answers that are correct and up to date.

To understand RAG, we first need to know about an LLM. LLM is short for large language model. An LLM is a computer program that writes text. It learned this skill by reading a very large amount of text. It writes by guessing the most likely next word, again and again, until a full answer is ready.

An LLM is very useful, but it has two problems.

First, its knowledge is frozen. It only knows what it saw during training. It does not know about new events. It also cannot see your private documents, such as the rules of your college.

Second, it can make mistakes while sounding very sure. This is called a hallucination. For example, it may tell you a fee date that does not exist.

RAG helps with both problems. The idea is simple. Before the LLM answers, the system first finds the right information from a trusted source. Then it gives that information to the LLM along with your question. The LLM writes its answer using that information.

Think of an open-book exam. A student without a book must answer from memory and may forget something. A student with a book finds the right page first and then writes the answer. RAG turns the LLM into the second student. The book is your own set of documents.

## Why do we need RAG?

RAG matters for four reasons.

- Fresh information. You can add new documents at any time, so the answers stay up to date.
- Private information. The LLM can answer from your own files, which it never saw during training.
- Fewer mistakes. The LLM answers using the text it is given, so it is less likely to make things up. RAG can also show the source, so you can check the answer yourself. But RAG does not remove mistakes completely.
- Less work. You do not need to train the model again. You only change the documents.

There is another way to teach a model new things. It is called fine-tuning. Fine-tuning means training the model again on new data. This changes the model itself, and updating it usually takes more work. With RAG, the model stays the same. Only the documents change.

Many companies use RAG. A help-bot that answers questions from policy documents is a common use. Other uses are searching course notes and answering customer support questions.

## How does RAG work?

RAG has two parts. The first part is done ahead of time. The second part happens every time someone asks a question.

### Part 1: Prepare the documents

1. Split. The documents are split into small pieces. Each small piece is called a chunk.
2. Convert. Each chunk is changed into an embedding. An embedding is a list of numbers that shows the meaning of the text. Texts with similar meaning get similar numbers.
3. Store. The embeddings are saved in a vector database. A vector database is a special storage that can quickly find items with similar meaning.

### Part 2: Answer a question

4. Convert the question. The question is also changed into an embedding. The same method is used as before, so the numbers can be compared.
5. Retrieve. The system looks in the vector database. It finds the chunks whose numbers are most similar to the question. This step is called retrieval.
6. Combine. The chunks are put into a prompt together with the question. A prompt is the text that we give to an LLM.
7. Generate. The LLM reads the prompt and writes the answer. This step is called generation.

You may ask why we do not give all the documents to the LLM. The reason is simple. An LLM can read only a limited amount of text at one time. This limit is called the context window. So we send only the few most useful chunks.

Remember one important point. RAG does not change the model. It only changes what we give to the model as input.

Also remember that RAG is only as good as its search. If the system finds the wrong chunks, the answer can be wrong too.

## A Simple Example

Imagine a college that builds a help-bot for its students. A student named Priya asks, "What is the last date to pay the hostel fee?"

Without RAG, the LLM has never seen the notices of this college. It may guess a date. That guess would be a hallucination.

Now see what happens with RAG.

1. Before the bot starts, the college adds its notices to the system. They are split into chunks, changed into embeddings and saved in the vector database.
2. Priya types her question. The question is changed into an embedding.
3. The system retrieves the chunk that matches best. In our imaginary example, the chunk says, "The hostel fee must be paid before 10 December."
4. The chunk and Priya's question are put into the prompt.
5. The LLM reads the prompt and answers, "The last date to pay the hostel fee is 10 December."

The answer is correct because it comes from the real notice. The bot can also show the notice, so Priya can check it herself.

## Recap

- RAG stands for Retrieval-Augmented Generation.
- An LLM has frozen knowledge and can make confident mistakes called hallucinations.
- RAG first finds the right information and then gives it to the LLM with the question.
- Preparation: split the documents into chunks, make embeddings and store them in a vector database.
- Answering: make an embedding of the question, retrieve similar chunks, add them to the prompt and let the LLM generate the answer.
- RAG does not change the model. It can reduce mistakes but cannot remove them, and its answers are only as good as its search.
