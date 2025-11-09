import { useState } from 'react'
import { Tabs, Form, Input, Button, App as AntApp } from 'antd'
import { api } from '../api/client'
import { useAuth } from '../store/useAuth'
import { useNavigate } from 'react-router-dom'

export default function AuthPage() {
	const [loading, setLoading] = useState(false)
	const navigate = useNavigate()
    const { message } = AntApp.useApp()
    const { setUser } = useAuth()

	async function submit(path, values) {
		setLoading(true)
		try {
			await api.post(`/api/auth/${path}/`, values, { withCredentials: true })
			message.success('Готово')
			// сразу проставим пользователя в стор, чтобы PrivateRoute не редиректил
			setUser({ username: values.username })
			navigate('/')
		} catch (e) {
			message.error('Ошибка: ' + (e.response?.data?.detail || ''))
		} finally {
			setLoading(false)
		}
	}

	const loginForm = (
		<Form layout='vertical' onFinish={(v)=>submit('login', v)}>
			<Form.Item label='Логин' name='username' rules={[{ required: true }]}><Input/></Form.Item>
			<Form.Item label='Пароль' name='password' rules={[{ required: true }]}><Input.Password/></Form.Item>
			<Button type='primary' htmlType='submit' loading={loading} block>Войти</Button>
		</Form>
	)

	const registerForm = (
		<Form layout='vertical' onFinish={(v)=>submit('register', v)}>
			<Form.Item label='Логин' name='username' rules={[{ required: true }]}><Input/></Form.Item>
			<Form.Item label='Пароль' name='password' rules={[{ required: true, min: 4 }]}><Input.Password/></Form.Item>
			<Button type='primary' htmlType='submit' loading={loading} block>Зарегистрироваться</Button>
		</Form>
	)

	const items = [
		{ key: 'login', label: 'Вход', children: loginForm },
		{ key: 'register', label: 'Регистрация', children: registerForm },
	]

	return (
		<div style={{ maxWidth: 360, margin: '64px auto' }}>
			<Tabs items={items} />
		</div>
	)
}
