<script lang="ts">
  import ChatLayout from './lib/components/ChatLayout.svelte';

  interface Message {
    role: 'user' | 'assistant';
    content: string;
  }

  let messages = $state<Message[]>([]);
  let isLoading = $state(false);

  async function sendMessage(query: string) {
    // Prepare History
    const history = messages
      .filter(m => m.content !== " Sorry, something went wrong. Please try again.")
      .map(m => ({
        role: m.role,
        content: m.content
      }));

    console.log("Debug - Sending Payload:", { query, history });

    // Optimistic UI Update
    messages = [...messages, { role: 'user', content: query }];
    isLoading = true;

    try {
      const response = await fetch('http://localhost:8000/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ query, history }),
      });

      if (!response.ok) {
        throw new Error(`Server Error: ${response.status}`);
      }

      const data = await response.json();
      
      // Handle Response
      if (!data.answer) throw new Error("No answer received from backend");

      messages = [...messages, { role: 'assistant', content: '' }];
      
      const fullText = data.answer;
      let currentContent = '';
      
      // Fake Streaming Effect
      const tokens = fullText.split(/(?=[\s\S])/);
      for (const char of tokens) {
        await new Promise(r => setTimeout(r, 10)); // 10ms delay
        currentContent += char;
        // Update the last message
        messages[messages.length - 1].content = currentContent;
      }
    } catch (error) {
      console.error('Chat Error:', error);
      messages = [...messages, { role: 'assistant', content: " Sorry, something went wrong. Please try again." }];
    } finally {
      isLoading = false; // Always re-enable the input
    }
  }
</script>

<ChatLayout {messages} {isLoading} onSend={sendMessage} />
