# Prompt 2: Implement File-Based Storage System

Implement a file-based storage system for PromptBin that:
1. Stores prompts as JSON files in the prompts/ directory structure
2. Each prompt file contains: id, title, content, category, description, tags, created_at, updated_at
3. Creates a PromptManager class with methods: save_prompt(), get_prompt(), list_prompts(), delete_prompt(), search_prompts()
4. Handles file operations with proper error handling
5. Generates unique IDs for prompts using timestamps and random strings
6. Supports moving prompts between categories

Store files as: prompts/{category}/{prompt_id}.json