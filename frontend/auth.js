/**
 * 鉴权：未登录跳转登录页；为发往后端的 fetch 自动附加 Bearer Token。
 */
(function () {
  var API_MARK = "127.0.0.1:5000";

  var path = window.location.pathname || "";
  var isAuthPage = /login\.html$/i.test(path) || /register\.html$/i.test(path);
  if (!isAuthPage && !sessionStorage.getItem("auth_token")) {
    window.location.replace("login.html");
    return;
  }

  var origFetch = window.fetch.bind(window);
  window.fetch = function (input, init) {
    init = init || {};
    var url = typeof input === "string" ? input : input.url;
    if (url && url.indexOf(API_MARK) !== -1) {
      var token = sessionStorage.getItem("auth_token");
      if (token) {
        var h = new Headers(init.headers || {});
        if (!h.has("Authorization")) {
          h.set("Authorization", "Bearer " + token);
        }
        init.headers = h;
      }
    }
    return origFetch(input, init);
  };

  window.legalLogout = async function () {
    try {
      var t = sessionStorage.getItem("auth_token");
      if (t) {
        await origFetch("http://127.0.0.1:5000/api/auth/logout", {
          method: "POST",
          headers: { Authorization: "Bearer " + t },
        });
      }
    } catch (e) {}
    sessionStorage.removeItem("auth_token");
    window.location.href = "login.html";
  };
})();
