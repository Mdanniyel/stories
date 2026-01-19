<script>
  import { onMount } from "svelte";

  // 1. קבלת Props בעזרת $props
  let { allStories = [] } = $props();

  // 2. הגדרת State בעזרת $state
  let selectedAuthor = $state("");
  let selectedTag = $state("");
  let selectedCategory = $state("");
  let searchQuery = $state("");
  let currentPage = $state(1);
  let pagefindResults = $state(null); // null means no search active, Set<string> means filtered slugs
  let isSearching = $state(false);

  const itemsPerPage = 24;

  // 3. משתנים מחושבים בעזרת $derived
  // Svelte 5 מבין לבד מתי לעדכן אותם כשהתלויות משתנות
  let authors = $derived(
    [...new Set(allStories.map((s) => s.data.author))].sort(),
  );
  let uniqueTags = $derived(
    [...new Set(allStories.flatMap((s) => s.data.tags || []))].sort(),
  );
  let uniqueCategories = $derived(
    [...new Set(allStories.map((s) => s.data.category).filter(Boolean))].sort(),
  );

  // לוגיקת הסינון
  let filteredStories = $derived(
    allStories.filter((story) => {
      const matchAuthor = selectedAuthor
        ? story.data.author === selectedAuthor
        : true;
      const matchTag = selectedTag
        ? (story.data.tags || []).includes(selectedTag)
        : true;
      const matchCategory = selectedCategory
        ? story.data.category === selectedCategory
        : true;

      // אם יש תוצאות חיפוש מ-Pagefind, נבדוק אם הסלאג קיים בהן
      // אם השאילתה ריקה, pagefindResults צריך להיות null
      const matchSearch = pagefindResults
        ? pagefindResults.has(story.slug)
        : true;

      // Fallback: If pagefind is not active but we have a query (e.g. dev mode without build), do simple title search
      const fallbackSearch =
        !pagefindResults && searchQuery
          ? story.data.title.toLowerCase().includes(searchQuery.toLowerCase())
          : true;

      return (
        matchAuthor &&
        matchTag &&
        matchCategory &&
        matchSearch &&
        fallbackSearch
      );
    }),
  );

  // לוגיקת הפגינציה
  let totalPages = $derived(Math.ceil(filteredStories.length / itemsPerPage));

  let paginatedStories = $derived(
    filteredStories.slice(
      (currentPage - 1) * itemsPerPage,
      currentPage * itemsPerPage,
    ),
  );

  // פונקציה לאיפוס עמוד כשמשנים פילטר
  function resetPage() {
    currentPage = 1;
  }

  // Pagefind Integration
  let pagefind = null;

  onMount(async () => {
    // טעינת פרמטרים מה-URL
    const params = new URLSearchParams(window.location.search);
    if (params.get("author")) selectedAuthor = params.get("author");
    if (params.get("tag")) selectedTag = params.get("tag");
    if (params.get("category")) selectedCategory = params.get("category");
    if (params.get("q")) {
      searchQuery = params.get("q");
      handleSearch(); // Trigger search immediately if param exists
    }

    // Load Pagefind
    try {
      pagefind = await import("/pagefind/pagefind.js");
      await pagefind.init();
    } catch (e) {
      console.log(
        "Pagefind not found (likely in dev mode), falling back to title search.",
      );
    }
  });

  async function handleSearch() {
    resetPage();
    if (!searchQuery.trim()) {
      pagefindResults = null;
      return;
    }

    if (pagefind) {
      isSearching = true;
      try {
        const search = await pagefind.search(searchQuery);
        // Extract slugs from URLs. URLs are like "/stories/slug/" or "/stories/slug.html"
        const slugs = new Set(
          search.results
            .map((r) => {
              // Adjust regex based on your actual URL structure
              const match = r.url.match(/\/stories\/([^\/.]+)/);
              return match ? match[1] : null;
            })
            .filter(Boolean),
        );

        pagefindResults = slugs;
      } catch (e) {
        console.error("Search error:", e);
        // Fallback handled in derived
        pagefindResults = null;
      } finally {
        isSearching = false;
      }
    } else {
      // Dev mode fallback is handled automatically in derived filteredStories via 'fallbackSearch'
      pagefindResults = null;
    }
  }

  // Wrappers to combine search trigger with input
  function onSearchInput() {
    // Debounce logic could go here if needed, for now we search on simple input or wait for 'enter'
    // For Pagefind, usually better to debounce or wait for explicit action to avoid too many requests
    // But for local fallback, instant is fine.
    // Let's do simple debounce
    clearTimeout(window.searchTimeout);
    window.searchTimeout = setTimeout(handleSearch, 300);
  }

  function commonReset() {
    resetPage();
  }

  function nextPage() {
    if (currentPage < totalPages) {
      currentPage++;
      window.scrollTo({ top: 0, behavior: "smooth" });
    }
  }

  function prevPage() {
    if (currentPage > 1) {
      currentPage--;
      window.scrollTo({ top: 0, behavior: "smooth" });
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
  <div
    class="mb-8 grid grid-cols-1 md:grid-cols-4 gap-4 bg-gray-100 p-4 rounded-lg shadow-sm"
  >
    <div class="relative">
      <input
        type="text"
        bind:value={searchQuery}
        oninput={onSearchInput}
        placeholder="חיפוש חופשי..."
        class="w-full p-2 border rounded focus:ring-2 focus:ring-indigo-500 outline-none"
      />
      {#if isSearching}
        <span class="absolute left-2 top-2 text-gray-400 text-sm">...</span>
      {/if}
    </div>

    <select
      bind:value={selectedAuthor}
      onchange={commonReset}
      class="p-2 border rounded focus:ring-2 focus:ring-indigo-500 outline-none"
    >
      <option value="">כל המחברים</option>
      {#each authors as author}
        <option value={author}>{author}</option>
      {/each}
    </select>

    <select
      bind:value={selectedCategory}
      onchange={commonReset}
      class="p-2 border rounded focus:ring-2 focus:ring-indigo-500 outline-none"
    >
      <option value="">כל הקטגוריות</option>
      {#each uniqueCategories as cat}
        <option value={cat}>{cat}</option>
      {/each}
    </select>

    <select
      bind:value={selectedTag}
      onchange={commonReset}
      class="p-2 border rounded focus:ring-2 focus:ring-indigo-500 outline-none"
    >
      <option value="">כל התגיות</option>
      {#each uniqueTags as tag}
        <option value={tag}>{tag}</option>
      {/each}
    </select>
  </div>

  <div class="flex justify-between items-center mb-4 text-gray-600">
    <p>
      נמצאו {filteredStories.length} סיפורים (עמוד {currentPage} מתוך {totalPages})
      {#if !pagefind && searchQuery}
        <span class="text-xs text-orange-500 mr-2"
          >(מצב פיתוח: חיפוש בכותרות בלבד)</span
        >
      {/if}
    </p>
  </div>

  <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
    {#each paginatedStories as story}
      <a
        href={`${import.meta.env.BASE_URL}${story.slug}`}
        class="group block p-6 bg-white border border-gray-200 rounded-xl hover:shadow-lg hover:border-indigo-300 transition duration-200 no-underline"
      >
        <h2
          class="text-xl font-bold mb-3 text-gray-800 group-hover:text-indigo-700 transition-colors"
        >
          {story.data.title}
        </h2>

        <div class="flex flex-col gap-2 mt-auto border-t pt-3 border-gray-100">
          <div class="flex justify-between items-center text-sm text-gray-500">
            <button
              onclick={(e) => selectAuthor(story.data.author, e)}
              class="hover:text-indigo-600 hover:bg-indigo-50 px-2 py-1 rounded transition-colors cursor-pointer"
            >
              ✍️ {story.data.author}
            </button>
            <span
              >📅 {new Date(story.data.date).toLocaleDateString("he-IL")}</span
            >
          </div>

          {#if story.data.category}
            <div class="flex gap-2 flex-wrap text-xs">
              <span class="bg-indigo-50 text-indigo-700 px-2 py-0.5 rounded">
                {story.data.category}
              </span>
            </div>
          {/if}
        </div>

        {#if story.data.tags && story.data.tags.length > 0}
          <div class="mt-4 flex gap-2 flex-wrap">
            {#each story.data.tags.slice(0, 3) as tag}
              <span
                class="text-xs bg-gray-100 text-gray-600 px-2 py-1 rounded-full group-hover:bg-indigo-50 group-hover:text-indigo-600 transition-colors"
              >
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
