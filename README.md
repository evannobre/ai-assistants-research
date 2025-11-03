# ai-assistants-research

This repository contains the prompts and the codes for the study "Evaluating the Correctness and Performance of AI-Generated Benchmarks".

Within the folder _"Answers from the AI-assistants"_ - https://github.com/evannobre/ai-assistants-research/tree/main/Answers%20from%20the%20AI-assistants -, you will find OneNote notebooks containing the complete answer gave by an AI-assistant (ChatGPT, Claude, DeepSeek, Gemini or Microsoft Copilot).

### **They are tagged as follow:**

* **[Experimental] Benchmark-name** refers to P1 (Basic) and P2 (Specialized). Those are the straight prompt, implementing few restrictions from the dataset (The Computer Language Benchmarks Game). They are mostly one-shot prompt, sometimes specifying specific data or techniques required by the dataset.

* **[CLBG] Benchmark-name** refers to P3 (Basic) and P4 (Specialized). Those are the prompts implementing all restrictions from the dataset (The Computer Language Benchmarks Game). 

----------

In the folder _"Codes from the AI-assistants"_ - https://github.com/evannobre/ai-assistants-research/tree/main/Codes%20from%20the%20AI-assistants -, you will find multiple codes provided by the AI-assistants under research (ChatGPT, Claude, DeepSeek, Gemini or Microsoft Copilot).

### **The folders are organized as follow:**

* **[Experimental] Benchmark-name** refers to codes provided from the P1 (Basic) and P2 (Specialized) prompts. 

* **[CLBG] Benchmark-name** refers to codes provided from the P3 (Basic) and P4 (Specialized) prompts. 

  * **Each "[Experimental] Benchmark-name" or "[CLBG] Benchmark-name" folder contains four sub-folders:**

    * **Basic Prompt - Normal Mode** codes generated from P1 (Experimental)/P3 (CLBG) using the "common" search-mode.

    * **Basic Prompt - TBR Mode** codes generated from P1 (Experimental)/P3 (CLBG) using the "think before responding" search-mode.

    * **Specialized Prompt - Normal Mode** codes generated from P2 (Experimental)/P4 (CLBG) using the "common" search-mode.

    * **Specialized Prompt - TBR Mode** codes generated from P2 (Experimental)/P4 (CLBG) using the "think before responding" search-mode.
   
----------

The codes will also follow the name pattern: _BenchmarkName_LLM_PromptType_SearchMode.CodeExtension_.
