<script lang="ts">
  import { ArrowUp } from 'lucide-svelte';

  interface Props {
    isLoading: boolean;
    onSend: (message: string) => void;
  }

  let { isLoading, onSend }: Props = $props();
  let input = $state('');
  let textarea: HTMLTextAreaElement;

  function handleInput() {
    if (textarea) {
      textarea.style.height = 'auto';
      textarea.style.height = `${Math.min(textarea.scrollHeight, 150)}px`;
    }
  }

  function handleSubmit() {
    if (!input.trim() || isLoading) return;
    onSend(input);
    input = '';
    if (textarea) {
        textarea.style.height = 'auto';
    }
  }

  function handleKeydown(e: KeyboardEvent) {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSubmit();
    }
  }
</script>

<div class="w-full max-w-4xl mx-auto px-4 pb-6">
  <div class="relative flex items-end gap-2 bg-[#1E1F20] rounded-[2rem] p-2 pl-6 transition-colors focus-within:bg-[#2A2B2C] border border-transparent focus-within:border-gray-600">
    <textarea
      bind:this={textarea}
      bind:value={input}
      oninput={handleInput}
      onkeydown={handleKeydown}
      placeholder="Ask about your fitness plan..."
      class="w-full bg-transparent border-none outline-none resize-none py-3 max-h-[150px] text-gray-100 placeholder:text-gray-400"
      rows="1"
      disabled={isLoading}
    ></textarea>
    
    <button
      onclick={handleSubmit}
      disabled={!input.trim() || isLoading}
      class="mb-1 mr-1 p-2 rounded-full bg-blue-500 hover:bg-blue-600 disabled:bg-[#303030] disabled:text-gray-500 disabled:cursor-not-allowed transition-colors text-white flex items-center justify-center w-10 h-10"
      aria-label="Send message"
    >
      <ArrowUp size={20} />
    </button>
  </div>
  <div class="text-center text-xs text-gray-500 mt-2">
    This Chatbot can make mistakes. Check important info.
  </div>
</div>