<script>
  let question = "";
  let chatHistory = [];
  let loading = false;

  async function askQuestion() {
    if (!question.trim()) return;

    // Add User Message to UI immediately
    chatHistory = [...chatHistory, { type: 'user', text: question }];
    const currentQuestion = question;
    question = ""; // Clear input
    loading = true;

    try {
      // Call API
      const response = await fetch('http://localhost:8000/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ query: currentQuestion })
      });

      const data = await response.json();

      // Add Bot Response to UI
      chatHistory = [...chatHistory, { 
        type: 'bot', 
        text: data.answer,
        sources: data.sources 
      }];
    } catch (error) {
      chatHistory = [...chatHistory, { type: 'error', text: "Error connecting to the brain." }];
    } finally {
      loading = false;
    }
  }
</script>

<main class="container">
  <h1>🏋️ Hypertrophy Expert Chatbot</h1>
  
  <div class="chat-window">
    {#each chatHistory as msg}
      <div class="message {msg.type}">
        <div class="bubble">
          {@html msg.text}
        </div>
        {#if msg.sources && msg.sources.length > 0}
          <div class="sources">
            <small>📚 Sources: {msg.sources.join(', ')}</small>
          </div>
        {/if}
      </div>
    {/each}

    {#if loading}
      <div class="message bot">
        <div class="bubble loading">Thinking...</div>
      </div>
    {/if}
  </div>

  <div class="input-area">
    <input 
      bind:value={question} 
      on:keydown={(e) => e.key === 'Enter' && askQuestion()}
      placeholder="Ask about hypertrophy, mechanics, etc..." 
    />
    <button on:click={askQuestion} disabled={loading}>Send</button>
  </div>
</main>

<style>
  :global(body) { margin: 0; font-family: sans-serif; background: #f4f4f9; }
  .container { max-width: 800px; margin: 0 auto; padding: 20px; display: flex; flex-direction: column; height: 95vh; }
  h1 { text-align: center; color: #333; margin-bottom: 20px; }
  
  .chat-window { 
    flex: 1; 
    overflow-y: auto; 
    padding: 20px; 
    background: white; 
    border-radius: 10px; 
    box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    display: flex; 
    flex-direction: column; 
    gap: 15px;
  }

  .message { display: flex; flex-direction: column; max-width: 80%; }
  .message.user { align-self: flex-end; align-items: flex-end; }
  .message.bot { align-self: flex-start; }
  
  .bubble { padding: 12px 16px; border-radius: 12px; line-height: 1.5; }
  .user .bubble { background: #007bff; color: white; border-bottom-right-radius: 2px; }
  .bot .bubble { background: #e9ecef; color: #333; border-bottom-left-radius: 2px; }
  .loading { font-style: italic; color: #666; }

  .sources { font-size: 0.8em; color: #666; margin-top: 5px; margin-left: 5px; }

  .input-area { margin-top: 20px; display: flex; gap: 10px; }
  input { flex: 1; padding: 15px; border-radius: 8px; border: 1px solid #ddd; font-size: 16px; }
  button { padding: 0 25px; background: #007bff; color: white; border: none; border-radius: 8px; cursor: pointer; font-weight: bold; }
  button:disabled { background: #ccc; }
</style>