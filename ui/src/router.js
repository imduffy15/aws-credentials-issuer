import Vue from "vue";
import Router from "vue-router";
import { vuexOidcCreateRouterMiddleware } from "vuex-oidc";

import store from "./store";
import Dashboard from "./views/Dashboard.vue";
import Callback from "./views/Callback.vue";

Vue.use(Router);

var router = new Router({
  mode: "history",
  routes: [
    {
      path: "/",
      name: "dashboard",
      component: Dashboard
    },
    {
      path: "/oidc-callback",
      name: "callback",
      component: Callback,
      meta: {
        isVuexOidcCallback: true,
        isPublic: true
      }
    }
  ]
});

router.beforeEach((to, from, next) => {
  return vuexOidcCreateRouterMiddleware(store)(to, from, next);
});

export default router;
