# ChatDocs 📄

ChatDocs is an AI-powered tool designed to help you interact naturally with your documents and data. Upload PDFs, text files, spreadsheets, or other data sources, and ChatDocs will enable you to ask questions, extract insights, and get quick, accurate answers. This project simplifies access to information, making your data more actionable and accessible.

## Features ✨

- **Works with All Kinds of Files**: Toss in whatever you’ve got—PDFs, text files, Word docs. If it’s a file, ChatDocs can probably handle it.
- **Chats Like a Buddy**: Have a real conversation with your docs and data. Ask questions, get answers—it’s like talking to a super-smart friend who’s read everything. 🗣️
- **Fast Insights, No Sweat**: Need a quick summary or the juicy bits from your content? ChatDocs pulls it out in seconds, no digging required.
- **Easy for Everyone**: Whether you’re a tech newbie or a pro, the interface is simple and friendly.

## Installation 🚀

Follow these steps to get ChatDocs up and running:

1. **Clone the Repository**:
   ```bash
   git clone https://github.com/sefatuter/ChatDocs.git
   cd ChatDocs
   ```
   
2. **Run the Application:**
   To start the application:

   ```bash
   docker compose up -d
   ```

   Or you can pull images and compose without build:

    - ```bash
      docker pull usersefa/chatdocs-postgres
      docker pull usersefa/chatdocs-flask-app
      docker pull usersefa/chatdocs-ollama
      ```
    - ```bash
      docker-compose up -d
      ```
 3. **Go to page:**
    Open your browser and head to ```http://localhost:5000``` to start chatting.



## Usage

1. Launch ChatDocs by running the installation steps above.
2. Upload your documents or website url.
3. Ask questions in the chat interface, such as "What’s in this file?" or "Summarize this data."
4. ChatDocs will respond with natural, context-aware answers based on your uploaded content.

## Contribution

If you want to contribute to the project:
- Fork the repository.
- Create a branch for new features or fixes.
- Share your changes with a pull request.

Please feel free to open an “issue” with your ideas and feedback!

## License

This project is licensed with [MIT License](LICENSE). You can review the license file for details.

## Contact

For questions or support requests: [1sefatuter@gmail.com](mailto:1sefatuter@gmail.com)  

---
