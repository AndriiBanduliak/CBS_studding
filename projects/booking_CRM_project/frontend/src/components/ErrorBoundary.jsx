import React from 'react'
import { Result, Button } from 'antd'

export class ErrorBoundary extends React.Component {
  constructor(props) {
    super(props)
    this.state = { hasError: false }
  }
  static getDerivedStateFromError() { return { hasError: true } }
  componentDidCatch(error, info) { console.error('ErrorBoundary', error, info) }
  render() {
    if (this.state.hasError) {
      return (
        <Result status="error" title="Щось пішло не так">
          <Button type="primary" onClick={() => window.location.reload()}>Перезавантажити</Button>
        </Result>
      )
    }
    return this.props.children
  }
}

