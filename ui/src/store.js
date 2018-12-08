import Vue from "vue";
import Vuex from "vuex";
import VuexPersist from "vuex-persist";
import { vuexOidcCreateStoreModule } from "vuex-oidc";

Vue.use(Vuex);

const oidcSettings = {
  authority: process.env.VUE_APP_IDP_URL,
  client_id: "aws-credentials-issuer",
  redirect_uri: window.location.origin + "/oidc-callback",
  response_type: "id_token token",
  scope: "openid profile",
  post_logout_redirect_uri: window.location.origin
};

const vuexLocalStorage = new VuexPersist({
  key: "vuex",
  storage: window.localStorage
});

export default new Vuex.Store({
  modules: {
    authentication: vuexOidcCreateStoreModule(oidcSettings)
  },
  plugins: [vuexLocalStorage.plugin]
});
