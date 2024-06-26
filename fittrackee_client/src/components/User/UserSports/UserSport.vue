<template>
  <div id="user-sport" class="description-list" v-if="sport">
    <Modal
      v-if="displayModal"
      :title="$t('common.CONFIRMATION')"
      :message="
        $t(
          `user.PROFILE.SPORT.CONFIRM_SPORT_RESET${sport.default_equipments.length > 0 ? '_WITH_EQUIPMENTS' : ''}`
        )
      "
      @confirmAction="resetSport(sport.id, true)"
      @cancelAction="updateDisplayModal(false)"
      @keydown.esc="updateDisplayModal(false)"
    />
    <dl>
      <dt>{{ capitalize($t('workouts.SPORT', 1)) }}</dt>
      <dd>
        {{ sport.translatedLabel }}
      </dd>
      <dt>{{ capitalize($t('user.PROFILE.SPORT.COLOR')) }}</dt>
      <dd>
        <SportImage
          :title="sport.translatedLabel"
          :sport-label="sport.label"
          :color="sport.color ? sport.color : sportColors[sport.label]"
        />
      </dd>
      <dt>{{ capitalize($t('workouts.WORKOUT', 0)) }}</dt>
      <dd>
        <i
          :class="`fa fa-${
            authUser.sports_list.includes(sport.id) ? 'check-' : ''
          }square-o`"
          aria-hidden="true"
        />
      </dd>
      <dt>
        {{ capitalize($t('user.PROFILE.SPORT.STOPPED_SPEED_THRESHOLD')) }}
      </dt>
      <dd>
        <Distance
          :distance="sport.stopped_speed_threshold"
          unitFrom="km"
          :speed="true"
          :useImperialUnits="authUser.imperial_units"
        />
      </dd>
      <dt>{{ capitalize($t('common.ACTIVE', 0)) }}</dt>
      <dd>
        <i
          :class="`fa fa-${sport.is_active_for_user ? 'check-' : ''}square-o`"
          aria-hidden="true"
        />
      </dd>
      <dt>{{ $t('user.PROFILE.SPORT.DEFAULT_EQUIPMENTS', 1) }}</dt>
      <dd class="sport-equipments">
        <EquipmentBadge
          v-for="equipment in sport.default_equipments"
          :equipment="equipment"
          :sport-id="sport.id"
          :key="equipment.label"
        />
        <div class="no-equipments" v-if="sport.default_equipments.length === 0">
          {{ $t('equipments.NO_EQUIPMENTS') }}
        </div>
      </dd>
    </dl>
    <div class="sport-buttons">
      <button @click="$router.push(`/profile/edit/sports/${sport.id}`)">
        {{ $t('buttons.EDIT') }}
      </button>
      <button
        :disabled="loading"
        class="danger"
        @click.prevent="updateDisplayModal(true)"
      >
        {{ $t('buttons.RESET') }}
      </button>
      <button
        @click="
          $router.push(
            route.query.fromEquipmentId
              ? `/profile/equipments/${route.query.fromEquipmentId}`
              : '/profile/sports'
          )
        "
      >
        {{ $t('buttons.BACK') }}
      </button>
    </div>
  </div>
  <div v-else>
    <p class="no-sport">{{ $t('user.NO_SPORT_FOUND') }}</p>
    <button @click="$router.push('/profile/sports')">
      {{ $t('buttons.BACK') }}
    </button>
  </div>
</template>

<script setup lang="ts">
  import { capitalize, computed, onUnmounted, toRefs, watch } from 'vue'
  import type { ComputedRef } from 'vue'
  import { useRoute } from 'vue-router'

  import EquipmentBadge from '@/components/Common/EquipmentBadge.vue'
  import userSportComponent from '@/components/User/UserSports/userSportComponent'
  import { ROOT_STORE } from '@/store/constants'
  import type { ITranslatedSport } from '@/types/sports'
  import type { IAuthUserProfile } from '@/types/user'
  import { useStore } from '@/use/useStore'

  interface Props {
    authUser: IAuthUserProfile
    translatedSports: ITranslatedSport[]
  }
  const props = defineProps<Props>()

  const store = useStore()
  const route = useRoute()

  const { translatedSports } = toRefs(props)
  const {
    displayModal,
    errorMessages,
    loading,
    sportColors,
    resetSport,
    updateDisplayModal,
  } = userSportComponent()

  const sport: ComputedRef<ITranslatedSport | null> = computed(() =>
    getSport(translatedSports.value)
  )

  function getSport(sportsList: ITranslatedSport[]) {
    if (!route.params.id) {
      return null
    }
    const filteredSportList = sportsList.filter((sport) =>
      route.params.id ? sport.id === +route.params.id : null
    )
    if (filteredSportList.length === 0) {
      return null
    }
    return filteredSportList[0]
  }

  onUnmounted(() => {
    store.commit(ROOT_STORE.MUTATIONS.EMPTY_ERROR_MESSAGES)
  })
  watch(
    () => loading.value,
    (newIsLoading) => {
      if (!newIsLoading && !errorMessages.value) {
        updateDisplayModal(false)
      }
    }
  )
</script>

<style scoped lang="scss">
  @import '~@/scss/vars.scss';

  #user-sport {
    .sport-img {
      height: 35px;
      width: 35px;
      margin: 0;
    }
    .sport-equipments {
      display: flex;
      flex-wrap: wrap;
      padding: $default-padding * 0.5;
      gap: $default-padding;
    }
  }
  .sport-buttons {
    display: flex;
    flex-wrap: wrap;
    gap: $default-padding;
  }
  .no-equipments {
    font-style: italic;
  }
</style>
