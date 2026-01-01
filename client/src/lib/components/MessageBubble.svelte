<script lang="ts">
  import { Sparkles } from 'lucide-svelte';
  import { marked } from 'marked';

  interface Props {
    role: 'user' | 'assistant';
    content: string;
    isStreaming?: boolean;
  }

  let { role, content, isStreaming = false }: Props = $props();

  let parsedContent = $derived(role === 'assistant' ? marked.parse(content) : content);
</script>

<div class={`flex w-full ${role === 'user' ? 'justify-end' : 'justify-start'} mb-6`}>
  {#if role === 'assistant'}
    <div class="mr-3 mt-1 flex-shrink-0 text-blue-400">
      <Sparkles size={24} />
    </div>
  {/if}

  <div
    class={`max-w-[85%] sm:max-w-[75%] rounded-2xl px-5 py-3 ${
      role === 'user'
        ? 'bg-[#303030] text-gray-100'  /* Dark Grey bubble for user */
        : 'bg-transparent text-gray-100 px-0 py-0'
    }`}
  >
    {#if role === 'assistant'}
      <div class="prose prose-invert max-w-none text-gray-200 leading-relaxed">
        {@html parsedContent}
        {#if isStreaming}
          <span class="inline-block w-2 h-4 bg-blue-400 animate-pulse ml-1 align-middle rounded-full"></span>
        {/if}
      </div>
    {:else}
      <p class="whitespace-pre-wrap text-[15px]">{content}</p>
    {/if}
  </div>
</div>