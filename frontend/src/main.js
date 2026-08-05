import { createApp } from 'vue'
import { createPinia } from 'pinia'
import App from './App.vue'
import router from './app/router'

// Подключаем глобальные стили
import './app/styles/main.css'

const app = createApp(App)

app.use(createPinia())
app.use(router)

app.mount('#app')
