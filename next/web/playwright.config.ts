import { defineConfig } from '@playwright/test'
export default defineConfig({ testDir: './tests', workers: 1, use: { baseURL: 'http://127.0.0.1:5174', launchOptions: { executablePath: process.env.CHROMIUM_PATH, args: ['--no-sandbox'] } }, webServer: { command: 'npm run dev', url: 'http://127.0.0.1:5174', reuseExistingServer: false } })
