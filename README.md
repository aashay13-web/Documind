🧠 What is DocuMind?
Imagine a new employee who has a question like, "How do I get a refund for a broken item?" Usually, they’d have to find a 50 page PDF, search for the right section, and hope they understand it correctly.

DocuMind changes that. It’s an AI assistant that has "read" all the company's private documents. You can ask it a question in plain English, and it will scan the documents, find the exact answer, and even tell you which page it found the info on.

🛠️ How it Works (The "Kitchen" Analogy)
If your project was a restaurant, here is how the parts work together:

The Ingredients (PDFs): These are your raw documents, like the refund_policy.pdf.

The Fridge (Pinecone): This is where we store the information. We don't just throw the files in; we "chop" them into small, searchable pieces so the AI can find them instantly.

The Chef (OpenAI/GPT-4o): This is the "brain." It looks at the pieces of information in the fridge and "cooks" a perfect answer for the user.

The Waiter (FastAPI): This is the interface you see on your screen. It takes your question to the chef and brings the answer back to you.

🛡️ Why is this better than ChatGPT?
If you ask a normal AI about a company's specific rules, it might guess or "hallucinate" (make things up). DocuMind is different because it is "Grounded." * It is forbidden from using outside knowledge.

If the answer isn't in your PDF, it will honestly say, "I don't know," instead of lying.

A .env.example file is a template that shows anyone using our project exactly what "secret keys" they need to provide to make the code work. Since we shouldn't share our actual private keys on GitHub, this file acts as a placeholder or a "blank form".

How to Use the .env.example File
Locate the Template: Find the file named .env.example in the main folder of the project.

Create Your Personal Copy:

Right-click the file and select Copy.

Paste it into the same folder.

Rename the new file to exactly .env.

Fill in Your Secrets: Open the new .env file and replace the placeholder text (like your_key_here) with your actual private API keys from OpenAI and Pinecone.
