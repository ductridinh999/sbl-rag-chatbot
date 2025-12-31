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
        // Reset height
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
  <div class="relative flex items-end gap-2 bg-gray-100 rounded-[2rem] p-2 pl-6 transition-colors focus-within:bg-gray-200 border border-transparent focus-within:border-gray-300">
    <textarea
      bind:this={textarea}
      bind:value={input}
      oninput={handleInput}
      onkeydown={handleKeydown}
      placeholder="Ask about your fitness plan..."
      class="w-full bg-transparent border-none outline-none resize-none py-3 max-h-[150px] text-gray-800 placeholder:text-gray-500"
      rows="1"
      disabled={isLoading}
    ></textarea>
    
    <button
      onclick={handleSubmit}
      disabled={!input.trim() || isLoading}
      class="mb-1 mr-1 p-2 rounded-full bg-blue-600 hover:bg-blue-700 disabled:bg-gray-300 disabled:cursor-not-allowed transition-colors text-white flex items-center justify-center w-10 h-10"
      aria-label="Send message"
    >
      <ArrowUp size={20} />
    </button>
  </div>
  <div class="text-center text-xs text-gray-400 mt-2">
    Fitness Assistant can make mistakes. Check important info.
  </div>
</div>
