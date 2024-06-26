<template>
  <div
    id="account-confirmation"
    class="center-card with-margin"
    v-if="errorMessages"
  >
    <ErrorImg />
    <p class="error-message">
      <span>{{ $t('error.SOMETHING_WRONG') }}.</span>
      <router-link class="links" to="/account-confirmation/resend">
        {{ $t('buttons.ACCOUNT-CONFIRMATION-RESEND') }}?
      </router-link>
    </p>
  </div>
</template>

<script setup lang="ts">
  import { computed, onBeforeMount, onUnmounted } from 'vue'
  import type { ComputedRef } from 'vue'
  import { useRoute, useRouter } from 'vue-router'
  import type { LocationQueryValue } from 'vue-router'

  import ErrorImg from '@/components/Common/Images/ErrorImg.vue'
  import { AUTH_USER_STORE, ROOT_STORE } from '@/store/constants'
  import type { IEquipmentError } from '@/types/equipments'
  import { useStore } from '@/use/useStore'

  const route = useRoute()
  const router = useRouter()
  const store = useStore()

  const errorMessages: ComputedRef<string | string[] | IEquipmentError | null> =
    computed(() => store.getters[ROOT_STORE.GETTERS.ERROR_MESSAGES])
  const token: ComputedRef<LocationQueryValue | LocationQueryValue[]> =
    computed(() => route.query.token)

  onBeforeMount(() => confirmAccount())

  function confirmAccount() {
    if (token.value) {
      store.dispatch(AUTH_USER_STORE.ACTIONS.CONFIRM_ACCOUNT, {
        token: token.value,
      })
    } else {
      router.push('/')
    }
  }

  onUnmounted(() => store.commit(ROOT_STORE.MUTATIONS.EMPTY_ERROR_MESSAGES))
</script>

<style lang="scss" scoped>
  @import '~@/scss/vars.scss';

  #account-confirmation {
    display: flex;
    flex-direction: column;
    align-items: center;

    svg {
      stroke: none;
      fill-rule: nonzero;
      fill: var(--app-color);
      filter: var(--svg-filter);
      width: 100px;
    }

    .error-message {
      font-size: 1.1em;
      text-align: center;
      display: flex;
      flex-direction: column;

      @media screen and (max-width: $medium-limit) {
        font-size: 1em;
      }
    }
  }
</style>
