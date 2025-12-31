<script lang="ts">
  import ChatLayout from './lib/components/ChatLayout.svelte';

  interface Message {
    role: 'user' | 'assistant';
    content: string;
  }

  let messages = $state<Message[]>([]);
  let isLoading = $state(false);

  async function sendMessage(query: string) {
    // Append User's message immediately
    messages = [...messages, { role: 'user', content: query }];
    isLoading = true;

    try {
      // Call API endpoint
      const response = await fetch('http://localhost:8000/chat', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ query }),
      });

      if (!response.ok) {
        throw new Error('Failed to connect to the assistant. Please try again.');
      }

      const data = await response.json();
      const fullText = data.answer;

      // Handle Response: Fake streaming effect
      // Add empty assistant message
      messages = [...messages, { role: 'assistant', content: '' }];
      
      let currentContent = '';
      const tokens = fullText.split(/(?=[\s\S])/); // Split by char
      
      for (const char of tokens) {
        await new Promise(r => setTimeout(r, 10 + Math.random() * 15)); // Faster fake streaming
        currentContent += char;
        // Update the last message directly
        messages[messages.length - 1].content = currentContent;
      }
    } catch (error) {
      console.error('Chat Error:', error);
      // Show concise error message
      messages = [
        ...messages, 
        { 
          role: 'assistant', 
          content: `${error instanceof Error ? error.message : 'Something went wrong. Please try again later.'}` 
        }
      ];
    } finally {
      isLoading = false;
    }
  }
</script>

<ChatLayout {messages} {isLoading} onSend={sendMessage} />
