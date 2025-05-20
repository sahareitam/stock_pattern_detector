import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';

// הגדרה פשוטה ותקינה
export default defineConfig({
  plugins: [react()],
  // הסרנו את כל ההגדרות המורכבות שגורמות לשגיאה
})