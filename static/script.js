const $ = (s) => document.querySelector(s);
const $$ = (s) => [...document.querySelectorAll(s)];
const api = async (url, options = {}) => {
  const response = await fetch(url, {
    headers: {"Content-Type": "application/json"},
    ...options
  });
  const data = await response.json();
  if (!response.ok) throw new Error(data.error || "Something went wrong.");
  return data;
};
function toast(message) {
  const el = $("#toast"); el.textContent = message; el.classList.add("show");
  clearTimeout(window.toastTimer);
  window.toastTimer = setTimeout(() => el.classList.remove("show"), 2600);
}
function showView(name) {
  $$(".view").forEach(v => v.classList.add("hidden"));
  $(`#${name}-view`).classList.remove("hidden");
  $$(".nav-item").forEach(b => b.classList.toggle("active", b.dataset.view === name));
  $("#page-title").textContent = ({dashboard:"Overview",books:"Books",members:"Members",loans:"Issue & return"})[name];
  if (name === "dashboard") loadDashboard();
  if (name === "books") loadBooks();
  if (name === "members") loadMembers();
  if (name === "loans") loadLoans();
}
$$(".nav-item").forEach(b => b.addEventListener("click", () => showView(b.dataset.view)));
$$(".quick-card").forEach(b => b.addEventListener("click", () => showView(b.dataset.go)));

async function loadDashboard() {
  try {
    const d = await api("/api/dashboard");
    $("#total-books").textContent = d.total_books;
    $("#available-books").textContent = d.available_books;
    $("#issued-books").textContent = d.issued_books;
    $("#members-count").textContent = d.members;
  } catch(e) { toast(e.message); }
}
function emptyRow(cols, message) { return `<tr><td colspan="${cols}" class="empty">${message}</td></tr>`; }

async function loadBooks(query = "") {
  try {
    const books = await api(`/api/books?q=${encodeURIComponent(query)}`);
    $("#book-count").textContent = books.length;
    $("#books-body").innerHTML = books.length ? books.map(b => `
      <tr><td>${escapeHtml(b.title)}</td><td>${escapeHtml(b.author)}</td>
      <td>${escapeHtml(b.isbn)}</td><td>${escapeHtml(b.category)}</td>
      <td><span class="status ${b.status === "Issued" ? "issued" : ""}">${b.status}</span></td>
      <td><button class="delete-btn" data-delete-book="${b.id}">Delete</button></td></tr>`).join("") : emptyRow(6, "No books found. Add your first book.");
    $$("[data-delete-book]").forEach(btn => btn.addEventListener("click", async () => {
      if (!confirm("Delete this book?")) return;
      try { await api(`/api/books/${btn.dataset.deleteBook}`, {method:"DELETE"}); toast("Book deleted."); loadBooks($("#book-search").value); loadDashboard(); }
      catch(e) { toast(e.message); }
    }));
  } catch(e) { toast(e.message); }
}
function escapeHtml(value) {
  return String(value ?? "").replace(/[&<>"']/g, c => ({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#39;"}[c]));
}
$("#book-search").addEventListener("input", e => loadBooks(e.target.value));
$("#show-book-form").addEventListener("click", () => $("#book-form").classList.toggle("hidden"));
$("#cancel-book").addEventListener("click", () => $("#book-form").classList.add("hidden"));
$("#book-form").addEventListener("submit", async e => {
  e.preventDefault(); const data = Object.fromEntries(new FormData(e.target));
  try { await api("/api/books", {method:"POST",body:JSON.stringify(data)}); e.target.reset(); e.target.classList.add("hidden"); toast("Book added."); loadBooks(); loadDashboard(); }
  catch(err) { toast(err.message); }
});

async function loadMembers() {
  try {
    const members = await api("/api/members");
    $("#members-body").innerHTML = members.length ? members.map(m => `
      <tr><td>${escapeHtml(m.name)}</td><td>${escapeHtml(m.email)}</td><td>${escapeHtml(m.phone || "—")}</td>
      <td><button class="delete-btn" data-delete-member="${m.id}">Delete</button></td></tr>`).join("") : emptyRow(4, "No members registered yet.");
    $$("[data-delete-member]").forEach(btn => btn.addEventListener("click", async () => {
      if (!confirm("Delete this member?")) return;
      try { await api(`/api/members/${btn.dataset.deleteMember}`, {method:"DELETE"}); toast("Member deleted."); loadMembers(); loadDashboard(); }
      catch(e) { toast(e.message); }
    }));
  } catch(e) { toast(e.message); }
}
$("#show-member-form").addEventListener("click", () => $("#member-form").classList.toggle("hidden"));
$("#cancel-member").addEventListener("click", () => $("#member-form").classList.add("hidden"));
$("#member-form").addEventListener("submit", async e => {
  e.preventDefault(); const data = Object.fromEntries(new FormData(e.target));
  try { await api("/api/members", {method:"POST",body:JSON.stringify(data)}); e.target.reset(); e.target.classList.add("hidden"); toast("Member registered."); loadMembers(); loadDashboard(); }
  catch(err) { toast(err.message); }
});

async function loadLoans() {
  try {
    const [books, members, loans] = await Promise.all([api("/api/books"),api("/api/members"),api("/api/loans")]);
    $("#loan-book").innerHTML = '<option value="">Choose a book</option>' + books.filter(b => b.status === "Available").map(b => `<option value="${b.id}">${escapeHtml(b.title)} — ${escapeHtml(b.author)}</option>`).join("");
    $("#loan-member").innerHTML = '<option value="">Choose a member</option>' + members.map(m => `<option value="${m.id}">${escapeHtml(m.name)}</option>`).join("");
    $("#loans-body").innerHTML = loans.length ? loans.map(l => `
      <tr><td>${escapeHtml(l.title)}</td><td>${escapeHtml(l.isbn)}</td><td>${escapeHtml(l.member)}</td>
      <td>${escapeHtml(l.issue_date)}</td><td><button class="return-btn" data-return="${l.id}">Return book ↗</button></td></tr>`).join("") : emptyRow(5, "No books are currently issued.");
    $$("[data-return]").forEach(btn => btn.addEventListener("click", async () => {
      try { await api(`/api/loans/${btn.dataset.return}/return`, {method:"POST"}); toast("Book returned."); loadLoans(); loadDashboard(); }
      catch(e) { toast(e.message); }
    }));
  } catch(e) { toast(e.message); }
}
$("#loan-form").addEventListener("submit", async e => {
  e.preventDefault(); const data = Object.fromEntries(new FormData(e.target));
  try { await api("/api/loans", {method:"POST",body:JSON.stringify(data)}); e.target.reset(); toast("Book issued successfully."); loadLoans(); loadDashboard(); }
  catch(err) { toast(err.message); }
});
loadDashboard();
