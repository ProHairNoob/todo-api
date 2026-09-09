/*
 * Todo dashboard.
 *
 * Rows are rendered by cloning the <template id="row-template"> in todos.html
 * and filling fields with textContent (never innerHTML with user data — avoids
 * needing to hand-roll HTML-escaping for titles/descriptions the user typed).
 * This was simpler and safer than building HTML strings by hand, and doesn't
 * require a server-side partial route (which we're not allowed to add).
 */

document.addEventListener("DOMContentLoaded", () => {
  if (!TODO.requireAuth()) return;

  const LIMIT = 10;
  let page = 1;
  let total = 0;
  let loadedCount = 0;

  const list = document.getElementById("todo-list");
  const emptyState = document.getElementById("empty-state");
  const loadMoreWrap = document.getElementById("load-more-wrap");
  const loadMoreBtn = document.getElementById("load-more-btn");
  const loadMoreIndicator = document.getElementById("load-more-indicator");
  const pageError = document.getElementById("page-error");
  const rowTemplate = document.getElementById("row-template");

  const addForm = document.getElementById("add-form");
  const addTitle = document.getElementById("add-title");
  const addDesc = document.getElementById("add-desc");
  const addSubmit = document.getElementById("add-submit");
  const addIndicator = document.getElementById("add-indicator");

  const logoutBtn = document.getElementById("logout-btn");

  function updateEmptyAndLoadMore() {
    emptyState.classList.toggle("hidden", total !== 0);
    const exhausted = loadedCount >= total;
    loadMoreWrap.classList.toggle("hidden", exhausted || total === 0);
  }

  function buildRow(task) {
    const node = rowTemplate.content.firstElementChild.cloneNode(true);
    node.dataset.id = task.id;
    node.querySelector(".task-title").textContent = task.title;
    node.querySelector(".task-desc").textContent = task.desc || "";
    node.querySelector(".task-desc").classList.toggle("hidden", !task.desc);
    wireRow(node, task);
    return node;
  }

  function wireRow(node, task) {
    const viewMode = node.querySelector(".view-mode");
    const editMode = node.querySelector(".edit-mode");
    const editTitle = node.querySelector(".edit-title");
    const editDesc = node.querySelector(".edit-desc");
    const editError = node.querySelector(".edit-error");

    node.querySelector(".edit-btn").addEventListener("click", () => {
      editTitle.value = node.querySelector(".task-title").textContent;
      editDesc.value = node.querySelector(".task-desc").textContent;
      TODO.hideMessage(editError);
      viewMode.classList.add("hidden");
      editMode.classList.remove("hidden");
      editTitle.focus();
    });

    node.querySelector(".cancel-btn").addEventListener("click", () => {
      editMode.classList.add("hidden");
      viewMode.classList.remove("hidden");
    });

    editMode.addEventListener("submit", async (e) => {
      e.preventDefault();
      const newTitle = editTitle.value.trim();
      if (!newTitle) {
        TODO.showMessage(editError, "Title can't be empty.");
        return;
      }
      const saveBtn = node.querySelector(".save-btn");
      saveBtn.disabled = true;

      const { ok, status, data } = await TODO.api(`/todos/${node.dataset.id}`, {
        method: "PUT",
        body: { title: newTitle, desc: editDesc.value.trim() },
      });

      saveBtn.disabled = false;

      if (!ok) {
        if (status === 404) {
          // Deleted elsewhere — remove the row with a brief notice instead of erroring.
          node.remove();
          total = Math.max(0, total - 1);
          loadedCount = Math.max(0, loadedCount - 1);
          TODO.showMessage(pageError, "That todo was already deleted elsewhere.");
          updateEmptyAndLoadMore();
          return;
        }
        TODO.showMessage(editError, TODO.errorMessage(data, "Couldn't save changes."));
        return;
      }

      node.querySelector(".task-title").textContent = data.title;
      const descEl = node.querySelector(".task-desc");
      descEl.textContent = data.desc || "";
      descEl.classList.toggle("hidden", !data.desc);
      editMode.classList.add("hidden");
      viewMode.classList.remove("hidden");
    });

    node.querySelector(".delete-btn").addEventListener("click", async () => {
      const confirmed = window.confirm(`Delete "${task.title}"?`);
      if (!confirmed) return;

      const { ok, status, data } = await TODO.api(`/todos/${node.dataset.id}`, { method: "DELETE" });

      if (!ok && status !== 404) {
        TODO.showMessage(pageError, TODO.errorMessage(data, "Couldn't delete that todo."));
        return;
      }

      // 204 (deleted) and 404 (already gone) both end with the row gone locally.
      node.remove();
      total = Math.max(0, total - 1);
      loadedCount = Math.max(0, loadedCount - 1);
      updateEmptyAndLoadMore();
    });
  }

  async function loadPage(targetPage, { append }) {
    TODO.hideMessage(pageError);
    if (append) {
      loadMoreBtn.disabled = true;
      loadMoreIndicator.classList.remove("hidden");
    }

    const { ok, data } = await TODO.api(`/todos?page=${targetPage}&limit=${LIMIT}`);

    if (append) {
      loadMoreBtn.disabled = false;
      loadMoreIndicator.classList.add("hidden");
    }

    if (!ok) {
      TODO.showMessage(pageError, TODO.errorMessage(data, "Couldn't load your todos."));
      return;
    }

    total = data.total;
    page = data.page;

    if (!append) {
      list.innerHTML = "";
      loadedCount = 0;
    }
    for (const task of data.data) {
      list.appendChild(buildRow(task));
      loadedCount += 1;
    }

    updateEmptyAndLoadMore();
  }

  loadMoreBtn.addEventListener("click", () => loadPage(page + 1, { append: true }));

  addForm.addEventListener("submit", async (e) => {
    e.preventDefault();
    const title = addTitle.value.trim();
    if (!title) return;

    addSubmit.disabled = true;
    addIndicator.classList.remove("hidden");

    const { ok, data } = await TODO.api("/todos", {
      method: "POST",
      body: { title, desc: addDesc.value.trim() },
    });

    addSubmit.disabled = false;
    addIndicator.classList.add("hidden");

    if (!ok) {
      TODO.showMessage(pageError, TODO.errorMessage(data, "Couldn't add that todo."));
      return;
    }

    list.prepend(buildRow(data));
    total += 1;
    loadedCount += 1;
    updateEmptyAndLoadMore();

    addForm.reset();
    addTitle.focus();
  });

  logoutBtn.addEventListener("click", () => {
    TODO.clearToken();
    window.location.href = TODO.ROUTES.login;
  });

  loadPage(1, { append: false });
});
