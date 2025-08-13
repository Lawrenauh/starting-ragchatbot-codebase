# Course Materials RAG System

A Retrieval-Augmented Generation (RAG) system designed to answer questions about course materials using semantic search and AI-powered responses.

## Overview

This application is a full-stack web application that enables users to query course materials and receive intelligent, context-aware responses. It uses ChromaDB for vector storage, Anthropic's Claude for AI generation, and provides a web interface for interaction.


## Prerequisites

- Python 3.13 or higher
- uv (Python package manager)
- An Anthropic API key (for Claude AI)
- **For Windows**: Use Git Bash to run the application commands - [Download Git for Windows](https://git-scm.com/downloads/win)

## Installation

1. **Install uv** (if not already installed)
   ```bash
   curl -LsSf https://astral.sh/uv/install.sh | sh
   ```

2. **Install Python dependencies**
   ```bash
   uv sync
   ```

3. **Set up environment variables**
   
   Create a `.env` file in the root directory:
   ```bash
   ANTHROPIC_API_KEY=your_anthropic_api_key_here
   ```

## Running the Application

### Quick Start

Use the provided shell script:
```bash
chmod +x run.sh
./run.sh
```

### Manual Start

```bash
cd backend
uv run uvicorn app:app --reload --port 8000
```

The application will be available at:
- Web Interface: `http://localhost:8000`
- API Documentation: `http://localhost:8000/docs`

## System Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    RAG CHATBOT SYSTEM FLOW                                  │
└─────────────────────────────────────────────────────────────────────────────┘

┌─────────────┐
│ USER INPUT  │
│ (Question)  │
└──────┬──────┘
       │
       ▼
┌─────────────┐    ┌────────────────────────────────────────┐
│  FRONTEND   │    │             BACKEND                    │
│ index.html  │◄──►│ app.py @app.post("/api/query")         │
│ script.js   │    │ 1. Receive query + session_id          │
│ style.css   │    │ 2. Create session if needed            │
└─────────────┘    │ 3. Call rag_system.query()             │
                   └─────────────────┬──────────────────────┘
                                     │
                                     ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                        RAG SYSTEM                                           │
│                      (rag_system.py)                                        │
│ query(query, session_id)                                                    │
│ 1. Create prompt with query                                                 │
│ 2. Get conversation history from session_manager                            │
│ 3. Call ai_generator.generate_response() with tools                         │
│ 4. Get sources from tool_manager                                            │
│ 5. Update conversation history in session_manager                           │
│ 6. Return response and sources                                              │
└────────────────────────────┬────────────────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                      AI GENERATOR                                           │
│                   (ai_generator.py)                                         │
│ generate_response(query, history, tools, tool_manager)                      │
│ 1. Prepare system prompt with conversation history                          │
│ 2. Configure API parameters with tools                                      │
│ 3. Send request to AI API                                                   │
│ 4. If tool calls requested:                                                 │
│    a. Handle tool execution (_handle_tool_execution)                        │
│    b. Send results back to AI for final response                            │
│ 5. Return final response text                                               │
└────────────────────────────┬────────────────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                     TOOL MANAGER                                            │
│                  (search_tools.py)                                          │
│ execute_tool("search_course_content", ...)                                  │
└────────────────────────────┬────────────────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                  COURSE SEARCH TOOL                                         │
│                  (search_tools.py)                                          │
│ execute(query, course_name, lesson_number)                                  │
│ 1. Call vector_store.search()                                               │
│ 2. Format search results                                                    │
│ 3. Track sources for UI                                                     │
│ 4. Return formatted results                                                 │
└────────────────────────────┬────────────────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                    VECTOR STORE                                             │
│                 (vector_store.py)                                           │
│ search(query, course_name, lesson_number)                                   │
│ 1. Resolve course name if provided (_resolve_course_name)                   │
│ 2. Build search filters (_build_filter)                                     │
│ 3. Query course_content collection in ChromaDB                              │
│ 4. Return SearchResults with documents and metadata                         │
└────────────────────────────┬────────────────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                    FINAL RESPONSE                                           │
│                     (Answer)                                                │
└────────────────────────────┬────────────────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                     FRONTEND UI                                             │
│              Display answer to user                                         │
└─────────────────────────────────────────────────────────────────────────────┘
```

