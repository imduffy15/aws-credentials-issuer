<template>
  <VApp>
    <VToolbar
      app
      color="primary"
    >
      <VToolbarTitle class="headline text-uppercase white--text">
        <span>AWS Credentials Issuer</span>
      </VToolbarTitle>
      <VSpacer />
      <VMenu
        v-if="oidcIsAuthenticated"
        :nudge-bottom="10"
        class="hidden-sm-and-down"
        offset-y
        origin="center center"
        transition="scale-transition"
      >
        <VBtn
          slot="activator"
          flat
        >
          <VAvatar
            size="30px"
            class="mr-3"
          >
            <img
              :src="oidcUser.image || `//www.gravatar.com/avatar/${md5(oidcUser.email)}`"
            >
          </VAvatar>
          {{ oidcUser.name }}
        </VBtn>
        <VList class="pa-0">
          <VListTile
            @click="signOutOidc"
          >
            <VListTileAction>
              <VIcon>logout</VIcon>
            </VListTileAction>
            <VListTileContent>
              <VListTileTitle>Logout</VListTileTitle>
            </VListTileContent>
          </VListTile>
        </VList>
      </VMenu>
    </VToolbar>

    <VContent>
      <VContainer grid-list-xl>
        <VLayout wrap>
          <VFlex
            v-for="(role, index) in oidcUser.roles"
            :key="index"
          >
            <VCard class="pa-3">
              <VCardTitle>
                <VLayout align-center>
                  <VIcon>vpn_key</VIcon>
                  <VFlex class="arn">
                    {{ role }}
                  </VFlex>
                </VLayout>
              </VCardTitle>
              <VDivider class="mb-4" />
              <VCardActions>
                <VLayout column>
                  <VFlex xs12>
                    <VBtn
                      :disabled="role in loading"
                      :loading="role in loading"
                      block
                      outline
                      color="primary"
                      @click="openWebConsole(role)"
                    >
                      Open Web Console
                    </VBtn>
                  </VFlex>
                  <VFlex xs12>
                    <VBtn
                      block
                      outline
                      color="secondary"
                      @click="show(role)"
                    >
                      Get API Credentials
                    </VBtn>
                  </VFlex>
                </VLayout>
              </VCardActions>
            </VCard>

            <VDialog
              v-model="modals[role]"
              persistent
            >
              <VCard>
                <VCardTitle primary-title>
                  <div>
                    <div class="headline">
                      Credentials for <span class="arn">
                        {{ role }}
                      </span>
                    </div>
                  </div>
                </VCardTitle>

                <VCardText>
                  <VFlex xs12>
                    <pre><code class="fill-width pa-4">{{ code }}</code></pre>
                  </Vflex>
                </VCardText>

                <VCardActions>
                  <VSpacer />
                  <VBtn
                    flat
                    color="primary"
                    @click="modals[role] = false"
                  >
                    Close
                  </VBtn>
                </VCardActions>
              </VCard>
            </VDialog>
          </VFlex>
        </VLayout>
      </VContainer>
    </VContent>
  </VApp>
</template>

<script>
import md5 from "md5";
import Vue from "vue";
import axios from "axios";
import { mapGetters, mapActions } from "vuex";

export default {
  data() {
    return {
      code: "",
      loading: {},
      modals: {}
    };
  },
  computed: {
    ...mapGetters(["oidcUser"]),
    ...mapGetters(["oidcIsAuthenticated"])
  },
  methods: {
    md5,
    show(role) {
      Vue.set(this.modals, role);
      this.modals[role] = true;
    },
    openWebConsole(arn) {
      Vue.set(this.loading, arn);
      axios
        .get(`${process.env.VUE_APP_API_GATEWAY_URL}/api/login?role=${arn}`)
        .then(response => {
          window.open(response.data.url, "_self");
        });
    },
    ...mapActions(["signOutOidc"])
  }
};
</script>

<style scoped>
.arn {
  overflow-wrap: break-word;
  word-wrap: break-word;
  hyphens: none;
}
</style>
