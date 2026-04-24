import { createApp } from 'vue'
import App from './App.vue'
import router from './router'
import { loadUser } from './store/auth'
import './style.css'

const app = createApp(App)
app.use(router)
app.mount('#app')

loadUser()
