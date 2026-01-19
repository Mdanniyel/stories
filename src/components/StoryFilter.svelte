<script>
  import { onMount } from 'svelte';
  
  // 1. קבלת Props בעזרת $props
  let { allStories = [] } = $props();

  // 2. הגדרת State בעזרת $state
  let selectedAuthor = $state("");
  let selectedTag = $state("");
  let searchQuery = $state("");
  let currentPage = $state(1);
  
  const itemsPerPage = 24;

  // 3. משתנים מחושבים בעזרת $derived
  // Svelte 5 מבין לבד מתי לעדכן אותם כשהתלויות משתנות
  let authors = $derived([...new Set(allStories.map(s => s.data.author))].sort());
  let uniqueTags = $derived([...new Set(allStories.flatMap(s => s.data.tags || []))].sort());

  // לוגיקת הסינון
  let filteredStories = $derived(allStories.filter(story => {
    const matchAuthor = selectedAuthor ? story.data.author === selectedAuthor : true;
    const matchTag = selectedTag ? (story.data.tags || []).includes(selectedTag) : true;
    const matchSearch = searchQuery ? story.data.title.includes(searchQuery) : true;
    return matchAuthor && matchTag && matchSearch;
  }));

  // לוגיקת הפגינציה
  let totalPages = $derived(Math.ceil(filteredStories.length / itemsPerPage));
  
  let paginatedStories = $derived(filteredStories.slice(
      (currentPage - 1) * itemsPerPage, 
      currentPage * itemsPerPage
  ));

  // פונקציה לאיפוס עמוד כשמשנים פילטר
  function resetPage() {
      currentPage = 1;
  }

  // טעינת פרמטרים מה-URL
  onMount(() => {
    const params = new URLSearchParams(window.location.search);
    if (params.get('author')) selectedAuthor = params.get('author');
    if (params.get('tag')) selectedTag = params.get('tag');
  });

  function nextPage() {
      if (currentPage < totalPages) {
          currentPage++;
          window.scrollTo({ top: 0, behavior: 'smooth' });
      }
  }

  function prevPage() {
      if (currentPage > 1) {
          currentPage--;
          window.scrollTo({ top: 0, behavior: 'smooth' });
      }
  }

  // פונקציה לטיפול בלחיצה על מחבר (כדי למנוע מעבר לדף הסיפור)
  function selectAuthor(author, e) {
      e.preventDefault();
      e.stopPropagation(); // מונע את הלחיצה על ה-Link העוטף
      selectedAuthor = author;
      resetPage();
  }
</script>

<div dir="rtl" class="font-sans">
  <div class="mb-8 grid grid-cols-1 md:grid-cols-3 gap-4 bg-gray-100 p-4 rounded-lg shadow-sm">
    <input 
      type="text" 
      bind:value={searchQuery}
      oninput={resetPage}
      placeholder="חיפוש לפי כותרת..." 
      class="p-2 border rounded focus:ring-2 focus:ring-indigo-500 outline-none"
    />

    <select 
        bind:value={selectedAuthor} 
        onchange={resetPage}
        class="p-2 border rounded focus:ring-2 focus:ring-indigo-500 outline-none"
    >
      <option value="">כל המחברים</option>
      {#each authors as author}
        <option value={author}>{author}</option>
      {/each}
    </select>

    <select 
        bind:value={selectedTag} 
        onchange={resetPage}
        class="p-2 border rounded focus:ring-2 focus:ring-indigo-500 outline-none"
    >
      <option value="">כל התגיות</option>
      {#each uniqueTags as tag}
        <option value={tag}>{tag}</option>
      {/each}
    </select>
  </div>

  <div class="flex justify-between items-center mb-4 text-gray-600">
      <p>נמצאו {filteredStories.length} סיפורים (עמוד {currentPage} מתוך {totalPages})</p>
  </div>

  <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
    {#each paginatedStories as story}
      <a href={`/stories/${story.slug}`} class="group block p-6 bg-white border border-gray-200 rounded-xl hover:shadow-lg hover:border-indigo-300 transition duration-200 no-underline">
        <h2 class="text-xl font-bold mb-3 text-gray-800 group-hover:text-indigo-700 transition-colors">
            {story.data.title}
        </h2>
        
        <div class="flex justify-between items-center text-sm text-gray-500 mt-auto border-t pt-3 border-gray-100">
             <button 
                onclick={(e) => selectAuthor(story.data.author, e)}
                class="hover:text-indigo-600 hover:bg-indigo-50 px-2 py-1 rounded transition-colors cursor-pointer"
             >
                ✍️ {story.data.author}
             </button>
             <span>📅 {new Date(story.data.date).toLocaleDateString('he-IL')}</span>
        </div>

        {#if story.data.tags && story.data.tags.length > 0}
          <div class="mt-4 flex gap-2 flex-wrap">
            {#each story.data.tags.slice(0,3) as tag}
              <span class="text-xs bg-gray-100 text-gray-600 px-2 py-1 rounded-full group-hover:bg-indigo-50 group-hover:text-indigo-600 transition-colors">
                  #{tag}
              </span>
            {/each}
          </div>
        {/if}
      </a>
    {/each}
  </div>

  {#if totalPages > 1}
      <div class="flex justify-center gap-4 mt-12 mb-8">
          <button 
              onclick={prevPage} 
              disabled={currentPage === 1}
              class="px-4 py-2 bg-white border rounded hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
          >
              → הקודם
          </button>
          
          <span class="flex items-center px-4 font-bold text-indigo-800">
              {currentPage} / {totalPages}
          </span>

          <button 
              onclick={nextPage} 
              disabled={currentPage === totalPages}
              class="px-4 py-2 bg-white border rounded hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
          >
              הבא ←
          </button>
      </div>
  {/if}
</div>