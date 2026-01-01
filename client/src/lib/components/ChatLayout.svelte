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

<div class="flex flex-col h-screen bg-[#131314] text-gray-100 font-sans">
  <header class="flex-none p-4 pl-6 flex items-center gap-2 text-xl font-medium text-gray-200 bg-[#131314] z-10">
    <Sparkles class="text-blue-400" size={24} />
    <span class="bg-gradient-to-r from-blue-400 to-purple-400 bg-clip-text text-transparent font-semibold"> Science-Based Lifting Chatbot</span>
  </header>

  <div 
    bind:this={scrollContainer}
    class="flex-1 overflow-y-auto w-full max-w-4xl mx-auto px-2 sm:px-4"
  >
    <div class="py-10">
      {#if messages.length === 0}
        <div class="h-full flex flex-col items-center justify-center text-center opacity-50 mt-20">
          <Sparkles size={48} class="text-blue-400 mb-4" />
          <h2 class="text-2xl font-semibold mb-2">Hello there</h2>
          <p class="text-gray-400">How can I help you with your fitness journey today?</p>
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

  <div class="flex-none pt-2 bg-gradient-to-t from-[#131314] via-[#131314] to-transparent">
    <ChatInput {isLoading} {onSend} />
  </div>
</div>