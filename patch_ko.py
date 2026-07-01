import re

def patch_lang_enum():
    path = "src/constant/index.ts"
    with open(path, encoding="utf-8") as f:
        content = f.read()

    if "KO_KR" not in content:
        content = content.replace(
            "RU_RU = 'ru-RU',",
            "RU_RU = 'ru-RU',\n  KO_KR = 'ko-KR',",
        )

    for line in ["ZH_CN = 'zh-CN',", "ZH_TW = 'zh-TW',", "RU_RU = 'ru-RU',"]:
        content = content.replace(line + "\n", "")

    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
    print("patched LANG enum")


def patch_i18n_index():
    path = "src/i18n/index.ts"
    with open(path, encoding="utf-8") as f:
        content = f.read()

    if "from './ko'" not in content:
        content = content.replace(
            "import zhTW from './zh-tw'",
            "import zhTW from './zh-tw'\nimport ko from './ko'",
        )
        content = content.replace(
            "[LANG.RU_RU]: ru,",
            "[LANG.RU_RU]: ru,\n    [LANG.KO_KR]: ko,",
        )

    for line in [
        "import zh from './zh'\n",
        "import zhTW from './zh-tw'\n",
        "import ru from './ru'\n",
        "[LANG.ZH_CN]: zh,\n",
        "[LANG.ZH_TW]: zhTW,\n",
        "[LANG.RU_RU]: ru,\n",
    ]:
        content = content.replace(line, "")

    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
    print("patched i18n index")


def patch_language_select():
    path = "src/components/settings/general/LanguageSelect.vue"
    with open(path, encoding="utf-8") as f:
        content = f.read()

    if "KO_KR" not in content:
        content = content.replace(
            "[LANG.RU_RU]: 'Русский',",
            "[LANG.RU_RU]: 'Русский',\n  [LANG.KO_KR]: '한국어',",
        )

    for line in [
        "[LANG.ZH_CN]: '简体中文',\n",
        "[LANG.ZH_TW]: '繁體中文',\n",
        "[LANG.RU_RU]: 'Русский',\n",
    ]:
        content = content.replace(line, "")

    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
    print("patched LanguageSelect.vue")


def remove_dashboard_upgrade_menu():
    path = "src/components/settings/general/GeneralSettings.vue"
    with open(path, encoding="utf-8") as f:
        content = f.read()

    markers = ["upgradeDashboard", "autoUpgradeDashboard"]
    pattern = re.compile(r"<SettingItem\b.*?</SettingItem>", re.DOTALL)

    def should_remove(block):
        return any(m in block for m in markers)

    content = pattern.sub(
        lambda m: "" if should_remove(m.group(0)) else m.group(0), content
    )

    # --- 더 이상 쓰이지 않게 된 script 쪽 선언 정리 ---
    content = content.replace("import { isSingboxBackend } from '@/assembly/backend'\n", "")
    content = content.replace(
        "import { isSingBoxCore, upgradeUIAPI } from '@/assembly/version'",
        "import { isSingBoxCore } from '@/assembly/version'",
    )
    content = content.replace("import { handlerUpgradeSuccess } from '@/helper'\n", "")
    content = content.replace("import { twMerge } from 'tailwind-merge'\n", "")
    content = content.replace("  autoUpgradeDashboard,\n", "")

    func_pattern = re.compile(
        r"const isUIUpgrading = ref\(false\)\n"
        r"const handlerClickUpgradeUI = async \(\) => \{.*?\n\}\n",
        re.DOTALL,
    )
    content = func_pattern.sub("", content)

        # ref가 더 이상 쓰이지 않으면 import에서도 제거
    if "ref(" not in content:
        content = content.replace(
            "import { computed, ref } from 'vue'",
            "import { computed } from 'vue'",
        )
        
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
    print("removed dashboard upgrade menu items + cleaned up unused script code")

def patch_update_check_url():
    path = "src/assembly/version.ts"
    with open(path, encoding="utf-8") as f:
        content = f.read()

    content = content.replace(
        "https://api.github.com/repos/Zephyruso/zashboard/releases/latest",
        "https://api.github.com/repos/hckwon767/dashboard-ko/releases/latest",
    )

    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
    print("patched update-check URL to use new repo")
    
def customize_version_display():
    path = "src/components/settings/general/ZashboardSettings.vue"
    with open(path, encoding="utf-8") as f:
        content = f.read()

    pattern = re.compile(
        r'<a\s+href="https://github\.com/Zephyruso/zashboard"[^>]*>.*?</a>',
        re.DOTALL,
    )

    new_block = '''<a
          href="https://github.com/hckwon767/dashboard-ko"
          target="_blank"
          class="text-lg font-semibold"
        >
          대시보드
          <span class="text-sm font-normal opacity-50">
            {{ zashboardVersion }}
          </span>
        </a>'''

    content, count = pattern.subn(new_block, content)

    if count > 0:
        print(f"patched version display ({count} match)")
    else:
        print("WARNING: version display block not found, skipping")

    content = re.sub(r"\nconst commitId = __COMMIT_ID__\n", "\n", content)

    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
        
def patch_latency_targets():
    # 1) src/api/latency.ts: cloudflare -> naver, github -> google
    path = "src/api/latency.ts"
    with open(path, encoding="utf-8") as f:
        content = f.read()

    content = content.replace(
        """export const getCloudflareLatencyAPI = () => {
  return getLatencyFromUrlAPI('https://www.cloudflare.com/favicon.ico')
}""",
        """export const getNaverLatencyAPI = () => {
  return getLatencyFromUrlAPI('https://www.naver.com/favicon.ico')
}""",
    )
    content = content.replace(
        """export const getGithubLatencyAPI = () => {
  return getLatencyFromUrlAPI('https://github.githubassets.com/favicon.ico')
}""",
        """export const getGoogleLatencyAPI = () => {
  return getLatencyFromUrlAPI('https://www.google.com/favicon.ico')
}""",
    )

    with open(path, "w", encoding="utf-8") as f:
        f.write(content)

    # 2) src/composables/overview.ts: ref 이름 변경
    path = "src/composables/overview.ts"
    with open(path, encoding="utf-8") as f:
        content = f.read()

    content = content.replace(
        "export const githubLatency = ref<number[]>([])",
        "export const googleLatency = ref<number[]>([])",
    )
    content = content.replace(
        "export const cloudflareLatency = ref<number[]>([])",
        "export const naverLatency = ref<number[]>([])",
    )

    with open(path, "w", encoding="utf-8") as f:
        f.write(content)

    # 3) ConnectionStatus.vue: import 및 targets 배열 변경
    path = "src/components/overview/ConnectionStatus.vue"
    with open(path, encoding="utf-8") as f:
        content = f.read()

    content = content.replace(
        """import {
  getBaiduLatencyAPI,
  getCloudflareLatencyAPI,
  getGithubLatencyAPI,
  getYouTubeLatencyAPI,
} from '@/api/latency'
import {
  baiduLatency,
  cloudflareLatency,
  githubLatency,
  youtubeLatency,
} from '@/composables/overview'""",
        """import {
  getBaiduLatencyAPI,
  getGoogleLatencyAPI,
  getNaverLatencyAPI,
  getYouTubeLatencyAPI,
} from '@/api/latency'
import {
  baiduLatency,
  googleLatency,
  naverLatency,
  youtubeLatency,
} from '@/composables/overview'""",
    )

    content = content.replace(
        """const targets = [
  { name: 'Baidu', ref: baiduLatency, api: getBaiduLatencyAPI },
  { name: 'Cloudflare', ref: cloudflareLatency, api: getCloudflareLatencyAPI },
  { name: 'GitHub', ref: githubLatency, api: getGithubLatencyAPI },
  { name: 'YouTube', ref: youtubeLatency, api: getYouTubeLatencyAPI },
]""",
        """const targets = [
  { name: 'Baidu', ref: baiduLatency, api: getBaiduLatencyAPI },
  { name: 'Naver', ref: naverLatency, api: getNaverLatencyAPI },
  { name: 'Google', ref: googleLatency, api: getGoogleLatencyAPI },
  { name: 'YouTube', ref: youtubeLatency, api: getYouTubeLatencyAPI },
]""",
    )

    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
    print("patched latency targets (Baidu/Naver/Google/YouTube)")

def patch_dayjs_locale():
    path = "src/helper/dayjs.ts"
    with open(path, encoding="utf-8") as f:
        content = f.read()

    if "dayjs/locale/ko" not in content:
        content = content.replace(
            "import 'dayjs/locale/ru'",
            "import 'dayjs/locale/ko'\nimport 'dayjs/locale/ru'",
        )
        print("patched dayjs locale (added ko)")
    else:
        print("dayjs ko locale already present")

    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
        
if __name__ == "__main__":
    patch_lang_enum()
    patch_i18n_index()
    patch_language_select()
    #remove_dashboard_upgrade_menu()
    patch_update_check_url()
    customize_version_display()
    patch_latency_targets()
    patch_dayjs_locale()
