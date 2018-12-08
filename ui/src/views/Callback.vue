<template><div /></template>

<script>
import { mapActions, mapGetters } from "vuex";

import router from "@/router";

export default {
  name: "OidcCallback",
  computed: {
    ...mapGetters(["oidcUser"])
  },
  mounted() {
    this.oidcSignInCallback()
      .then(redirectPath => {
        router.push(redirectPath);
      })
      .catch(err => {
        console.error(err);
      });
  },
  methods: {
    ...mapActions(["oidcSignInCallback"])
  }
};
</script>
