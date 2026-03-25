/**
 * 鉴权工具（登录检测已禁用，合并时取消注释相关代码）
 * 
 * 功能说明：
 * 1. 已禁用：未登录跳转登录页检测
 * 2. 已保留：为发往后端的 fetch 自动附加 Bearer Token（供合并后使用）
 */
(function () {
  var API_MARK = "127.0.0.1:5000";

  // === 登录注册功能（已禁用，合并时取消注释） ===
  // var path = window.location.pathname || "";
  // var isAuthPage = /login\.html$/i.test(path) || /register\.html$/i.test(path);
  // if (!isAuthPage && !sessionStorage.getItem("auth_token")) {
  //   window.location.replace("login.html");
  //   return;
  // }
  // =============================================

  // 保留：为发往后端的请求自动附加 Token（合并后恢复登录功能时使用）
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

  // === 登录注册功能（已禁用，合并时取消注释） ===
  // window.legalLogout = async function () {
  //   try {
  //     var t = sessionStorage.getItem("auth_token");
  //     if (t) {
  //       await origFetch("http://127.0.0.1:5000/api/auth/logout", {
  //         method: "POST",
  //         headers: { Authorization: "Bearer " + t },
  //       });
  //     }
  //   } catch (e) {}
  //   sessionStorage.removeItem("auth_token");
  //   window.location.href = "login.html";
  // };
  // =============================================
})();