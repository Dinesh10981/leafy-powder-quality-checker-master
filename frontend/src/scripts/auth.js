/**
 * Client-side authentication and tab switching logic for index.html
 */

function switchTab(tab) {
  const si = document.getElementById("form-signin");
  const su = document.getElementById("form-signup");
  const tsi = document.getElementById("tab-signin");
  const tsu = document.getElementById("tab-signup");
  const c = document.getElementById("forms-container");

  if (tab === "signin") {
    tsi.className = "flex-1 py-3 text-sm font-semibold text-center tab-active transition-all";
    tsu.className = "flex-1 py-3 text-sm font-semibold text-center tab-inactive transition-all";
    si.style.transform = "translateX(0)";
    si.classList.remove("invisible");
    su.style.transform = "translateX(100%)";
    setTimeout(() => su.classList.add("invisible"), 350);
    c.style.minHeight = "300px";
  } else {
    tsu.className = "flex-1 py-3 text-sm font-semibold text-center tab-active transition-all";
    tsi.className = "flex-1 py-3 text-sm font-semibold text-center tab-inactive transition-all";
    su.style.transform = "translateX(0)";
    su.classList.remove("invisible");
    si.style.transform = "translateX(-100%)";
    setTimeout(() => si.classList.add("invisible"), 350);
    c.style.minHeight = "420px";
  }
}

function showToast(msg, icon = "check_circle", isError = false) {
  const t = document.getElementById("toast");
  document.getElementById("toast-msg").textContent = msg;
  document.getElementById("toast-icon").textContent = icon;
  t.style.background = isError ? "#ba1a1a" : "#006b2c";
  t.classList.add("show");
  setTimeout(() => t.classList.remove("show"), 3200);
}

function handleSignIn(e) {
  e.preventDefault();
  const btn = document.getElementById("signin-btn");
  const lbl = document.getElementById("signin-label");
  const ico = document.getElementById("signin-icon");
  lbl.textContent = "Authenticating...";
  ico.textContent = "autorenew";
  ico.classList.add("animate-spin");
  btn.disabled = true;

  setTimeout(() => {
    ico.classList.remove("animate-spin");
    lbl.textContent = "Authenticate";
    ico.textContent = "login";
    btn.disabled = false;
    showToast("Login successful! Redirecting…", "check_circle", false);
    setTimeout(() => {
      window.location.href = "dashboard.html";
    }, 900);
  }, 1300);
}

function handleSignUp(e) {
  e.preventDefault();
  const pwd = document.getElementById("signup-password").value;
  const confirmPwd = document.getElementById("signup-confirm").value;
  if (pwd !== confirmPwd) {
    showToast("Passwords do not match.", "error", true);
    return;
  }
  showToast("Account created! Please sign in.", "person_add", false);
  setTimeout(() => switchTab("signin"), 1600);
}
