import { createRouter, createWebHashHistory } from "vue-router";

import SettingsPage from "../pages/SettingsPage.vue";
import WorkspacePage from "../pages/WorkspacePage.vue";

export const router = createRouter({
  history: createWebHashHistory(),
  routes: [
    {
      path: "/",
      name: "workspace",
      component: WorkspacePage
    },
    {
      path: "/settings",
      name: "settings",
      component: SettingsPage
    }
  ]
});
