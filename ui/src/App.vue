<template>
  <RouterView />
</template>

<script>
import { mapActions, mapGetters } from "vuex";
import md5 from "md5";

export default {
  computed: {
    ...mapGetters(["oidcIsAuthenticated"]),
    ...mapGetters(["oidcUser"])
  },
  methods: {
    md5,
    ...mapActions(["signOutOidc"])
  }
};
</script>

<style>
.fill-width {
  min-width: 100%;
}
code:before {
  content: "";
}
</style>
