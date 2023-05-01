import { GetterTree } from 'vuex'

import { NOTIFICATIONS_STORE } from '@/store/constants'
import {
  INotificationsGetters,
  INotificationsState,
} from '@/store/modules/notifications/types'
import { IRootState } from '@/store/modules/root/types'

export const getters: GetterTree<INotificationsState, IRootState> &
  INotificationsGetters = {
  [NOTIFICATIONS_STORE.GETTERS.UNREAD_STATUS]: (state: INotificationsState) => {
    return state.unread
  },
}