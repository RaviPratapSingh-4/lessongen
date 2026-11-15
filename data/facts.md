F1 [MUST] An LLM (large language model) writes text by predicting the most likely next word, using patterns it learned from a very large amount of training text.
F2 [MUST] An LLM's knowledge is frozen at training time. It does not know about newer events or about private documents it never saw.
F3 [MUST] An LLM can give confident but wrong answers. This is called hallucination.
F4 [MUST] RAG stands for Retrieval-Augmented Generation. Before the LLM answers, the system retrieves relevant information from an external knowledge source and gives it to the LLM together with the question.
F5 [MUST] RAG lets an LLM use up-to-date or private information without retraining the model.
F6 [MUST] RAG can reduce hallucination because the LLM answers from supplied text, and the sources can be shown so answers can be checked. It does not remove hallucination completely.
F7 [MUST] Preparation step (done ahead of time): documents are split into small pieces called chunks.
F8 [MUST] Each chunk is converted into an embedding, a list of numbers that represents its meaning. Texts with similar meaning get similar numbers.
F9 Embeddings are stored in a vector database, which can quickly find the most similar items.
F10 [MUST] Answering step: the user's question is converted into an embedding with the same method, and the most similar chunks are found. This is called retrieval.
F11 [MUST] The retrieved chunks are placed in the prompt together with the question (augmentation), and the LLM writes the answer (generation).
F12 RAG does not change the model itself. It only changes the input given to the model.
F13 Retrieval quality limits answer quality: if the wrong chunks are retrieved, the answer can be wrong.
F14 Fine-tuning changes the model by training it more. RAG supplies information at question time, and is usually easier to update because you only change the documents.
F15 Typical uses: a help-bot that answers from policy documents, searching course notes, customer support, question answering over internal documents.
F16 The context window is the limit on how much text an LLM can read at one time. This is why only a few relevant chunks are retrieved instead of all documents.
