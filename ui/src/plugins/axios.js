import axios from "axios";
import store from "../store";

axios.interceptors.request.use(
  function(config) {
    const token = store.state.authentication.access_token;
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  function(err) {
    return Promise.reject(err);
  }
);
