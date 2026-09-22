(() => {
  const options = document.getElementById("options");
  const feedback = document.getElementById("feedback");
  const nextBtn = document.getElementById("next-btn");
  const csrf = document.querySelector('meta[name="csrf-token"]').content;
  const buttons = [...options.querySelectorAll(".option")];
  const KEYS = { a: 0, b: 1, c: 2, d: 3, 1: 0, 2: 1, 3: 2, 4: 3 };
  let answered = false;

  async function answer(btn) {
    if (answered) return;
    answered = true;
    buttons.forEach((b) => (b.disabled = true));
    btn.classList.add("picked");

    let data;
    try {
      const res = await fetch("/quiz/answer", {
        method: "POST",
        headers: { "Content-Type": "application/json", "X-CSRF-Token": csrf },
        body: JSON.stringify({ choice: btn.dataset.code }),
      });
      data = await res.json();
      if (!res.ok) throw new Error(data.error || "Request failed");
    } catch (err) {
      feedback.textContent = "Something went wrong. Reloading…";
      setTimeout(() => location.reload(), 1200);
      return;
    }

    buttons.forEach((b) => {
      if (b.dataset.code === data.answer) b.classList.add("correct");
      else if (b === btn) b.classList.add("wrong");
    });
    const correctName = buttons.find((b) => b.dataset.code === data.answer).lastChild.textContent.trim();
    feedback.textContent = data.correct ? "Correct!" : `Not quite. It's ${correctName}.`;
    feedback.className = "feedback " + (data.correct ? "good" : "bad");

    nextBtn.href = data.next;
    nextBtn.textContent = data.finished ? "See results" : "Next";
    nextBtn.hidden = false;
    nextBtn.focus();
  }

  options.addEventListener("click", (e) => {
    const btn = e.target.closest(".option");
    if (btn) answer(btn);
  });

  // Keyboard: A-D or 1-4 to answer, Enter for next.
  document.addEventListener("keydown", (e) => {
    if (e.metaKey || e.ctrlKey || e.altKey) return;
    const isEnter = e.key === "Enter" || e.code === "Enter" || e.keyCode === 13;
    if (isEnter) {
      if (!nextBtn.hidden) {
        e.preventDefault();
        location.href = nextBtn.href;
      }
      return;
    }
    const idx = KEYS[(e.key || "").toLowerCase()];
    if (!answered && idx !== undefined && buttons[idx]) answer(buttons[idx]);
  });
})();
