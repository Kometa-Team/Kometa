import { computed, onMounted, watch } from 'vue';
import { useUIStore } from '@/stores';
import type { Theme } from '@/types';

export function useTheme() {
  const ui = useUIStore();

  const theme = computed(() => ui.theme);
  const isDark = computed(() => ui.isDarkMode);

  const setTheme = (newTheme: Theme) => {
    ui.setTheme(newTheme);
  };

  const toggleTheme = () => {
    ui.toggleTheme();
  };

  const cycleTheme = () => {
    const themes: Theme[] = ['light', 'dark', 'system'];
    const currentIndex = themes.indexOf(ui.theme);
    const nextIndex = (currentIndex + 1) % themes.length;
    setTheme(themes[nextIndex]);
  };

  // Watch for system theme changes
  onMounted(() => {
    const mediaQuery = window.matchMedia('(prefers-color-scheme: dark)');

    const handleChange = () => {
      if (ui.theme === 'system') {
        // Re-apply system theme
        ui.setTheme('system');
      }
    };

    mediaQuery.addEventListener('change', handleChange);
  });

  return {
    theme,
    isDark,
    setTheme,
    toggleTheme,
    cycleTheme,
  };
}
