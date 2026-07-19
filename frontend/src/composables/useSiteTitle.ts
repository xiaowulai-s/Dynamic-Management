import { ref } from 'vue'
import request from '@/api/request'

const siteTitleZh = ref('设备信息动态管理系统')
const siteTitleEn = ref('Equipment Management')
const loaded = ref(false)

export function useSiteTitle() {
  async function loadSiteTitle() {
    if (loaded.value) return
    try {
      // 使用公开接口 /api/settings/site-title（无需认证），避免登录页 401 死循环
      const res = await request.get('/settings/site-title')
      const data = res.data || res
      if (data.site_title_zh) siteTitleZh.value = data.site_title_zh
      if (data.site_title_en) siteTitleEn.value = data.site_title_en
      loaded.value = true
    } catch (e) {
      // 读取失败用默认值
      loaded.value = true
    }
  }

  function setSiteTitle(zh: string, en: string) {
    siteTitleZh.value = zh
    siteTitleEn.value = en
  }

  return { siteTitleZh, siteTitleEn, loadSiteTitle, setSiteTitle }
}
