const buttons = document.querySelectorAll(".filter-button");
const posts = document.querySelectorAll(".post-row");

buttons.forEach((button) => {
  button.addEventListener("click", () => {
    const filter = button.dataset.filter;

    buttons.forEach((item) => item.classList.remove("is-active"));
    button.classList.add("is-active");

    posts.forEach((post) => {
      const visible = filter === "all" || post.dataset.category === filter;
      post.classList.toggle("is-hidden", !visible);
    });
  });
});
