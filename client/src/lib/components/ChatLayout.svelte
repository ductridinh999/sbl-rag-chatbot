<script lang="ts">
  import { Sparkles } from 'lucide-svelte';
  import ChatInput from './ChatInput.svelte';
  import MessageBubble from './MessageBubble.svelte';
  import { tick } from 'svelte';

  interface Message {
    role: 'user' | 'assistant';
    content: string;
  }

  interface Props {
    messages: Message[];
    isLoading: boolean;
    onSend: (message: string) => void;
  }

  let { messages, isLoading, onSend }: Props = $props();
  
  let scrollContainer: HTMLDivElement;

  $effect(() => {
    if (messages.length) {
      scrollToBottom();
    }
  });

  async function scrollToBottom() {
    await tick();
    if (scrollContainer) {
      scrollContainer.scrollTop = scrollContainer.scrollHeight;
    }
  }
</script>

<div class="flex flex-col h-screen bg-white text-gray-900 font-sans">
  <header class="flex-none p-4 pl-6 flex items-center gap-2 text-xl font-medium text-gray-700 bg-white z-10">
    <Sparkles class="text-blue-500" size={24} />
    <span class="bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent font-semibold"> Science-Based Lifting Chatbot</span>
  </header>

  <!-- Scroll Area -->
  <div 
    bind:this={scrollContainer}
    class="flex-1 overflow-y-auto w-full max-w-4xl mx-auto px-2 sm:px-4"
  >
    <div class="py-10">
      {#if messages.length === 0}
        <div class="h-full flex flex-col items-center justify-center text-center opacity-50 mt-20">
          <Sparkles size={48} class="text-blue-300 mb-4" />
          <h2 class="text-2xl font-semibold mb-2">Hello there</h2>
          <p>How can I help you with your fitness journey today?</p>
        </div>
      {/if}

      {#each messages as msg, i}
        <MessageBubble 
          role={msg.role} 
          content={msg.content} 
          isStreaming={isLoading && i === messages.length - 1 && msg.role === 'assistant'} 
        />
      {/each}
    </div>
  </div>

  <!-- Input Area -->
  <div class="flex-none pt-2 bg-gradient-to-t from-white via-white to-transparent">
    <ChatInput {isLoading} {onSend} />
  </div>
</div>
