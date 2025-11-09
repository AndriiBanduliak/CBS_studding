import axios from 'axios'

const baseURL = import.meta.env.VITE_API_BASE || ''

export const api = axios.create({
	baseURL,
	headers: { 'Content-Type': 'application/json' },
})

api.defaults.withCredentials = true

function getCookie(name) {
	const match = document.cookie.match(new RegExp('(^|; )' + name + '=([^;]+)'))
	return match ? decodeURIComponent(match[2]) : null
}

api.interceptors.request.use((config) => {
	const method = (config.method || 'get').toLowerCase()
	if ([ 'post', 'put', 'patch', 'delete' ].includes(method)) {
		const token = getCookie('csrftoken')
		if (token) config.headers['X-CSRFToken'] = token
	}
	return config
})

export async function ensureCsrfCookie() {
	try { await api.get('/api/auth/csrf/') } catch {}
}
